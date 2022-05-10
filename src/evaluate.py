# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 08:58:50 2020

@author: luol2
"""
'''
document level evaluation
input: prediction/gold result({'pmid':[[sid1,eid1,hpoid1],[sid2,eid2,hpoid2]]})

'''
import json
import copy
#change alt hpoid to first hpoid
def alt_hpo():
    path='//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/'
    fin=open(path+'hpo_obo.json','r',encoding='utf-8')
    fout=open(path+'alt_hpoid.json','w',encoding='utf-8')
    hpo_obo=json.load(fin)
    fin.close()
    alt_hpoid={}
    for hpoid in hpo_obo.keys():
        
        if hpo_obo[hpoid]['is_obsolete']=='':
            alt_hpoid[hpoid]=hpoid
            for ele in hpo_obo[hpoid]['alt_id']:
                if ele not in alt_hpoid.keys():
                    alt_hpoid[ele]=hpoid
                else:
                    print('alt_id:',ele,'old:',alt_hpoid[ele])
    json.dump(alt_hpoid, fout ,indent=2)
def document_metric(pre_result, gold_result):
   
   
    pre_num=0
    gold_num=0
    total_pre_true=0
    file_num=0
    macroP,macroR,macroF=0,0,0
    microP,microR,microF=0,0,0
    for pre_id in pre_result.keys():
        doc_pre=[]
        doc_gold=[]
        for ele in pre_result[pre_id]:
            if ele[2] not in doc_pre:
                doc_pre.append(ele[2])
        for ele in gold_result[pre_id]:
            if ele[2] not in doc_gold:
                doc_gold.append(ele[2])
        file_num+=1
        doc_pre_true=0        
        pre_num+=len(doc_pre)
        gold_num+=len(doc_gold)
        
        for ele in doc_pre:
            if ele in doc_gold:
                total_pre_true+=1
                doc_pre_true+=1
                              
        if len(doc_pre)==0 and len(doc_gold)==0:
            temp_macroP,temp_macroR,temp_macroF=1,1,1
        elif len(doc_pre)==0 and len(doc_gold)!=0:
            temp_macroP,temp_macroR,temp_macroF=0,0,0
        elif len(doc_pre)!=0 and len(doc_gold)==0:
            temp_macroP,temp_macroR,temp_macroF=0,0,0
        elif len(doc_pre)!=0 and len(doc_gold)!=0:
            temp_macroP=doc_pre_true/len(doc_pre)
            temp_macroR=doc_pre_true/len(doc_gold)
            if temp_macroP+temp_macroR==0:
                temp_macroF=0
            else:
                temp_macroF=2*temp_macroP*temp_macroR/(temp_macroP+temp_macroR)
                
        macroP+=temp_macroP
        macroR+=temp_macroR
        macroF+=temp_macroF
    macroP=macroP/file_num
    macroR=macroR/file_num
    if macroP+macroR!=0:
        macroF=2*macroP*macroR/(macroP+macroR)
    else:
        macroF=0
    
    if pre_num==0 and gold_num==0:
        microP,microR,microF=1,1,1
    elif pre_num==0 and gold_num!=0:
        microP,microR,microF=0,0,0
    elif pre_num!=0 and gold_num==0:
        microP,microR,microF=0,0,0
    elif pre_num!=0 and gold_num!=0:    
        microP=total_pre_true/pre_num
        microR=total_pre_true/gold_num
        microF=2*microP*microR/(microP+microR)
    print('......document level evaluation:......')
    print('file num:',file_num)
    print(gold_num,pre_num,total_pre_true)
    print('miP=%.5f, miR=%.5f, miF=%.5f' %(microP,microR,microF))
    print('maP=%.5f, maR=%.5f, maF=%.5f' %(macroP,macroR,macroF))
    return macroF

def mention_metric_new(pre_result, gold_result):

    gold_num=0
    NER_true_num_Ps=0
    NER_true_num_Rs=0
    NER_true_num_Pr=0
    NER_true_num_Rr=0
    pre_num=0
    NEN_true_num_Ps=0
    NEN_true_num_Rs=0
    NEN_true_num_Pr=0
    NEN_true_num_Rr=0
    

    for pmid in pre_result.keys():
        
        doc_pre=copy.deepcopy(pre_result[pmid])
        doc_gold=copy.deepcopy(gold_result[pmid])
        
        gold_num+=len(doc_gold)
        pre_num+=len(doc_pre)
        
        entity_gold={}
        for ele in doc_gold:
            entity_index=ele[0]+' '+ele[1]
            if entity_index not in entity_gold.keys():
                entity_gold[entity_index]=ele[2]
            else:
                print('over!!',ele)
        entity_pre={}
        for ele in doc_pre:
            entity_index=ele[0]+' '+ele[1]
            if entity_index not in entity_pre.keys():
                entity_pre[entity_index]=[ele[2]]
            else:
                if ele[2] not in entity_pre[entity_index]:
                    entity_pre[entity_index].append(ele[2])
        
        for pre_ele in doc_pre:
            pre_index=pre_ele[0]+' '+pre_ele[1]
            if pre_index in entity_gold.keys():
                NER_true_num_Ps+=1
                if pre_ele[2] == entity_gold[pre_index]:
                    NEN_true_num_Ps+=1
        
        
        for gold_ele in doc_gold:
            gold_index=gold_ele[0]+' '+gold_ele[1]
            if gold_index in entity_pre.keys():
                NER_true_num_Rs+=1
                if gold_ele[2] in entity_pre[gold_index]:
                    NEN_true_num_Rs+=1
        
        for pre_ele in doc_pre:
            ner_flag=0
            for gold_ele in doc_gold:
                if max(int(pre_ele[0]),int(gold_ele[0])) <= min(int(pre_ele[1]),int(gold_ele[1])):
                    ner_flag=1
                    if pre_ele[2]==gold_ele[2]:
                        NEN_true_num_Pr+=1    
                        break
            if ner_flag==1:
                NER_true_num_Pr+=1
        
        for gold_ele in doc_gold:
            ner_flag=0
            for pre_ele in doc_pre:
                pre_index=pre_ele[0]+' '+pre_ele[1]
                if max(int(pre_ele[0]),int(gold_ele[0])) <= min(int(pre_ele[1]),int(gold_ele[1])):
                    ner_flag=1
                    if gold_ele[2] in entity_pre[pre_index]:
                        NEN_true_num_Rr+=1    
                        break
            if ner_flag==1:
                NER_true_num_Rr+=1
        
       
                
    if pre_num==0 and gold_num==0:
        NER_P_s,NER_R_s,NER_F_s=1,1,1
        NER_P_r,NER_R_r,NER_F_r=1,1,1
        NEN_P_s,NEN_R_s,NEN_F_s=1,1,1
        NEN_P_r,NEN_R_r,NEN_F_r=1,1,1

    elif pre_num==0 and gold_num!=0:
        NER_P_s,NER_R_s,NER_F_s=0,0,0
        NER_P_r,NER_R_r,NER_F_r=0,0,0
        NEN_P_s,NEN_R_s,NEN_F_s=0,0,0
        NEN_P_r,NEN_R_r,NEN_F_r=0,0,0
        
    elif pre_num!=0 and gold_num==0:
        NER_P_s,NER_R_s,NER_F_s=0,0,0
        NER_P_r,NER_R_r,NER_F_r=0,0,0
        NEN_P_s,NEN_R_s,NEN_F_s=0,0,0
        NEN_P_r,NEN_R_r,NEN_F_r=0,0,0
    elif pre_num!=0 and gold_num!=0:
        
        NER_P_s=NER_true_num_Ps/pre_num
        NER_P_r=NER_true_num_Pr/pre_num
        NEN_P_s=NEN_true_num_Ps/pre_num
        NEN_P_r=NEN_true_num_Pr/pre_num
        
        NER_R_s=NER_true_num_Rs/gold_num
        NER_R_r=NER_true_num_Rr/gold_num
        NEN_R_s=NEN_true_num_Rs/gold_num
        NEN_R_r=NEN_true_num_Rr/gold_num

        NER_F_s=2*NER_P_s*NER_R_s/(NER_P_s+NER_R_s)
        NER_F_r=2*NER_P_r*NER_R_r/(NER_P_r+NER_R_r)
        NEN_F_s=2*NEN_P_s*NEN_R_s/(NEN_P_s+NEN_R_s)
        NEN_F_r=2*NEN_P_r*NEN_R_r/(NEN_P_r+NEN_R_r)
        
    print('......memtion level evaluation:......')
    print(gold_num,pre_num)
    print('NER P_s=%.5f, R_s=%.5f, F_s=%.5f' %(NER_P_s,NER_R_s,NER_F_s))
    print('NER P_r=%.5f, R_r=%.5f, F_r=%.5f' %(NER_P_r,NER_R_r,NER_F_r))  
    print('NEN P_s=%.5f, R_s=%.5f, F_s=%.5f' %(NEN_P_s,NEN_R_s,NEN_F_s))
    print('NEN P_r=%.5f, R_r=%.5f, F_r=%.5f' %(NEN_P_r,NEN_R_r,NEN_F_r))
    return NEN_F_r

def mention_metric(pre_result, gold_result):

    gold_num=0
    NER_true_num_s=0
    NER_true_num_r=0
    pre_num=0
    NEN_true_num_s=0
    NEN_true_num_r=0

    for pre_id in pre_result.keys():
        
        doc_pre={}
        doc_gold={}
        for ele in pre_result[pre_id]:
            doc_pre[ele[0]+' '+ele[1]]=ele[2]
        for ele in gold_result[pre_id]:
            doc_gold[ele[0]+' '+ele[1]]=ele[2]
        
        gold_num+=len(doc_gold)
        pre_num+=len(doc_pre)

        for pre in doc_pre.keys():
            if pre in doc_gold.keys():
                NER_true_num_s+=1
                if doc_pre[pre] == doc_gold[pre]:
                    NEN_true_num_s+=1
        

        for pre in doc_pre.keys():
            pre_seg=pre.split()
            for gold in doc_gold.keys():
                gold_seg=gold.split()
                if max(int(pre_seg[0]),int(gold_seg[0])) <= min(int(pre_seg[1]),int(gold_seg[1])):
                    NER_true_num_r+=1
                    break
                
        for pre in doc_pre.keys():
            pre_seg=pre.split()
            for gold in doc_gold.keys():
                gold_seg=gold.split()
                if max(int(pre_seg[0]),int(gold_seg[0])) <= min(int(pre_seg[1]),int(gold_seg[1])):
                    if doc_pre[pre] == doc_gold[gold]:
                        NEN_true_num_r+=1
                        break
                
    if pre_num==0:
        NER_P_s=0
        NER_P_r=0
        NEN_P_s=0
        NEN_P_r=0
    else:
        NER_P_s=NER_true_num_s/pre_num
        NER_P_r=NER_true_num_r/pre_num
        NEN_P_s=NEN_true_num_s/pre_num
        NEN_P_r=NEN_true_num_r/pre_num


    NER_R_s=NER_true_num_s/gold_num 
    if NER_P_s+NER_R_s==0:
        NER_F_s=0
    else:
        NER_F_s=2*NER_P_s*NER_R_s/(NER_P_s+NER_R_s)
    
    
    NER_R_r=NER_true_num_r/gold_num
    if NER_P_r+NER_R_r==0:
        NER_F_r=0
    else:
        NER_F_r=2*NER_P_r*NER_R_r/(NER_P_r+NER_R_r)
    

    NEN_R_s=NEN_true_num_s/gold_num
    if NEN_P_s+NEN_R_s==0:
        NEN_F_s=0
    else:
        NEN_F_s=2*NEN_P_s*NEN_R_s/(NEN_P_s+NEN_R_s)
    
    NEN_R_r=NEN_true_num_r/gold_num
    if NEN_P_r+NEN_R_r==0:
        NEN_F_r=0
    else:
        NEN_F_r=2*NEN_P_r*NEN_R_r/(NEN_P_r+NEN_R_r)
    print('......memtion level evaluation:......')
    print(gold_num,pre_num,NER_true_num_s,NER_true_num_r,NEN_true_num_s,NEN_true_num_r)
    print('NER P_s=%.5f, R_s=%.5f, F_s=%.5f' %(NER_P_s,NER_R_s,NER_F_s))
    print('NER P_r=%.5f, R_r=%.5f, F_r=%.5f' %(NER_P_r,NER_R_r,NER_F_r))  
    print('NEN P_s=%.5f, R_s=%.5f, F_s=%.5f' %(NEN_P_s,NEN_R_s,NEN_F_s))
    print('NEN P_r=%.5f, R_r=%.5f, F_r=%.5f' %(NEN_P_r,NEN_R_r,NEN_F_r))
    return NEN_F_r
def find_maxlen_entity_nest(nest_list):
    temp_result_list={}
    for i in range(0, len(nest_list)):
        hpoid=nest_list[i][-1]
        leng=len(nest_list[i][2].split())
        if hpoid not in temp_result_list.keys():
            temp_result_list[hpoid]=nest_list[i]
        else:
            if leng>len(temp_result_list[hpoid][2].split()):
                temp_result_list[hpoid]=nest_list[i]
    new_list=[]
    for hpoid in temp_result_list.keys():
        new_list.append(temp_result_list[hpoid])
    return new_list
#turn the GSC to gold HPO id, only subtree,drop the nest entity with same hpoid, remain the longest
def GSCplus_corpus_gold():
    path='//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/'
    fin=open(path+'GSCplus_dev_gold_ori.tsv','r',encoding='utf-8')
    fout=open(path+'GSCplus_dev_gold.tsv','w',encoding='utf-8')
    fin_alt=open(path+'alt_hpoid.json','r',encoding='utf-8')
    fin_subtree=open(path+'hpo_lable.vocab','r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_gold=fin.read().strip().split('\n\n')
    fin.close()

    for doc in all_gold:
        lines=doc.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if hpoid in subtree_list:
                    seg[3]=hpoid
                    temp_result.append(seg)

            else:
                print('pre hpo obo no this id:',lines[i])
        entity_list=[]
        if len(temp_result)>1:
            first_entity=temp_result[0]
            nest_list=[first_entity]
            max_eid=int(first_entity[1])
            for i in range(1,len(temp_result)):
                segs=temp_result[i]
                if int(segs[0])> max_eid:
                    if len(nest_list)==1:
                        entity_list.append(nest_list[0])
                        nest_list=[]
                        nest_list.append(segs)
                        if int(segs[1])>max_eid:
                            max_eid=int(segs[1])
                    else:
                        tem=find_maxlen_entity_nest(nest_list)#find max entity
                        entity_list.extend(tem)
                        nest_list=[]
                        nest_list.append(segs)
                        if int(segs[1])>max_eid:
                            max_eid=int(segs[1])
                       
                else:
                    nest_list.append(segs)
                    if int(segs[1])>max_eid:
                        max_eid=int(segs[1])
            if nest_list!=[]:
                if len(nest_list)==1:
                    entity_list.append(nest_list[0])

                else:
                    tem=find_maxlen_entity_nest(nest_list)#find max entity
                    entity_list.extend(tem)
        else:
            entity_list=temp_result
        fout.write(pmid+'\n'+lines[1]+'\n')
        for ele in entity_list:
            fout.write('\t'.join(ele)+'\n')
        fout.write('\n')
    fout.close()
    
        

def GSCplus_corpus(prefile,goldfile,subtree=True):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')
    #fin_alt=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/alt_hpoid.json','r',encoding='utf-8')
    #fin_subtree=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/hpo_lable.vocab','r',encoding='utf-8')
    fin_alt=open('../dict/alt_hpoid.json','r',encoding='utf-8')
    fin_subtree=open('../dict/lable.vocab','r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_pre=fin_pre.read().strip().split('\n\n')
    all_gold=fin_gold.read().strip().split('\n\n')
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for doc_pre in all_pre:
        lines=doc_pre.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('pre hpo obo no this id:',lines[i],seg[3])
                
        pre_result[pmid]=temp_result
                
    for doc_gold in all_gold:
        lines=doc_gold.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('gold hpo obo no this id:',lines[i],seg[3])
        gold_result[pmid]=temp_result
    doc_f=document_metric(pre_result,gold_result)
    men_f=mention_metric_new(pre_result,gold_result)
    return doc_f+men_f

def GSCplus_corpus_hponew(prefile,goldfile,subtree=True):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')
    #fin_alt=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/alt_hpoid.json','r',encoding='utf-8')
    #fin_subtree=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/hpo_lable.vocab','r',encoding='utf-8')
    fin_alt=open('../dict_hponew/alt_hpoid.json','r',encoding='utf-8')
    fin_subtree=open('../dict_hponew/lable.vocab','r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_pre=fin_pre.read().strip().split('\n\n')
    all_gold=fin_gold.read().strip().split('\n\n')
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for doc_pre in all_pre:
        lines=doc_pre.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('pre hpo obo no this id:',lines[i],seg[3])

        pre_result[pmid]=temp_result

    for doc_gold in all_gold:
        lines=doc_gold.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('gold hpo obo no this id:',lines[i],seg[3])
        gold_result[pmid]=temp_result
    doc_f=document_metric(pre_result,gold_result)
    men_f=mention_metric_new(pre_result,gold_result)
    return doc_f+men_f

def GSCplus_corpus_sub(subfiles,prefile,goldfile,subtree=True):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')
    #fin_alt=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/alt_hpoid.json','r',encoding='utf-8')
    #fin_subtree=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/hpo_lable.vocab','r',encoding='utf-8')
    fin_alt=open(subfiles['alt_file'],'r',encoding='utf-8')
    fin_subtree=open(subfiles['subtree_file'],'r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_pre=fin_pre.read().strip().split('\n\n')
    all_gold=fin_gold.read().strip().split('\n\n')
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for doc_pre in all_pre:
        lines=doc_pre.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('pre hpo obo no this id:',lines[i],seg[3])

        pre_result[pmid]=temp_result

    for doc_gold in all_gold:
        lines=doc_gold.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            if seg[3] in alt_hpoid.keys():
                hpoid=alt_hpoid[seg[3]]
                if subtree==True:
                    if hpoid in subtree_list:
                        temp_result.append([seg[0],seg[1],hpoid])
                else:
                    temp_result.append([seg[0],seg[1],hpoid])
            else:
                print('gold hpo obo no this id:',lines[i],seg[3])
        gold_result[pmid]=temp_result
    doc_f=document_metric(pre_result,gold_result)
    men_f=mention_metric_new(pre_result,gold_result)
    return doc_f+men_f

def JAX_corpus(prefile,goldfile,subtree=True):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')
    #fin_alt=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/alt_hpoid.json','r',encoding='utf-8')
    #fin_subtree=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/hpo_lable.vocab','r',encoding='utf-8')
    fin_alt=open('../dict/alt_hpoid.json','r',encoding='utf-8')
    fin_subtree=open('../dict/lable.vocab','r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_pre=json.load(fin_pre)
    all_gold=json.load(fin_gold)
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for pmid in all_pre.keys():
        pre_temp_result=[]
        #for pre_hpoid in all_pre[pmid].keys():
        #    pre_hpoid=pre_hpoid.split('|')[0]
        for ele in all_pre[pmid]:
            pre_hpoid=ele[2].split('|')[0]
            if pre_hpoid in alt_hpoid.keys():
                hpoid=alt_hpoid[pre_hpoid]
                if subtree==True:
                    if hpoid in subtree_list:
                        pre_temp_result.append(['0','0',hpoid])
                else:
                    pre_temp_result.append(['0','0',hpoid])
            else:
                print('pre hpo obo no this id:',pre_hpoid)
           
        pre_result[pmid]=pre_temp_result
        
        gold_temp_result=[]
        for gold_hpoid in all_gold[pmid].keys():
            if gold_hpoid in alt_hpoid.keys():
                hpoid=alt_hpoid[gold_hpoid]
                if subtree==True:
                    if hpoid in subtree_list:
                        gold_temp_result.append(['0','0',hpoid])
                else:
                    gold_temp_result.append(['0','0',hpoid])
            else:
                print('pre hpo obo no this id:',gold_hpoid)
           
        gold_result[pmid]=gold_temp_result
        
    document_metric(pre_result,gold_result)

def JAX_corpus_hponew(prefile,goldfile,subtree=True):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')
    #fin_alt=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/alt_hpoid.json','r',encoding='utf-8')
    #fin_subtree=open('//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/evaluation/hpo_lable.vocab','r',encoding='utf-8')
    fin_alt=open('../dict_hponew/alt_hpoid.json','r',encoding='utf-8')
    fin_subtree=open('../dict_hponew/lable.vocab','r',encoding='utf-8')
    alt_hpoid=json.load(fin_alt)
    fin_alt.close()
    subtree_list=fin_subtree.read().strip().split('\n')
    fin_subtree.close()
    all_pre=json.load(fin_pre)
    all_gold=json.load(fin_gold)
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for pmid in all_pre.keys():
        pre_temp_result=[]
        #for pre_hpoid in all_pre[pmid].keys():
        #    pre_hpoid=pre_hpoid.split('|')[0]
        for ele in all_pre[pmid]:
            pre_hpoid=ele[2].split('|')[0]
            if pre_hpoid in alt_hpoid.keys():
                hpoid=alt_hpoid[pre_hpoid]
                if subtree==True:
                    if hpoid in subtree_list:
                        pre_temp_result.append(['0','0',hpoid])
                else:
                    pre_temp_result.append(['0','0',hpoid])
            else:
                print('pre hpo obo no this id:',pre_hpoid)
           
        pre_result[pmid]=pre_temp_result
        
        gold_temp_result=[]
        for gold_hpoid in all_gold[pmid].keys():
            if gold_hpoid in alt_hpoid.keys():
                hpoid=alt_hpoid[gold_hpoid]
                if subtree==True:
                    if hpoid in subtree_list:
                        gold_temp_result.append(['0','0',hpoid])
                else:
                    gold_temp_result.append(['0','0',hpoid])
            else:
                print('pre hpo obo no this id:',gold_hpoid)
           
        gold_result[pmid]=gold_temp_result
        
    document_metric(pre_result,gold_result)
        
def NCBI_corpus(prefile,goldfile):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')

    all_pre=fin_pre.read().strip().split('\n\n')
    all_gold=fin_gold.read().strip().split('\n\n')
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for doc_pre in all_pre:
        lines=doc_pre.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')            
            temp_result.append([seg[0],seg[1],seg[3]])

        pre_result[pmid]=temp_result
                
    for doc_gold in all_gold:
        lines=doc_gold.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            temp_result.append([seg[0],seg[1],seg[3]])

        gold_result[pmid]=temp_result
    doc_f=document_metric(pre_result,gold_result)
    #men_f=mention_metric_new(pre_result,gold_result)
    return doc_f
def general_corpus(prefile,goldfile):
    fin_pre=open(prefile,'r',encoding='utf-8')
    fin_gold=open(goldfile,'r',encoding='utf-8')

    all_pre=fin_pre.read().strip().split('\n\n')
    all_gold=fin_gold.read().strip().split('\n\n')
    fin_gold.close()
    fin_pre.close()
    pre_result={}
    gold_result={}
    for doc_pre in all_pre:
        lines=doc_pre.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')            
            temp_result.append([seg[0],seg[1],seg[3]])

        pre_result[pmid]=temp_result
                
    for doc_gold in all_gold:
        lines=doc_gold.split('\n')
        pmid=lines[0]
        temp_result=[]
        for i in range(2,len(lines)):
            seg=lines[i].split('\t')
            temp_result.append([seg[0],seg[1],seg[3]])

        gold_result[pmid]=temp_result
    doc_f=document_metric(pre_result,gold_result)
    men_f=mention_metric_new(pre_result,gold_result)
    return doc_f+men_f    
if __name__=='__main__':
#    alt_hpo()
    #GSCplus_corpus_gold()
    #path='//panfs/pan1/bionlp/lulab/luoling/HPO_project/diseaseTag/data/test/'
    #prefile=path+'NCBItestset.output'
    #goldfile=path+'NCBI_test_gold.tsv'
    #general_corpus(prefile,goldfile)
    #JAX_corpus('../results/jax_bioformer_95.tsv', '../data/corpus/JAX/JAX_gold.json')
    path='//panfs/pan1/bionlplab/luol2/HPO_project/PhenoTagger_v1.1/results/'
    GSCplus_corpus_hponew(path+'gsc_test_bioformer_95_nonest.tsv',path+'GSCplus_test_gold_nonest.tsv',subtree=True)
