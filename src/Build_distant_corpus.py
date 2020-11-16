# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:19:32 2020

@author: luol2
"""

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer
import nltk
import numpy as np
import json
import copy
import sys
import argparse
import os
np.random.seed(123)

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()  
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R') or treebank_tag=='IN':
        return wordnet.ADV
    else:
        return wordnet.NOUN

def train_pos(hpo_obo,hpo_vocab,outpath):
    fout=open(outpath+'distant_train_pos.conll','w',encoding='utf-8')
 
    for hpoid in hpo_vocab:
        if hpoid=='HP:None':
            continue
        term_name=hpo_obo[hpoid]['name']
        temp_out=[]
        temp_out.append(hpoid+'\t'+term_name[0])
        tokens = term_name[0].split(' ')
        token_pos = nltk.pos_tag(tokens)
        for token in token_pos:
            lemma = lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) 
            stem = stemmer.stem(token[0])                
            temp_out.append(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\tB\tB')
        fout.write('\n'.join(temp_out)+'\n\n')
        if term_name[0]!=term_name[1]:
            temp_out=[]
            temp_out.append(hpoid+'\t'+term_name[1])
            tokens = term_name[1].split(' ')
            token_pos = nltk.pos_tag(tokens)
            for token in token_pos:
                lemma = lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) 
                stem = stemmer.stem(token[0])                
                temp_out.append(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\tB\tB')
            fout.write('\n'.join(temp_out)+'\n\n')
            
        term_synonyms= hpo_obo[hpoid]['synonym'] 
        for term_name in term_synonyms:
            temp_out=[]
            temp_out.append(hpoid+'\t'+term_name[0])
            tokens = term_name[0].split(' ')
            token_pos = nltk.pos_tag(tokens)
            for token in token_pos:
                lemma = lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) 
                stem = stemmer.stem(token[0])                
                temp_out.append(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\tB\tB')
            fout.write('\n'.join(temp_out)+'\n\n')
            if term_name[0]!=term_name[1]:
                temp_out=[]
                temp_out.append(hpoid+'\t'+term_name[1])
                tokens = term_name[1].split(' ')
                token_pos = nltk.pos_tag(tokens)
                for token in token_pos:
                    lemma = lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) 
                    stem = stemmer.stem(token[0])                
                    temp_out.append(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\tB\tB')
                fout.write('\n'.join(temp_out)+'\n\n')
    fout.close()
    
def pun_filter(temp_entity):

    pun_list1=['.','!',';',':','?','(',')','[',']','{','}']
    pun_list2=[',','-','/']
    filter_flag=0
    
    if (temp_entity[1].split('\t')[0] in pun_list2) or (temp_entity[-1].split('\t')[0] in pun_list2):
        filter_flag=1
    for ele in temp_entity[1:]:
        token=ele.split('\t')[0]
        if token in pun_list1:
            filter_flag=1
            break
    return filter_flag

def pos_filter(temp_entity):
    pos_list_l=['PRP']
    pos_list=['IN','DT','CC','O','MD','EX','POS','WDT','WP','WP$','WRB','TO','PRP$']
    verb_word=['is','are','was','were','had','have','has','be','been','also']
    filter_flag=0
    
    token_s=temp_entity[1].split('\t')[0]
    token_e=temp_entity[-1].split('\t')[0]
    pos_s=temp_entity[1].split('\t')[3]
    pos_e=temp_entity[-1].split('\t')[3]
    if (token_s in verb_word) or (token_e in verb_word):
        filter_flag=1
    if (pos_s in pos_list) or (pos_e in pos_list) or (pos_s in pos_list_l):
        filter_flag=1
    return filter_flag
    
    
def train_neg(negfile,num,hpo_dic,outpath):

    fin=open(negfile,'r',encoding='utf-8',errors='replace') 
    fout=open(outpath+'distant_train_neg.conll','w',encoding='utf-8')
    all_text = fin.read().split()
    fin.close()
    indecies = np.random.choice(len(all_text), num*100)
    lengths = np.random.randint(1, 10, num*100)
    neg_num=0
    i=0
    while(neg_num<num):
        negative_text=' '.join(all_text[indecies[i]:indecies[i]+lengths[i]])
        tokens = word_tokenize(negative_text.strip().lower().replace('-',' - ').replace('/',' / '))
        negative_text=' '.join(tokens)
        i+=1
#        print(negative_text)
        temp_out=[]
        if negative_text not in hpo_dic:         
            temp_out.append('HP:None\t'+negative_text)
            token_pos = nltk.pos_tag(tokens)
            for token in token_pos:
                lemma = lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) 
                stem = stemmer.stem(token[0])                
                temp_out.append(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\tB\tB')
            if pun_filter(temp_out)==0 and pos_filter(temp_out)==0:
                neg_num+=1
                fout.write('\n'.join(temp_out)+'\n\n')
            else:
                pass
                #print('filter:',negative_text)
    #print('neg_num:',neg_num)
    fout.close()
def combine_pos_neg(outpath):
    fin_pos=open(outpath+'distant_train_pos.conll','r',encoding='utf-8')
    fin_neg=open(outpath+'distant_train_neg.conll','r',encoding='utf-8') 
    fout=open(outpath+'distant_train.conll','w',encoding='utf-8')
    all_pos=fin_pos.read().rstrip()
    all_neg=fin_neg.read().rstrip()
    fin_pos.close()
    fin_neg.close()
    fout.write(all_pos+'\n\n'+all_neg+'\n')
    fout.close()
if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='build distant training corpus, python Build_distant_corpus.py -d dictpath -f fileneg  -n number_of_neg -o outpath')
    parser.add_argument('--dict', '-d', help="the input path of the ontology dictionary",default='../dict/')
    parser.add_argument('--fileneg', '-f', help="the text file used to generate the negatives",default='../mutation_disease.txt')
    parser.add_argument('--negnum', '-n', help="the number of negatives ",type=int, default=10000)
    parser.add_argument('--output', '-o', help="the output folder of the distantly-supervised training dataset",default='../data/distant_train_data/')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    fin_obo=open(args.dict+'obo.json','r',encoding='utf-8')
    hpo_obo=json.load(fin_obo)
    fin_obo.close()   
    fin_label=open(args.dict+'lable.vocab','r',encoding='utf-8')
    hpo_vocab=fin_label.read().strip().split('\n')
    fin_label.close()
    fin_dic=open(args.dict+'noabb_lemma.dic','r',encoding='utf-8')
    hpo_dic=fin_dic.read().strip().split('\n')
    fin_dic.close()
    
    print('generating training positives........')
    train_pos(hpo_obo,hpo_vocab,args.output)
    print('done..........')
    
    print('generating training negatives........')
    train_neg(args.fileneg,args.negnum,hpo_dic,args.output)
    print('done..........')
    
    combine_pos_neg(args.output)