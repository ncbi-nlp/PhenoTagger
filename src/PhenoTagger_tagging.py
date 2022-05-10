# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 09:20:38 2020

@author: luol2
"""


import argparse
from nn_model import bioTag_CNN,bioTag_BERT
from dic_ner import dic_ont
from tagging_text import bioTag
import os
import time
import json
import re
import bioc



def PubTator_Converter(infile,outfile,biotag_dic,nn_model,para_set):

    with open(infile, 'r',encoding='utf-8') as fin:
        with open(outfile,'w', encoding='utf8') as fout:
            title=''
            abstract=''
            for line in fin:
                line = line.rstrip()
                p_title = re.compile('^([0-9]+)\|t\|(.*)$')
                p_abstract = re.compile('^([0-9]+)\|a\|(.*)$')
                if p_title.search(line):  # title
                    m = p_title.match(line)
                    pmid = m.group(1)
                    title = m.group(2)
                    fout.write(pmid+"|t|"+title+"\n")
                elif p_abstract.search(line):  # abstract
                    m = p_abstract.match(line)
                    pmid = m.group(1)
                    abstract = m.group(2)
                    fout.write(pmid+"|a|"+abstract+"\n")
                else:  # annotation
                    intext=title+' '+abstract
                    #print('..........',pmid)
                    #print(intext)
                    tag_result=bioTag(intext,biotag_dic,nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold'])
                    for ele in tag_result:
                        start = ele[0]
                        last = ele[1]
                        mention = intext[int(ele[0]):int(ele[1])]
                        type='Phenotype'
                        id=ele[2]
                        score=ele[3]
                        fout.write(pmid+"\t"+start+"\t"+last+"\t"+mention+"\t"+type+"\t"+id+"\t"+score+"\n")
                    fout.write('\n')
                    title=''
                    abstract=''

def BioC_Converter(infile,outfile,biotag_dic,nn_model,para_set):

    with open(infile, 'r',encoding='utf-8') as fin:
        with open(outfile,'w', encoding='utf8') as fout:
            collection = bioc.load(fin)
            for document in collection.documents:
                mention_num=0
                for passage in document.passages:
                    passage_offset=passage.offset
                    tag_result=bioTag(passage.text,biotag_dic,nn_model,onlyLongest=para_set['onlyLongest'], abbrRecog=para_set['abbrRecog'],Threshold=para_set['ML_Threshold']) 
                    for ele in tag_result:
                        bioc_note = bioc.BioCAnnotation()
                        bioc_note.id = str(mention_num)
                        mention_num+=1
                        bioc_note.infons['identifier'] = ele[2]
                        bioc_note.infons['type'] = "Phenotype"
                        bioc_note.infons['score'] = ele[3]
                        start = int(ele[0])
                        last = int(ele[1])
                        loc = bioc.BioCLocation(offset=str(passage_offset+start), length= str(last-start))
                        bioc_note.locations.append(loc)
                        bioc_note.text = passage.text[start:last]
                        passage.annotations.append(bioc_note)
            bioc.dump(collection, fout, pretty_print=True)

def phenotagger_tag(infolder,para_set,outfolder):
    
    ontfiles={'dic_file':'../dict/noabb_lemma.dic',
              'word_hpo_file':'../dict/word_id_map.json',
              'hpo_word_file':'../dict/id_word_map.json'}
    
    if para_set['model_type']=='cnn':
        vocabfiles={'w2vfile':'../models_v1.1/bio_embedding_intrinsic.d200',   
                    'charfile':'../dict/char.vocab',
                    'labelfile':'../dict/lable.vocab',
                    'posfile':'../dict/pos.vocab'}
        modelfile='../models_v1.1/cnn_hpo_v1.1.h5'
    elif para_set['model_type']=='bioformer':
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'config_path':'../models_v1.1/bioformer-cased-v1.0/bert_config.json',
                    'checkpoint_path':'../models_v1.1/bioformer-cased-v1.0/bioformer-cased-v1.0-model.ckpt-2000000',
                    'vocab_path':'../models_v1.1/bioformer-cased-v1.0/vocab.txt'}
        modelfile='../models_v1.1/bioformer_hpo_v1.1.h5'
    else:
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'config_path':'../models_v1.1/biobert_v11_pubmed/bert_config.json',
                    'checkpoint_path':'../models_v1.1/biobert_v11_pubmed/model.ckpt-1000000',
                    'vocab_path':'../models_v1.1/biobert_v11_pubmed/vocab.txt'}
        modelfile='../models_v1.1/biobert_hpo_v1.1.h5'
    
    # loading dict and model
        
    biotag_dic=dic_ont(ontfiles)    

    if para_set['model_type']=='cnn':
        nn_model=bioTag_CNN(vocabfiles)
        nn_model.load_model(modelfile)
    else:
        nn_model=bioTag_BERT(vocabfiles)
        nn_model.load_model(modelfile)

    #tagging text
    print("begin tagging........")
    start_time=time.time()
    
    i=0
    N=0
    for filename in os.listdir(infolder):
        N+=1
    for filename in os.listdir(infolder):
        print("Processing:{0}%".format(round(i * 100 / N)), end="\r")
        i+=1
                
        with open(infolder+filename, 'r',encoding='utf-8') as fin:
            format=""
            for line in fin:
                pattern_bioc = re.compile('.*<collection>.*')
                pattern_pubtator = re.compile('^([^\|]+)\|[^\|]+\|(.*)')
                if pattern_pubtator.search(line):
                    format="PubTator"
                    break
                elif pattern_bioc.search(line):
                    format="BioC"
                    break
            if(format == "PubTator"):
                PubTator_Converter(infolder+filename,outfolder+filename,biotag_dic,nn_model,para_set)
            elif(format == "BioC"):
                BioC_Converter(infolder+filename,outfolder+filename,biotag_dic,nn_model,para_set)    

    
    print('tag done:',time.time()-start_time)




if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='build weak training corpus, python build_dict.py -i infile -o outpath')
    parser.add_argument('--infolder', '-i', help="input folder path",default='../example/input/')
    parser.add_argument('--outfolder', '-o', help="output folder path",default='../example/output/')
   
    args = parser.parse_args()
    
    if not os.path.exists(args.outfolder):
        os.makedirs(args.outfolder)

    para_set={
              'model_type':'bioformer', # cnn, bioformer, or biobert
              'onlyLongest':False, # False: return overlap concepts, True only longgest
              'abbrRecog':True,# False: don't identify abbr, True: identify abbr
              'ML_Threshold':0.95,# the Threshold of deep learning model
              }
    
    
    phenotagger_tag(args.infolder,para_set,args.outfolder)
    print('The results are in ',args.outfolder)
