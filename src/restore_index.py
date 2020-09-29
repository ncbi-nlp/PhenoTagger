# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:19:02 2020

@author: luol2
"""

import io
import sys
        
def restore_index_nest_fn(ori_text,file_pre):


    fin_pre=io.StringIO(file_pre)
    #print(file_pre)
    all_pre=fin_pre.read().strip().split('\n\n')
    fin_pre.close()
    #print(len(all_pre))
    
    new_sentence=''
    restore_result=[]
    
    sentence_ori=ori_text.lower().replace('``','" ')
    sentence_ori=sentence_ori.replace("''",'" ')
    for pre_i in range(0,len(all_pre)):
        pre_lines=all_pre[pre_i].split('\n')
        #print(pre_lines)
#        print(sentence_ori)
        if len(pre_lines)>1:
            #print(pre_lines)
            sentence_pre=pre_lines[0].lower().replace('``','"')
            sentence_pre=sentence_pre.replace("''",'"')
            sentence_pre=sentence_pre.split()
            pre_result=[]
            for i in range(1,len(pre_lines)):
                pre_result.append(pre_lines[i].split('\t'))
            
            restore_sid=0
            restore_eid=0
            each_word_id=[]
            
            for i in range(0,len(sentence_pre)):

                temp_id=sentence_ori.find(sentence_pre[i])
                if temp_id<0:
                    if sentence_pre[i].find('"')>=0:
                        temp_id = sentence_ori.find(sentence_pre[i].replace('"','" '))
                    else:
                        #print('ori:',sentence_ori)
                        print('resotr index error:',sentence_pre[i])
                new_sentence+=sentence_ori[0:temp_id]
                
                restore_sid=len(new_sentence)
                restore_eid=len(new_sentence)+len(sentence_pre[i])
                each_word_id.append([str(restore_sid),str(restore_eid)])
                new_sentence+=sentence_ori[temp_id:temp_id+len(sentence_pre[i])]
                sentence_ori=sentence_ori[temp_id+len(sentence_pre[i]):]
#            print('each_word:',each_word_id)    
            for pre_ele in pre_result:
                # if len(pre_ele)>4:
                #     temp_pre_result=[each_word_id[int(pre_ele[0])][0],each_word_id[int(pre_ele[1])][1],pre_ele[3].split('|')[0],pre_ele[4]]
                # else:
                #     temp_pre_result=[each_word_id[int(pre_ele[0])][0],each_word_id[int(pre_ele[1])][1],pre_ele[3].split('|')[0],'1.00']
                temp_pre_result=[each_word_id[int(pre_ele[0])][0],each_word_id[int(pre_ele[1])][1],pre_ele[3].split('|')[0],pre_ele[4]]
                if temp_pre_result not in restore_result:
                    restore_result.append(temp_pre_result)
        else:
            sentence_pre=pre_lines[0].lower().replace('``','"')
            sentence_pre=sentence_pre.replace("''",'"')
            sentence_pre=sentence_pre.split()
           
            for i in range(0,len(sentence_pre)):

                temp_id=sentence_ori.find(sentence_pre[i])
                if temp_id<0:
                    if sentence_pre[i].find('"')>=0:
                        temp_id = sentence_ori.find(sentence_pre[i].replace('"','" '))
                    else:
                        print('resotr index error:',sentence_pre[i])
                new_sentence+=sentence_ori[0:temp_id]
                new_sentence+=sentence_ori[temp_id:temp_id+len(sentence_pre[i])]
                sentence_ori=sentence_ori[temp_id+len(sentence_pre[i]):]
#    print('resotre:',restore_result)
    return restore_result

if __name__=='__main__':
    path='//panfs/pan1/bionlp/lulab/luoling/HPO_project/bioTag/data/test/gsc/result/'
    fin=open(path+'GSCplus_Nest_biobert.tsv','r',encoding='utf-8')
    fout=open(path+'GSCplus_Nest_restore_biobert.tsv','w',encoding='utf-8')
    all_context=fin.read().strip().split('\n\n\n\n')
    fin.close()
    file_num=0
    for doc in all_context:
        file_num+=1
        print('file_num:',file_num)
        doc_ele=doc.split('\n\n')
        first_line = doc_ele[0].split('\n')
        pmid=first_line[0]
        ori_text=first_line[1]
        pre_result='\n\n'.join(doc_ele[1:])
#        print('pmid:',pmid)
#        print('ori:',ori_text)
#        print('pre:',pre_result)
        final_result=restore_index_nest_fn(ori_text,pre_result)
        fout.write(pmid+'\n'+ori_text+'\n')
        for ele in final_result:
            fout.write('\t'.join(ele)+'\t'+ori_text[int(ele[0]):int(ele[1])]+'\n')
        fout.write('\n')
    fout.close()
