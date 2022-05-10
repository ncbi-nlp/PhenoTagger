# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 15:05:00 2020

@author: luol2
"""
import sys
import json
import io
from ssplit_tokenzier import ssplit_token_pos_lemma
class Trie(object):
    class Node(object):
        def __init__(self):
            self.term = None
            self.next = {}
    
    def __init__(self, terms=[]):
        self.root = Trie.Node()
        for term in terms:
            self.add(term)
    
    def add(self, term):
        node = self.root
        for char in term:
            if not char in node.next:
                node.next[char] = Trie.Node()
            node = node.next[char]
        node.term = term
    
    def match(self, query):
        results = []
        for i in range(len(query)):
            node = self.root
            for j in range(i, len(query)):
                node = node.next.get(query[j])
                if not node:
                    break
                if node.term:
                    results.append((i, len(node.term)))
        return results
    
    def __repr__(self):
        output = []
        def _debug(output, char, node, depth=0):
            output.append('%s[%s][%s]' % (' '*depth, char, node.term))
            for (key, n) in node.next.items():
                _debug(output, key, n, depth+1)
        _debug(output, '', self.root)
        return '\n'.join(output)
    
class dic_ont():

    def __init__(self, ont_files):
        
        dicin=open(ont_files['dic_file'],'r',encoding='utf-8')
        win_size=50000
        Dic=[]
        print("loading dict!") 
        for line in dicin:
            line=line.strip()
            if len(line.split())<=win_size:
                words=line.split()
                for i in range(len(words)):
                    if len(words[i])>3 and (not words[i].isupper()):
                        words[i]=words[i].lower()
                line=' '.join(words[0:])
                Dic.append(line.strip())
        print("Dic_len:",len(Dic))
        dicin.close()
        
        self.dic_trie = Trie(Dic)
        print("load dic done!")
        
        #load word hpo mapping
        fin_map=open(ont_files['word_hpo_file'],'r',encoding='utf-8')
        self.word_hpo=json.load(fin_map)
        fin_map.close()
        
        #load hpo word mapping
        fin_map=open(ont_files['hpo_word_file'],'r',encoding='utf-8')
        self.hpo_word=json.load(fin_map)
        fin_map.close()
    
    def matching(self, source):
    
        fin=io.StringIO(source)
        fout=io.StringIO()
            
        sent_list=[]
        sent = []
        sent_ori_list=[]
        sent_ori=[]
        
        for line in fin:
            line=line.strip()
            if line=="":
                sent_list.append(sent)
                sent_ori_list.append(sent_ori)
                sent=[]
                sent_ori=[]         
            else:
                words=line.split('\t')
                words[1]=words[1].lower()
                sent.append(words[1])   # word lemma
                sent_ori.append(words[0])
        sent=[]       
        fin.close()
        
        for k in range(len(sent_list)):
            sent = sent_list[k]
            sentence=' '.join(sent[0:])+" "
            sentence_ori=' '.join(sent_ori_list[k])
#            print('sentence:',sentence)
            result=self.dic_trie.match(sentence) 
#            print('result:',result)
            new_result=[]
            for i in range(0,len(result)):               
                if result[i][0]==0 and sentence[result[i][1]]==" ":
                    new_result.append([result[i][0],result[i][0]+result[i][1]])
                elif result[i][0]>0 and sentence[result[i][0]-1]==' ' and sentence[result[i][0]+result[i][1]]==' ':
                    new_result.append([result[i][0],result[i][0]+result[i][1]])
#            print('new result:',new_result)
            
           
                 
            if len(new_result)==0:
                fout.write(sentence_ori+'\n\n')
                 
            else:
                fout.write(sentence_ori+'\n')
                for ele in new_result:
                    entity_text=sentence[ele[0]:ele[1]]
                    if entity_text in self.word_hpo.keys():
                        hpoid=self.word_hpo[entity_text]
                    else:
                        print('no id:', entity_text)
                        hpoid=['None']
                    if ele[0]==0:
                        sid="0"
                    else:
                        temp_sent=sentence[0:ele[0]]
                        sid=str(len(temp_sent.rstrip().split(' ')))
                    temp_sent=sentence[0:ele[1]]
                    eid=str(len(temp_sent.rstrip().split(' '))-1)
#                    print(sid,eid,entity_text,hpoid[0])
                    #fout.write(sid+'\t'+eid+'\t'+entity_text+'\t'+";".join(hpoid)+'\t1.00\n')
                    fout.write(sid+'\t'+eid+'\t'+entity_text+'\t'+hpoid[0]+'\t1.00\n')        
                fout.write('\n')
        
        return fout.getvalue()
     

if __name__=='__main__':
    
    ontfiles={'dic_file':'//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/dict/hpo_noabb_lemma.dic',
              'word_hpo_file':'//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/dict/word_hpoid_map.json',
              'hpo_word_file':'//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/dict/hpoid_word_map.json'}
    biotag_dic=dic_ont(ontfiles)
    text='Nevoid basal cell carcinoma syndrome (NBCCS) is a hereditary condition transmitted as an autosomal dominant trait with complete penetrance and variable expressivity. The syndrome is characterised by numerous basal cell carcinomas (BCCs), odontogenic keratocysts of the jaws, palmar and/or plantar pits, skeletal abnormalities and intracranial calcifications. In this paper, the clinical features of 37 Italian patients are reviewed. Jaw cysts and calcification of falx cerebri were the most frequently observed anomalies, followed by BCCs and palmar/plantar pits. Similar to the case of African Americans, the relatively low frequency of BCCs in the Italian population is probably due to protective skin pigmentation. A future search based on mutation screening might establish a possible genotype phenotype correlation in Italian patients.'
    ssplit_token=ssplit_token_pos_lemma(text)
#    print(ssplit_token)
    dic_result=biotag_dic.matching(ssplit_token)
    print(dic_result)

    
