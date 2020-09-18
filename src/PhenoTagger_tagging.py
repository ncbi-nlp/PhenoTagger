# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 09:20:38 2020

@author: luol2
"""


import argparse
from nn_model import bioTag_CNN,bioTag_BERT
from dic_ner import dic_ont
from tagging_text import bioTag,bioTag_dic,bioTag_ml
import os
import time
import json
import tensorflow as tf
config = tf.ConfigProto()  
config.gpu_options.allow_growth = True  
session = tf.Session(config=config) 

def file_tag_hybrid(infile,outfile,biotag_dic,nn_model,para_set):
    

    fin=open(infile,'r',encoding='utf-8')
    all_context=fin.read().strip().split('\n')
    fin.close()
    fout=open(outfile,'w',encoding='utf-8')
    preds_result={} # {pmid:[[sid,eid,concept text,concept id,score],...]}
    for doc in all_context:
        segs=doc.split('\t')
        pmid = segs[0]
        intext=segs[1]
        tag_result=bioTag(intext,biotag_dic,nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold'])
        temp_result=[]
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def path_tag_hybrid(inpath,outfile,biotag_dic,nn_model,para_set):

    fout=open(outfile,'w',encoding='utf-8')
    i=0
    N=0
    preds_result={}
    for filename in os.listdir(inpath):
        N+=1
    for filename in os.listdir(inpath):
        i+=1
        print("Processing:{0}%".format(round((i + 1) * 100 / N)), end="\r")
        pmid=filename 
        fin=open(inpath+filename,'r',encoding='utf-8')
        intext=fin.read().rstrip()
        fin.close()   
        temp_result=[]
        tag_result=bioTag(intext,biotag_dic,nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold'])
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def file_tag_dl(infile,outfile,nn_model,para_set):
    

    fin=open(infile,'r',encoding='utf-8')
    all_context=fin.read().strip().split('\n')
    fin.close()
    fout=open(outfile,'w',encoding='utf-8')
    preds_result={} # {pmid:[[sid,eid,concept text,concept id,score],...]}
    for doc in all_context:
        segs=doc.split('\t')
        pmid = segs[0]
        intext=segs[1]
        tag_result=bioTag_ml(intext,ml_model=nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold'])
        temp_result=[]
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def path_tag_dl(inpath,outfile,nn_model,para_set):

    fout=open(outfile,'w',encoding='utf-8')
    i=0
    N=0
    preds_result={}
    for filename in os.listdir(inpath):
        N+=1
    for filename in os.listdir(inpath):
        i+=1
        print("Processing:{0}%".format(round((i + 1) * 100 / N)), end="\r")
        pmid=filename 
        fin=open(inpath+filename,'r',encoding='utf-8')
        intext=fin.read().rstrip()
        fin.close()   
        temp_result=[]
        tag_result=bioTag_ml(intext,nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold'])
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def file_tag_dict(infile,outfile,biotag_dic,para_set):
    

    fin=open(infile,'r',encoding='utf-8')
    all_context=fin.read().strip().split('\n')
    fin.close()
    fout=open(outfile,'w',encoding='utf-8')
    preds_result={} # {pmid:[[sid,eid,concept text,concept id,score],...]}
    for doc in all_context:
        segs=doc.split('\t')
        pmid = segs[0]
        intext=segs[1]
        tag_result=bioTag_dic(intext,biotag_dic,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'])
        temp_result=[]
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def path_tag_dict(inpath,outfile,biotag_dic,para_set):

    fout=open(outfile,'w',encoding='utf-8')
    i=0
    N=0
    preds_result={}
    for filename in os.listdir(inpath):
        N+=1
    for filename in os.listdir(inpath):
        i+=1
        print("Processing:{0}%".format(round((i + 1) * 100 / N)), end="\r")
        pmid=filename 
        fin=open(inpath+filename,'r',encoding='utf-8')
        intext=fin.read().rstrip()
        fin.close()   
        temp_result=[]
        tag_result=bioTag_dic(intext,biotag_dic,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'])
        for ele in tag_result:
            temp_result.append([ele[0],ele[1],intext[int(ele[0]):int(ele[1])],ele[2],ele[3]])
        preds_result[pmid]=temp_result
    json.dump(preds_result, fout ,indent=2)
    fout.close()

def phecr_tag(infile,para_set,outfile):
    
    ontfiles={'dic_file':'../dict/noabb_lemma.dic',
              'word_hpo_file':'../dict/word_id_map.json',
              'hpo_word_file':'../dict/id_word_map.json'}
    
    if para_set['model_type']=='cnn':
        vocabfiles={'w2vfile':'../data/vocab/bio_embedding_intrinsic.d200',   
                    'charfile':'../data/vocab/char.vocab',
                    'labelfile':'../dict/lable.vocab',
                    'posfile':'../data/vocab/pos.vocab'}
        modelfile='../models/cnn_hpo.h5'
    else:
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'config_path':'/data/vocab/biobert_v11_pubmed/bert_config.json',
                    'checkpoint_path':'/data/vocab/biobert_v11_pubmed/model.ckpt-1000000',
                    'vocab_path':'/data/vocab/biobert_v11_pubmed/vocab.txt'}
        modelfile='../models/biobert_hpo.h5'
    
    if para_set['tagger']=='hybrid':
        biotag_dic=dic_ont(ontfiles)    

        if para_set['model_type']=='cnn':
            nn_model=bioTag_CNN(vocabfiles)
            nn_model.load_model(modelfile)
        else:
            nn_model=bioTag_BERT(vocabfiles)
            nn_model.load_model(modelfile)
        
        if os.path.isdir(infile):
            print("it's a directory")
            start_time=time.time()
            path_tag_hybrid(infile,outfile,biotag_dic,nn_model,para_set)
            print('tag done:',time.time()-start_time)
        elif os.path.isfile(infile):
            print("it's a normal file")
            start_time=time.time()
            file_tag_hybrid(infile,outfile,biotag_dic,nn_model,para_set)
            print('tag done:',time.time()-start_time)
    
    elif para_set['tagger']=='dl':   

        if para_set['model_type']=='cnn':
            nn_model=bioTag_CNN(vocabfiles)
            nn_model.load_model(modelfile)
        else:
            nn_model=bioTag_BERT(vocabfiles)
            nn_model.load_model(modelfile)   
        
        if os.path.isdir(infile):
            print("it's a directory")
            start_time=time.time()
            path_tag_dl(infile,outfile,nn_model,para_set)
            print('tag done:',time.time()-start_time)
        elif os.path.isfile(infile):
            print("it's a normal file")
            start_time=time.time()
            file_tag_dl(infile,outfile,nn_model,para_set)
            print('tag done:',time.time()-start_time)

    elif para_set['tagger']=='dict':
        biotag_dic=dic_ont(ontfiles)    
    
        if os.path.isdir(infile):
            print("it's a directory")
            start_time=time.time()
            path_tag_dict(infile,outfile,biotag_dic,para_set)
            print('tag done:',time.time()-start_time)
        elif os.path.isfile(infile):
            print("it's a normal file")
            start_time=time.time()
            file_tag_dict(infile,outfile,biotag_dic,para_set)
            print('tag done:',time.time()-start_time)

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='build weak training corpus, python build_dict.py -i infile -o outpath')
    parser.add_argument('--infile', '-i', help="input the ontology dictionary path or file",default='none')
    parser.add_argument('--outfile', '-o', help="the output path of weak corpus",default='//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/')
    args = parser.parse_args()

    para_set={'tagger':'dict', # hybrid, dl, or dict
              'model_type':'cnn', # cnn or biobert
              'onlyLongest':False, # False: return overlap concepts, True only longgest
              'abbrRecog':False,# False: don't identify abbr, True: identify abbr
              'ML_Threshold':0.95,# the Threshold of deep learning model
              }
    
    
    phecr_tag(args.infile,para_set,args.outfile)
