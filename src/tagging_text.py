# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 16:21:23 2020

@author: luol2
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 11:33:22 2020

@author: luol2
"""
import argparse
from ssplit_tokenzier import ssplit_token_pos_lemma
from ml_ner import ml_tagging,ml_tagging_allngram
from combine_result import combine_ml_dict
from restore_index import restore_index_nest_fn
from nn_model import bioTag_CNN,bioTag_BERT
from dic_ner import dic_ont
from evaluate import GSCplus_corpus,JAX_corpus
from post_processing import combine_overlap
from abbre_resolution import postprocess_abbr
import os
import time
import json

#hybrid method
def bioTag(text,biotag_dic,ml_model,onlyLongest=False, abbrRecog=False, Threshold=0.95):

#    startTime=time.time()
    ssplit_token=ssplit_token_pos_lemma(text)
#    print(ssplit_token) 
#    print('ssplit token:',time.time()-startTime)
    
#    startTime=time.time()
    dict_tsv=biotag_dic.matching(ssplit_token)
#    print('dict tsv:\n',dict_tsv)
#    print('dict ner:',time.time()-startTime)
  
#    startTime=time.time()
    ml_tsv=ml_tagging(ssplit_token,ml_model,Threshold)
    #print('ml_tsv:\n',ml_tsv)
#    print('ml ner:',time.time()-startTime)
    
#    startTime=time.time()
    combine_tsv=combine_ml_dict(dict_tsv,ml_tsv)
    #combine_tsv=combine_ml_dict_fn(ml_tsv,dict_tsv)
    #print('combine:\n',combine_tsv)
    
    final_result=  restore_index_nest_fn(text,combine_tsv)
#    print('final ner:',time.time()-startTime)
    if onlyLongest==True:
        final_result=combine_overlap(final_result)
    if abbrRecog==True:
        final_result=postprocess_abbr(final_result,text)
#    print('final result:') 
#    print(final_result)
    
    return final_result

# only machine learning-based method
def bioTag_ml(text,ml_model,onlyLongest=False,abbrRecog=False, Threshold=0.95):

#    startTime=time.time()
    ssplit_token=ssplit_token_pos_lemma(text)
#    print(ssplit_token) 
#    print('ssplit token:',time.time()-startTime)
    
#    startTime=time.time()
    ml_tsv=ml_tagging_allngram(ssplit_token,ml_model,Threshold)
#    print('ml_tsv:\n',ml_tsv)
#    print('ml ner:',time.time()-startTime)
       
    final_result=  restore_index_nest_fn(text,ml_tsv)
#    print('final ner:',time.time()-startTime)
    if onlyLongest==True:
        final_result=combine_overlap(final_result)
    
    if abbrRecog==True:
        final_result=postprocess_abbr(final_result,text)
    
    return final_result

# only dict method
def bioTag_dic(text,biotag_dic,onlyLongest=False, abbrRecog=False):

#    startTime=time.time()
    ssplit_token=ssplit_token_pos_lemma(text)
#    print(ssplit_token) 
#    print('ssplit token:',time.time()-startTime)
    
#    startTime=time.time()
    dict_tsv=biotag_dic.matching(ssplit_token)
#    print('dict tsv:\n',dict_tsv)
#    print('dict ner:',time.time()-startTime)
    
    final_result=  restore_index_nest_fn(text,dict_tsv)
#    print('final ner:',time.time()-startTime)
    if onlyLongest==True:
        final_result=combine_overlap(final_result)
    
    if abbrRecog==True:
        final_result=postprocess_abbr(final_result,text)
    
    return final_result

