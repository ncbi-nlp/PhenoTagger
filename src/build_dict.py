# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:02:24 2020

@author: luol2
"""

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

import json
import copy
import sys
import os
import argparse

lemmatizer = WordNetLemmatizer()
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

ALL_CLEAN_NODE=[]
def get_all_child(all_obo,root_node):
    global ALL_CLEAN_NODE
    tree_obo={}
    for i in range(2,len(all_obo)):
        lines=all_obo[i].split('\n')
        for line in lines:
            if line[0:len('id: HP:')]=='id: HP:':
                hpoid=line[len('id: '):]
            elif line[0:len('is_a: ')]=='is_a: ':
                father_hpoid=line[len('is_a: '):line.find(' ! ')]
        if father_hpoid not in tree_obo.keys():
            tree_obo[father_hpoid]=[hpoid]
        else:
            if hpoid not in tree_obo[father_hpoid]:
                tree_obo[father_hpoid].append(hpoid)
#    print(len(tree_obo))
    for ele in root_node:
        get_child(tree_obo,ele)
    return ALL_CLEAN_NODE
def get_child(tree_obo,hpoid):
    global ALL_CLEAN_NODE
    father_hpoid=hpoid
    if father_hpoid not in tree_obo.keys():
        return 1
    else:
        for ele in tree_obo[father_hpoid]:
            if ele not in ALL_CLEAN_NODE:
                ALL_CLEAN_NODE.append(ele)
                get_child(tree_obo,ele)
            
    return 0

'''
    output:dict file, obo json file, label vocab file
    hpo_obo={'HP:0000017':{'name':['Nocturia','nocturia'],
                           'alt_id':[...,...,],
                           'def':'',
                           'synonym':[['Nycturia','nycturia']], [[word_ori,word_lemma]]
                           'replaced_by:'
                           'xref':[...,...],
                           'is_a':[...,...]}}
'''
def build_dict(hpofile, outpath,rootnode):

    
    fin=open(hpofile,'r',encoding='utf-8')
    fout_dic=open(outpath+'noabb_lemma.dic','w',encoding='utf-8')
    fout_nodes=open(outpath+'lable.vocab','w',encoding='utf-8')
    hpo_dict={}
    all_obo=fin.read().strip().split('\n\n')
    fin.close()

    
    all_nodes=get_all_child(all_obo,rootnode) #get all nodes
    for ele in all_nodes:
        fout_nodes.write(ele+'\n')
    fout_nodes.write('HP:None'+'\n') #neg label
    fout_nodes.close()
    
    fout_obo=open(outpath+'obo.json','w',encoding='utf-8')
    
    hpo_obo={}
    for i in range(2,len(all_obo)):
        lines=all_obo[i].split('\n')
        first_name=[]
        synonym_list=[]
        alt_id_list=[]
        def_string=''
        is_obsolete=''
        replace_id=''
        xref_list=[]
        isa_list=[]
        for line in lines:
            if line.find('id: HP:')==0:
                hpoid=line[len('id: '):]
            elif line.find('name:')==0:
                term=line[len('name: '):]
                if term.isupper():
                    pass
#                    print('first name:',term)
                else:
                    tokens = word_tokenize(term.strip().lower().replace('-',' - ').replace('/',' / '))  
                    token_pos = nltk.pos_tag(tokens)
                    lemmas = [lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) for token in token_pos]    
                    first_name_ori=' '.join(tokens)
                    first_name_lemma=' '.join(lemmas)
                    first_name=[first_name_ori,first_name_lemma]
                    
                    if hpoid in all_nodes:  #input dict
                        hpo_dict[first_name_ori]=len(tokens)
                        hpo_dict[first_name_lemma]=len(lemmas)
                    
            elif line.find('alt_id: ')==0:
                alt_id=line[len('alt_id: '):]
                if alt_id not in alt_id_list:
                    alt_id_list.append(alt_id)
            elif line.find('def: "')==0:
                eid=line.find('" ')
                def_string=line[len('def: "'):eid]
            elif line.find('synonym:')==0:
                eid=line.find('" ')
                term=line[len('synonym: "'):eid]
                if term.isupper():
                    pass
#                    print('synonym name:',term)
                else:
                    tokens = word_tokenize(term.strip().lower().replace('-',' - ').replace('/',' / '))  
                    token_pos = nltk.pos_tag(tokens)
                    lemmas = [lemmatizer.lemmatize(token[0], get_wordnet_pos(token[1])) for token in token_pos]                        
                    synonym_ori=' '.join(tokens)
                    synonym_lemma=' '.join(lemmas)
                    temp_list=[synonym_ori,synonym_lemma]
                    if temp_list not in synonym_list: 
                        synonym_list.append(temp_list)
                    
                    if hpoid in all_nodes:  #input dict
                        hpo_dict[synonym_ori]=len(tokens)
                        hpo_dict[synonym_lemma]=len(lemmas)
                    
            elif line.find('xref: ')==0:
                xref_id=line[len('xref: '):]
                if xref_id not in xref_list:
                    xref_list.append(xref_id)
            elif line.find('is_a: ')==0:
                eid=line.find(' ! ')
                isa_id=line[len('is_a: '):eid]
                if isa_id not in isa_list:
                    isa_list.append(isa_id)
            elif line.find('is_obsolete: ')==0:
                is_obsolete=line[len('is_obsolete: '):]
            elif line.find('replaced_by: ')==0:
                replace_id=line[len('replaced_by: '):]
                
        hpo_obo[hpoid]={'name':first_name,'alt_id':alt_id_list,'def':def_string,'synonym':synonym_list,'xref':xref_list,'is_a':isa_list,'is_obsolete':is_obsolete,'replace_id':replace_id}
    
    sort_hpo_dict=sorted(hpo_dict.items(), key=lambda kv:(kv[1], kv[0]), reverse=False)
    for ele in sort_hpo_dict:
        fout_dic.write(ele[0]+'\n')
    fout_dic.close()
                    
    json.dump(hpo_obo, fout_obo ,indent=2)
    fout_obo.close()
    return hpo_obo
    
#mapping all words + lemma 
def word_hpo_map(hpo_obo, outpath):

    fout=open(outpath+'word_id_map.json','w',encoding='utf-8')
    
    word_hpoid={}

    for hpoid in hpo_obo.keys():
        first_name_ori=hpo_obo[hpoid]['name'][0]
        first_name=hpo_obo[hpoid]['name'][1]
        if first_name!=first_name_ori:
            if first_name not in word_hpoid.keys():
                word_hpoid[first_name]=[hpoid]
            else:
                if word_hpoid[first_name][0]!=hpoid:
                    word_hpoid[first_name]=[hpoid]

            if first_name_ori not in word_hpoid.keys():
                word_hpoid[first_name_ori]=[hpoid]
            else:
                if word_hpoid[first_name_ori][0]!=hpoid:
                    word_hpoid[first_name_ori]=[hpoid]
        else:
            if first_name not in word_hpoid.keys():
                word_hpoid[first_name]=[hpoid]
            else:
                if word_hpoid[first_name][0]!=hpoid:
                    word_hpoid[first_name]=[hpoid]

               
        for synonym in hpo_obo[hpoid]['synonym']:
            word=synonym[1]
            word_ori=synonym[0]
            if word_ori == word:
                if word not in word_hpoid.keys():
                    word_hpoid[word]=[hpoid]
                else:
                    if word_hpoid[word][0]!=hpoid:
                        old_hpoid=word_hpoid[word][0]
                        new_hpoid=hpoid
                        if hpo_obo[old_hpoid]['name'][1]!=word:
                            word_hpoid[word].append(new_hpoid)

            else:
                if word not in word_hpoid.keys():
                    word_hpoid[word]=[hpoid]
                else:
                    if word_hpoid[word][0]!=hpoid:
                        old_hpoid=word_hpoid[word][0]
                        new_hpoid=hpoid
                        if hpo_obo[old_hpoid]['name'][1]!=word:
                            word_hpoid[word].append(new_hpoid)

                if word_ori not in word_hpoid.keys():
                    word_hpoid[word_ori]=[hpoid]
                else:
                    if word_hpoid[word_ori][0]!=hpoid:
                        old_hpoid=word_hpoid[word_ori][0]
                        new_hpoid=hpoid
                        if hpo_obo[old_hpoid]['name'][0]!=word_ori:
                            word_hpoid[word_ori].append(new_hpoid)

    json.dump(word_hpoid, fout,indent=2)
    fout.close()
    
#hpoid word mapping    
def hpo_word_map(hpo_obo, outpath):
    fout=open(outpath+'id_word_map.json','w',encoding='utf-8')
    hpoid_word={}

    for hpoid in hpo_obo.keys():
        first_name=hpo_obo[hpoid]['name'][1]
        first_name_ori=hpo_obo[hpoid]['name'][0]
        if first_name_ori==first_name:
            if hpoid not in hpoid_word.keys():
                hpoid_word[hpoid]=[first_name]
            else:
                if first_name not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(first_name)
        else:
            if hpoid not in hpoid_word.keys():
                hpoid_word[hpoid]=[first_name,first_name_ori]
            else:
                if first_name not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(first_name)
                if first_name_ori not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(first_name_ori)
            
               
        for synonym in hpo_obo[hpoid]['synonym']:
            word=synonym[1]
            word_ori=synonym[0]
            if word==word_ori:
                if word not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(word)
            else:
                if word not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(word)
                if word_ori not in hpoid_word[hpoid]:
                    hpoid_word[hpoid].append(word_ori)
                    
        for alt_id in hpo_obo[hpoid]['alt_id']:
            if alt_id not in hpoid_word.keys():
                hpoid_word[alt_id]=hpoid_word[hpoid]
            else:
                temp=copy.deepcopy(hpoid_word[alt_id])
                for ele in hpoid_word[hpoid]:
                    if ele not in temp:
                        temp.append(ele)
                hpoid_word[alt_id]=copy.deepcopy(temp)
                hpoid_word[hpoid]=copy.deepcopy(temp)

    json.dump(hpoid_word, fout,indent=2)
    fout.close()    


if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='build ontogoly dictionary, python Build_dict.py -i infile -o outpath -r rootnode')
    parser.add_argument('--input', '-i', help="input the ontology .obo file",default='../ontology/hp.obo')
    parser.add_argument('--output', '-o', help="the output path of dictionary",default='../dict/')
    parser.add_argument('--rootnode','-r',help="input the root node of the ontogyly",nargs='+', default=['HP:0000118'])
    args = parser.parse_args()
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    print('building dictionary........')
    hpo_obo=build_dict(args.input,args.output,args.rootnode)
    
    word_hpo_map(hpo_obo, args.output)
    
    hpo_word_map(hpo_obo, args.output)
    
    print('building dictionary done........')

