# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 10:14:27 2020

@author: luol2
"""

import argparse
from nn_model import bioTag_CNN,bioTag_BERT
from tensorflow.keras.optimizers import RMSprop, SGD, Adam, AdamW, Adadelta, Adagrad,Nadam
from ml_ner import ml_intext
from dic_ner import dic_ont
from tagging_text import bioTag
from evaluate import general_corpus
import sys
import os
import time
import tensorflow as tf


gpu = tf.config.list_physical_devices('GPU')
print("Num GPUs Available: ", len(gpu))
if len(gpu) > 0:
    tf.config.experimental.set_memory_growth(gpu[0], True)

def run_dev(files,biotag_dic,nn_model):
    
    fin_dev=open(files['devfile'],'r',encoding='utf-8')
    all_dev=fin_dev.read().strip().split('\n\n')
    fin_dev.close()
    dev_out=open(files['devout'],'w',encoding='utf-8')
    for doc_dev in all_dev:
        lines=doc_dev.split('\n')
        pmid = lines[0]
        dev_result=bioTag(lines[1],biotag_dic,nn_model,None,Threshold=0.95)
        dev_out.write(pmid+'\n'+lines[1]+'\n')
        for ele in dev_result:
            dev_out.write(ele[0]+'\t'+ele[1]+'\t'+lines[1][int(ele[0]):int(ele[1])]+'\t'+ele[2]+'\t'+ele[3]+'\n')
        dev_out.write('\n')
    dev_out.close()
    ave_f=general_corpus(files['devout'],files['devfile'])
    return ave_f

def CNN_training(trainfiles,vocabfiles,modelfile,EPOCH=150):
    
    cnn_model=bioTag_CNN(vocabfiles)

    #load dataset
    trainfile=trainfiles['trainfile']
    train_set,train_label = ml_intext(trainfile)

    train_x, train_y = cnn_model.rep.represent_instances_all_feas(train_set,train_label,word_max_len=cnn_model.hyper['sen_max'],char_max_len=cnn_model.hyper['word_max'],training=True)
    input_train = []

    if cnn_model.fea_dict['word'] == 1:
        input_train.append(train_x[0])

    if cnn_model.fea_dict['char'] == 1:
        input_train.append(train_x[1])

    if cnn_model.fea_dict['lemma'] == 1:
        input_train.append(train_x[2])

    if cnn_model.fea_dict['pos'] == 1:
        input_train.append(train_x[3])

    #opt = Adadelta()
    #opt = AdamW(learning_rate=5e-5,weight_decay=0.01,epsilon=1e-6,global_clipnorm=1.0 ) 
    #opt = Adam(lr=0.00001) 
    opt = RMSprop(lr=0.0001, rho=0.9, epsilon=1e-06)
    #cnn_model.model.compile(loss='categorical_crossentropy', optimizer=opt,metrics=['categorical_accuracy'])
    cnn_model.model.compile(optimizer=opt,loss='sparse_categorical_crossentropy',metrics=['accuracy'])
    cnn_model.model.summary()
    #cnn_model.load_model(modelfile)
    ontfiles={'dic_file':'../dict/noabb_lemma.dic',
              'word_hpo_file':'../dict/word_id_map.json',
              'hpo_word_file':'../dict/id_word_map.json'}
    biotag_dic=dic_ont(ontfiles)
    
    max_dev=0.0
    max_dev_epoch=0
    Dev_ES=True   #early stop using dev set
    if trainfiles['devfile']=='none':
        Dev_ES=False
    for i in range(EPOCH):
        print('\nepoch:',i)
        cnn_model.model.fit(input_train,train_y,batch_size=128, epochs=1,verbose=2)
        if i<40:   # after 10 epoch, begin dev evaluation
            continue
        #evaluation dev
        if Dev_ES==True:
            print('............dev evaluation..........')
            dev_ave_f=run_dev(trainfiles,biotag_dic,cnn_model)
            if dev_ave_f >max_dev:
                if dev_ave_f > max_dev:
                    max_dev=dev_ave_f
                    max_dev_epoch=i
                    cnn_model.model.save_weights(modelfile)
                print('max_dev_f=',max_dev/2,'epoch:',max_dev_epoch)
    if Dev_ES==False:
        cnn_model.model.save_weights(modelfile)
        print('The model has saved.')
            

def BERT_training(trainfiles,vocabfiles,modelfile,EPOCH=100):
    
    bert_model=bioTag_BERT(vocabfiles)

  
    trainfile=trainfiles['trainfile']

    train_set,train_label = ml_intext(trainfile)

    train_x,train_y=bert_model.rep.load_data(train_set,train_label,word_max_len=bert_model.maxlen,training=True)
    
    bert_model.model.compile(optimizer=Adam(5e-6),loss='sparse_categorical_crossentropy',metrics=['accuracy'])

    bert_model.model.summary()
    
    ontfiles={'dic_file':'../dict/noabb_lemma.dic',
              'word_hpo_file':'../dict/word_id_map.json',
              'hpo_word_file':'../dict/id_word_map.json'}
    biotag_dic=dic_ont(ontfiles)
    
    max_dev=0.0
    max_dev_epoch=0
    Dev_ES=True   #early stop using dev set
    if trainfiles['devfile']=='none':
        Dev_ES=False

    for i in range(EPOCH):
        print('epoch:',i)
        bert_model.model.fit(train_x,train_y,batch_size=64, epochs=1,verbose=2)
        if i<30:   # after 5 epoch, begin dev evaluation
            continue
        #evaluation dev
        if Dev_ES==True:
            print('............dev evaluation..........')
            dev_ave_f=run_dev(trainfiles,biotag_dic,bert_model)
            if dev_ave_f >max_dev or i%1==0:
                if dev_ave_f > max_dev:
                    max_dev=dev_ave_f
                    max_dev_epoch=i
                    bert_model.model.save_weights(modelfile)
                    print('max_dev_f=',max_dev/2,'epoch:',max_dev_epoch)
                
    if Dev_ES==False:
        bert_model.model.save_weights(modelfile)
        print('The model has saved.')
        
if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='train PhenoTagger, python PhenoTagger_training.py -t trainfile -d devfile -m modeltype -o outpath')
    parser.add_argument('--trainfile', '-t', help="the training file",default='../data/distant_train_data/distant_train.conll')
    parser.add_argument('--devfile', '-d', help="the development set file",default='none')
    parser.add_argument('--modeltype', '-m', help="deep learning model (cnn, bioformer or biobert?)",default='bioformer')
    parser.add_argument('--output', '-o', help="the model output folder",default='../newmodels/')
    args = parser.parse_args()
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.modeltype=='cnn':
        vocabfiles={'w2vfile':'../models/bio_embedding_intrinsic.d200',   
                    'charfile':'../dict/char.vocab',
                    'labelfile':'../dict/lable.vocab',
                    'posfile':'../dict/pos.vocab'}
        
        trainfiles={'trainfile':' ',
                    'devfile':' ',
                    'devout':' '}
        trainfiles['trainfile']=args.trainfile
        trainfiles['devfile']=args.devfile
        trainfiles['devout']=args.output+'cnn_dev_temp_b64.tsv'
        modelfile=args.output+'cnn_PT_v1.2.h5'
        CNN_training(trainfiles,vocabfiles,modelfile)
        
    elif args.modeltype=='bioformer':
        
        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'checkpoint_path':'../models/bioformer-cased-v1.0/',
                    'lowercase':False}

        
        trainfiles={'trainfile':' ',
                    'devfile':' ',
                    'devout':' '}
        trainfiles['trainfile']=args.trainfile
        trainfiles['devfile']=args.devfile
        trainfiles['devout']=args.output+'bioformer_dev_temp.tsv'
        modelfile=args.output+'bioformer_PT_v1.2.h5'
        BERT_training(trainfiles,vocabfiles,modelfile)
        
    elif args.modeltype=='pubmedbert':

        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'checkpoint_path':'../models/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext/',
                    'lowercase':True}
        
        trainfiles={'trainfile':' ',
                    'devfile':' ',
                    'devout':' '}
        trainfiles['trainfile']=args.trainfile
        trainfiles['devfile']=args.devfile
        trainfiles['devout']=args.output+'pubmedbert_dev_temp.tsv'
        modelfile=args.output+'pubmedbert_PT_v1.2.h5'
        BERT_training(trainfiles,vocabfiles,modelfile)
    

    elif args.modeltype=='biobert':

        vocabfiles={'labelfile':'../dict/lable.vocab',
                    'checkpoint_path':'../models/biobert-base-cased-v1.2/',
                    'lowercase':False}

        trainfiles={'trainfile':' ',
                    'devfile':' ',
                    'devout':' '}
        trainfiles['trainfile']=args.trainfile
        trainfiles['devfile']=args.devfile
        trainfiles['devout']=args.output+'biobert_dev_temp.tsv'
        modelfile=args.output+'biobert_PT_v1.2-new.h5'
        BERT_training(trainfiles,vocabfiles,modelfile)
