# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 11:33:22 2020

@author: luol2
"""
import argparse
from nn_model import bioTag_CNN,bioTag_BERT
from dic_ner import dic_ont
from evaluate import GSCplus_corpus,JAX_corpus
from tagging_text import bioTag
import os
import time
import json
import tensorflow as tf

'''
config = tf.ConfigProto()  
config.gpu_options.allow_growth = True  
session = tf.Session(config=config) 
'''
def run_gsc_test(files,biotag_dic,nn_model):
    

    fin_test=open(files['testfile'],'r',encoding='utf-8')
    all_test=fin_test.read().strip().split('\n\n')
    fin_test.close()
    test_out=open(files['outfile'],'w',encoding='utf-8')
    #i=0
    for doc_test in all_test:
        #i+=1
        #print(i)
        lines=doc_test.split('\n')
        pmid = lines[0]
        test_result=bioTag(lines[1],biotag_dic,nn_model,onlyLongest=False,abbrRecog=False,Threshold=0.95)
        test_out.write(pmid+'\n'+lines[1]+'\n')
        for ele in test_result:
            test_out.write(ele[0]+'\t'+ele[1]+'\t'+lines[1][int(ele[0]):int(ele[1])]+'\t'+ele[2]+'\t'+ele[3]+'\n')
        test_out.write('\n')
    test_out.close()
    GSCplus_corpus(files['outfile'],files['testfile'],subtree=True)

def run_jax_test(files,biotag_dic,nn_model):
    inpath=files['testfile']
    test_out=open(files['outfile'],'w',encoding='utf-8')
    i=0
    preds_result={}
    for file in os.listdir(inpath):
        i+=1
        print(i)
        pmid=file[:-4]
        temp_result=[]
        fin=open(inpath+file,'r',encoding='utf-8')
        intext=fin.read().rstrip()
        fin.close()     
        test_result=bioTag(intext,biotag_dic,nn_model,onlyLongest=False,abbrRecog=True,Threshold=0.95)
        for ele in test_result:
            if ele not in temp_result:
                temp_result.append(ele)
        preds_result[pmid]=temp_result
    json.dump(preds_result, test_out ,indent=2)
    test_out.close()
    JAX_corpus(files['outfile'], files['goldfile'])


if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='build weak training corpus, python build_dict.py -i infile -o outpath')
    parser.add_argument('--modeltype', '-m', help="the model type (cnn or biobert or bioformer?)",default='biobert')
    parser.add_argument('--corpus', '-c', help="HPO corpus (gsc or jax?)",default='jax')
    parser.add_argument('--output', '-o', help="the output prediction file ",default='../results/gsc_bioformer_new1.tsv')
    
    args = parser.parse_args()
    model_type=args.modeltype
    test_set=args.corpus

    
    
    ontfiles={'dic_file':'../dict/noabb_lemma.dic',
              'word_hpo_file':'../dict/word_id_map.json',
              'hpo_word_file':'../dict/id_word_map.json'}
    biotag_dic=dic_ont(ontfiles)
    
    if model_type=='cnn':
        vocabfiles={'w2vfile':'../models_v1.1/bio_embedding_intrinsic.d200',   
                    'charfile':'../dict/char.vocab',
                    'labelfile':'../dict/lable.vocab',
                    'posfile':'../dict/pos.vocab'}

        modelfile='../models_v1.1/cnn_hpo_v1.1.h5'
        nn_model=bioTag_CNN(vocabfiles)
        nn_model.load_model(modelfile)
        
    elif model_type=='biobert':
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'config_path':'../models_v1.1/biobert_v11_pubmed/bert_config.json',
                    'checkpoint_path':'../models_v1.1/biobert_v11_pubmed/model.ckpt-1000000',
                    'vocab_path':'../models_v1.1/biobert_v11_pubmed/vocab.txt'}
        modelfile='../models_v1.1/biobert_hpo_v1.1.h5'
        nn_model=bioTag_BERT(vocabfiles)
        nn_model.load_model(modelfile)
    else:
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'config_path':'../models_v1.1/bioformer-cased-v1.0/bert_config.json',
                    'checkpoint_path':'../models_v1.1/bioformer-cased-v1.0/bioformer-cased-v1.0-model.ckpt-2000000',
                    'vocab_path':'../models_v1.1/bioformer-cased-v1.0/vocab.txt'}
        modelfile='../models_v1.1/bioformer_hpo_v1.1.h5'
        nn_model=bioTag_BERT(vocabfiles)
        nn_model.load_model(modelfile)
    
    if test_set=='gsc':
        files={'testfile':'../data/corpus/GSC/GSCplus_test_gold.tsv',
               'outfile':'../results/gsc_test_bioformer_p5n5.tsv'}
        files['outfile']=args.output
        start_time=time.time()
        run_gsc_test(files,biotag_dic,nn_model)
        print('gsc done:',time.time()-start_time)
    else:
        files={'testfile':'../data/corpus/JAX/txt/',
               'goldfile':'../data/corpus/JAX/JAX_gold.json',
               'outfile':'../results/jax_test_bert_p5n5.json'}
        start_time=time.time()
        files['outfile']=args.output
        run_jax_test(files,biotag_dic,nn_model)
        print('jax done:',time.time()-start_time)
