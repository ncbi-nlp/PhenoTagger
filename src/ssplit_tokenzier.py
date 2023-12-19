# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 15:26:44 2020

@author: luol2
"""

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer
lemmatizer = WordNetLemmatizer() 
stemmer = PorterStemmer()
import io
    
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
    
def ssplit_token_pos_lemma(in_text):
    
    fout=io.StringIO()

    line=in_text.strip()
    line=line.replace('-',' - ').replace('/',' / ')
    sentences = nltk.sent_tokenize(line)
    sentences = [nltk.word_tokenize(sent) for sent in sentences] 
#    print(sentences)
    for sent in sentences:
        token_pos = nltk.pos_tag(sent)
        for token in token_pos:
            lemma = lemmatizer.lemmatize(token[0].lower(), get_wordnet_pos(token[1]))
            stem = stemmer.stem(token[0].lower())
            fout.write(token[0]+'\t'+lemma+'\t'+stem+'\t'+token[1]+'\n')
        fout.write('\n')
           
    return fout.getvalue()

def ssplit_token(in_text):
    line=in_text.strip()
    line=line.replace('-',' - ').replace('/',' / ')
    sentences = nltk.sent_tokenize(line)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
#    print(sentences)
    output_tokens=''
    for sent in sentences:
        output_tokens += ' '.join(sent)+' '
    return ' '.join(output_tokens.strip().split())