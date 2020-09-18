# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:41:54 2020

@author: luol2
"""

import io
import time
import numpy as np
def ml_intext(infile):
    fin=open(infile,'r',encoding='utf-8')
    alltexts=fin.read().strip().split('\n\n')
    fin.close()
    data_list=[]
    label_list=[]
    for sents in alltexts:
        lines=sents.split('\n')
        temp_sentece=[]
        label=lines[0].split('\t')[0]
        label_list.append(label)
        for i in range(1,len(lines)):
            seg=lines[i].split('\t')
            temp_sentece.append(seg)
        data_list.append(temp_sentece)
    return data_list,label_list
def ml_intext_fn(ml_input):
    fin=io.StringIO(ml_input)
    alltexts=fin.read().strip().split('\n\n')
    fin.close()
    data_list=[]
    label_list=[]
    for sents in alltexts:
        lines=sents.split('\n')
        temp_sentece=[]
        label=lines[0].split('\t')[0]
        label_list.append(label)
        for i in range(1,len(lines)):
            seg=lines[i].split('\t')
            temp_sentece.append(seg)
        data_list.append(temp_sentece)
    return data_list,label_list
def pun_filter(temp_entity):
    pun_list=[',','.','!',';',':','?','(',')','[',']','{','}']
    filter_flag=0
    for ele in temp_entity:
        if ele in pun_list:
            filter_flag=1
            break
    return filter_flag
def pos_filter(temp_pos,temp_entity):
    pos_list_l=['PRP']
    pos_list=['IN','DT','CC','O','MD','EX','POS','WDT','WP','WP$','WRB','TO','PRP$']
    verb_word=['is','are','was','were','had','have','has','be','been','also']
    filter_flag=0

    if (temp_entity[0] in verb_word) or (temp_entity[-1] in verb_word):
        filter_flag=1
    if (temp_pos[0] in pos_list) or (temp_pos[-1] in pos_list) or (temp_pos[0] in pos_list_l):
        filter_flag=1
    return filter_flag 
    
def build_ngram_testset_filted(conll_input,Ngram=8):

    fin_genia=io.StringIO(conll_input)
    fout_context=io.StringIO()
    fout_txt=io.StringIO()
   
    index_dict={}
    allentity=[]
    alltext=fin_genia.read().strip().split('\n\n')
    fin_genia.close()
    num_total=0
    for i in range(0,len(alltext)):
        
        lines=alltext[i].split('\n') 
        ori_txt=[]
        for ele in lines:
            seg=ele.split('\t')
            ori_txt.append(seg[0])
        fout_txt.write(' '.join(ori_txt)+'\n')

        if Ngram>len(lines):
            Ngram=len(lines)
        
        fout_context_list=[]
        temp_entity=[]
        temp_pos=[]
        for ngram in range(2,Ngram+1):
            if ngram==1:
                for j in range(0, len(lines)):                 
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            sid=m
                            eid=m
                            fout_context_list.append(lines[m]+'\tO\tB')
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])                            
                        else:
                            pass
    #                        print(sentence[m])
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]
                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]
            elif ngram==2:
                for j in range(0, len(lines)-1):                  
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            sid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        elif m==j+1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            eid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        else:
                            pass
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]
                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]
            else :
                for j in range(0, len(lines)-ngram+1):               
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            sid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        elif m>j and m<j+ngram-1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[2])
                        elif m==j+ngram-1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            eid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        else:
                            pass
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]

                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]

    return fout_context.getvalue(),fout_txt.getvalue(),index_dict

def build_all_ngram_testset_filted(conll_input,Ngram=8):

    fin_genia=io.StringIO(conll_input)
    fout_context=io.StringIO()
    fout_txt=io.StringIO()
   
    index_dict={}
    allentity=[]
    alltext=fin_genia.read().strip().split('\n\n')
    fin_genia.close()
    num_total=0
    for i in range(0,len(alltext)):
        
        lines=alltext[i].split('\n') 
        ori_txt=[]
        for ele in lines:
            seg=ele.split('\t')
            ori_txt.append(seg[0])
        fout_txt.write(' '.join(ori_txt)+'\n')

        if Ngram>len(lines):
            Ngram=len(lines)
        
        fout_context_list=[]
        temp_entity=[]
        temp_pos=[]
        for ngram in range(1,Ngram+1):
            if ngram==1:
                for j in range(0, len(lines)):                 
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            sid=m
                            eid=m
                            fout_context_list.append(lines[m]+'\tO\tB')
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])                            
                        else:
                            pass
    #                        print(sentence[m])
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]
                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]
            elif ngram==2:
                for j in range(0, len(lines)-1):                  
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            sid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        elif m==j+1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            eid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        else:
                            pass
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]
                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]
            else :
                for j in range(0, len(lines)-ngram+1):               
                    sid=0
                    eid=0
                    for m in range(0,len(lines)):
                        if m==j:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            sid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        elif m>j and m<j+ngram-1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[2])
                        elif m==j+ngram-1:
                            fout_context_list.append(lines[m]+'\tO\tB')
                            eid=m
                            temp_seg=lines[m].split('\t')
                            temp_entity.append(temp_seg[0])
                            temp_pos.append(temp_seg[3])
                        else:
                            pass
#                            fout_context_list.append(lines[m]+'\tO\tO')
                    
                    if pun_filter(temp_entity)==0 and pos_filter(temp_pos,temp_entity)==0:
                        num_total+=1
                        if ' '.join(temp_entity) not in allentity:
                            allentity.append(' '.join(temp_entity))
                        fout_context.write('HP:None\t'+' '.join(temp_entity)+'\n')
                        fout_context.write('\n'.join(fout_context_list)+'\n\n')
                        index_dict[str(num_total)]=[i,sid,eid]

                    temp_entity=[]
                    temp_pos=[]
                    fout_context_list=[]

    return fout_context.getvalue(),fout_txt.getvalue(),index_dict

def output_result(result,label_2_index,Top_N=5):

    fout=io.StringIO()
    hpo_label={}

    for key in label_2_index.keys():
        hpo_label[label_2_index[key]]=key


    for line in result:
        #Top_index=line.argsort()[-1*Top_N:][::-1]
        index_top_unsort=np.argpartition(line,-Top_N)[-Top_N:]
        values_top=line[index_top_unsort]
        Top_index=index_top_unsort[np.argsort(-values_top)]
        temp_list=[]
        for max_index in Top_index:
            hpo_id=hpo_label[max_index]
            hpo_id_value=round(line[max_index],5)
            temp_list.append(str(hpo_id)+'|'+str(hpo_id_value))
        fout.write('\t'.join(temp_list)+'\n')
        
    return fout.getvalue()

def decode_tsv(test_score, ml_input_index, ml_input_txt, T=0.8):
    
    fin_predict=io.StringIO(test_score)
    fin_text=io.StringIO(ml_input_txt)
    fout=io.StringIO()
    
    test_txt=fin_text.read().strip().split('\n')
    test_index=ml_input_index
    test_pre=fin_predict.read().strip().split('\n')
    
    fin_text.close()
    fin_predict.close()
    
    sent_result={}
    for i in range(0,len(test_pre)):
        seg_pre=test_pre[i].split('\t')[0].split('|')
        #print(seg_pre,T)
        if float(seg_pre[1])>T and seg_pre[0]!='HP:None':
            term_id=str(i+1)
            pre_result=[test_index[term_id][1],test_index[term_id][2],seg_pre[0],seg_pre[1]]
            sent_id=str(test_index[term_id][0])
            if sent_id not in sent_result.keys():
                sent_result[sent_id]=[pre_result]
            else:
                sent_result[sent_id].append(pre_result)
        
    for i in range(0,len(test_txt)):
        fout.write(test_txt[i]+'\n')
        if str(i) in sent_result.keys():
            temp_result={}
            for ele in sent_result[str(i)]:
                temp_line=str(ele[0])+'\t'+str(ele[1])+'\t'+' '.join(test_txt[i].split()[ele[0]:ele[1]+1])+'\t'+ele[2]+'\t'+ele[3]
                temp_result[temp_line]=[ele[0],ele[1]]
            if len(temp_result)>=1:
                temp_result=sorted(temp_result.items(), key=lambda d: (d[1][0],d[1][1]), reverse=False)
                for ent in temp_result:
                    fout.write(ent[0]+'\n')
        fout.write('\n')

    return fout.getvalue()
    
def score_filter(temp_entity,  T=0.1):

    result_list=[]
    for i in range(0,len(temp_entity)):
        if float (temp_entity[i][-1])>T:
            result_list.append(temp_entity[i])
    return(result_list)
def find_max_entity_nest(nest_list):
    temp_result_list={}
    for i in range(0, len(nest_list)):
        hpoid=nest_list[i][-2]
        score=float(nest_list[i][-1])
        if hpoid not in temp_result_list.keys():
            temp_result_list[hpoid]=nest_list[i]
        else:
            if score>float(temp_result_list[hpoid][-1]):
                temp_result_list[hpoid]=nest_list[i]
    new_list=[]
    for hpoid in temp_result_list.keys():
        new_list.append(temp_result_list[hpoid])
    return new_list
def duplicate_filter(temp_entity):
    result_list=[]
    if len(temp_entity)>1:                   
        first_entity=temp_entity[0]
        nest_list=[first_entity]
        max_eid=int(first_entity[1])
    
        for i in range(1,len(temp_entity)):
            segs=temp_entity[i]
            if int(segs[0])> max_eid:
                if len(nest_list)==1:
                    result_list.append(nest_list[0])
                    nest_list=[segs]
                    if int(segs[1])>max_eid:
                        max_eid=int(segs[1])
                else:
                    result_list.extend(find_max_entity_nest(nest_list))
                    nest_list=[segs]

                    if int(segs[1])>max_eid:
                        max_eid=int(segs[1])
                    
            else:
                nest_list.append(segs)
                if int(segs[1])>max_eid:
                    max_eid=int(segs[1])
        if nest_list!=[]:
            if len(nest_list)==1:
                result_list.append(nest_list[0])

            else:
                result_list.extend(find_max_entity_nest(nest_list))
    else:
        result_list=temp_entity
    return result_list
def combine_strategy(test_decode_temp, T=0.8):
    fin=io.StringIO(test_decode_temp)
    fout=io.StringIO()
    
    documents=fin.read().strip().split('\n\n')
    fin.close()
    
    for doc in documents:
        lines=doc.split('\n')
        context=lines[0]
        final_entity_list=[]
        if len(lines)>1:
            # all entity candidates
            temp_entity=[]
            for i in range(1,len(lines)):
                temp_entity.append(lines[i].split('\t'))
            #print('all entity condidates: ',len(temp_entity))
            
            # 将阈值低于T的候选过滤
            filter1=score_filter(temp_entity,T)
#            print('filter1:', len(filter1))
            filter2=duplicate_filter(filter1)  
            #print('filter2:', filter2)
            final_entity_list=filter2
            
        fout.write(context+'\n')
        for ele in final_entity_list:
            fout.write('\t'.join(ele)+'\n')
        fout.write('\n')
    
    return fout.getvalue() 


def model_predict(ml_input,nn_model,ml_input_txt,ml_input_index,Threshold):
    if nn_model.model_type=='cnn':
        test_set,test_label = ml_intext_fn(ml_input)
        test_x, test_y = nn_model.rep.represent_instances_all_feas(test_set,test_label,word_max_len=nn_model.hyper['sen_max'],char_max_len=nn_model.hyper['word_max'])
        input_test = []
    
        if nn_model.fea_dict['word'] == 1:
            input_test.append(test_x[0])
    
        if nn_model.fea_dict['char'] == 1:
            input_test.append(test_x[1])
    
        if nn_model.fea_dict['lemma'] == 1:
            input_test.append(test_x[2])
    
        if nn_model.fea_dict['pos'] == 1:
            input_test.append(test_x[3])
    
        test_pre = nn_model.model.predict(input_test,batch_size=256)
    
    elif nn_model.model_type=='bert':

        test_set,test_label = ml_intext_fn(ml_input)
        test_x,test_y=nn_model.rep.load_data(test_set,test_label,word_max_len=nn_model.maxlen)
        test_pre = nn_model.model.predict(test_x,batch_size=128)
    
    test_score=output_result(test_pre, nn_model.rep.label_2_index,Top_N=3)
    #print('test_score:',test_score)
    test_decode_temp=decode_tsv(test_score, ml_input_index, ml_input_txt,  T=Threshold)
    #print('decode_temp:\n',test_decode_temp)
    # test_pre_tsv=combine_strategy(test_decode_temp,T=Threshold) 
    return test_decode_temp

def model_predict_old(ml_input,nn_model,ml_input_txt,ml_input_index,Threshold):
    if nn_model.model_type=='cnn':
        test_set,test_label = ml_intext_fn(ml_input)
        test_x, test_y = nn_model.rep.represent_instances_all_feas(test_set,test_label,word_max_len=nn_model.hyper['sen_max'],char_max_len=nn_model.hyper['word_max'])
        input_test = []

        if nn_model.fea_dict['word'] == 1:
            input_test.append(test_x[0])

        if nn_model.fea_dict['char'] == 1:
            input_test.append(test_x[1])

        if nn_model.fea_dict['lemma'] == 1:
            input_test.append(test_x[2])

        if nn_model.fea_dict['pos'] == 1:
            input_test.append(test_x[3])

        test_pre = nn_model.model.predict(input_test,batch_size=256)

    elif nn_model.model_type=='bert':

        test_set,test_label = ml_intext_fn(ml_input)
        test_x,test_y=nn_model.rep.load_data(test_set,test_label,word_max_len=nn_model.maxlen)
        test_pre = nn_model.model.predict(test_x,batch_size=128)

    test_score=output_result(test_pre, nn_model.rep.label_2_index,Top_N=3)
    #print('test_score:',test_score)
    test_decode_temp=decode_tsv(test_score, ml_input_index, ml_input_txt,  T=0.0)
    #print('decode_temp:\n',test_decode_temp)
    test_pre_tsv=combine_strategy(test_decode_temp,T=Threshold) 
    return test_pre_tsv

def output_txt(ml_input_txt):
    fin_text=io.StringIO(ml_input_txt)
    fout=io.StringIO()

    test_txt=fin_text.read().strip().split('\n')

    fin_text.close()

    for i in range(0,len(test_txt)):
        fout.write(test_txt[i]+'\n')
        fout.write('\n')

    return fout.getvalue()

def ml_tagging(ssplit_token,ml_model,Threshold):
    ml_input, ml_input_txt,ml_input_index=build_ngram_testset_filted(ssplit_token)
    #print('ml_input:')
    #print(ml_input)
    if len(ml_input_index)>0:
        ml_pre_tsv=model_predict(ml_input,ml_model,ml_input_txt,ml_input_index,Threshold)
    else:
        ml_pre_tsv=output_txt(ml_input_txt)
    return ml_pre_tsv
    
def ml_tagging_allngram(ssplit_token,ml_model,Threshold):
    ml_input, ml_input_txt,ml_input_index=build_all_ngram_testset_filted(ssplit_token)
    #print('ml_input:')
    #print(ml_input)
    if len(ml_input_index)>0:
        ml_pre_tsv=model_predict_old(ml_input,ml_model,ml_input_txt,ml_input_index,Threshold)
    else:
        ml_pre_tsv=output_txt(ml_input_txt)
    return ml_pre_tsv
