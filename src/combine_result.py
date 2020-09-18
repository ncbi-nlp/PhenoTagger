# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:24:45 2020

@author: luol2
"""

import io
def nest_overlap_entity(nest_list):
    temp_result_list={}
    for i in range(0, len(nest_list)):
        hpoid=nest_list[i][3]
        if hpoid not in temp_result_list.keys():
            temp_result_list[hpoid]=nest_list[i]
        else:
            score=float(nest_list[i][4])
            old_score=float(temp_result_list[hpoid][4])
            if score>old_score: # retain higer score concept
                temp_result_list[hpoid]=nest_list[i]
    new_list=[]
    for hpoid in temp_result_list.keys():
        new_list.append(temp_result_list[hpoid])
    
    temp_result_list={} #same index, different ids
    for i in range(0, len(new_list)):
        ids=new_list[i][0]+' '+new_list[i][1]
        if ids not in temp_result_list.keys():
            temp_result_list[ids]=new_list[i]
        else:
            score=float(nest_list[i][4])
            old_score=float(temp_result_list[ids][4])
            if score>old_score: 
                temp_result_list[ids]=new_list[i]
    final_list=[]
    for ids in temp_result_list.keys():
        final_list.append(temp_result_list[ids]) 
    return final_list
def combine_ml_dict(dict_tsv,ml_tsv,nest=True):
    fin_dic=io.StringIO(dict_tsv)
    fin_ml=io.StringIO(ml_tsv)
    fout=io.StringIO()
    all_dic=fin_dic.read().strip().split('\n\n')
    all_ml=fin_ml.read().strip().split('\n\n')
    fin_dic.close()
    fin_ml.close()
    
    for i in range(0,len(all_dic)):
        lines_dic=all_dic[i].split('\n')
        lines_ml=all_ml[i].split('\n')
        entity_list={}
        for j in range(1,len(lines_dic)):
            seg=lines_dic[j].split('\t')
            entity_list[lines_dic[j]]=[int(seg[0]),int(seg[1])] #dict results score 1.00
        for j in range(1,len(lines_ml)):
            seg=lines_ml[j].split('\t')
            entity_list[lines_ml[j]]=[int(seg[0]),int(seg[1])]
                
        entity_list=sorted(entity_list.items(), key=lambda kv:(kv[1]), reverse=False)
        entity_list_sort=[]
        for ele in entity_list:
            entity_list_sort.append(ele[0])
        
        final_entity=[]
        if len(entity_list_sort)!=0:
            first_entity=entity_list_sort[0].split('\t')
            nest_list=[first_entity]
            max_eid=int(first_entity[1])

            for i in range(1,len(entity_list_sort)):
                segs=entity_list_sort[i].split('\t')
                if int(segs[0])> max_eid:
                    if len(nest_list)==1:
                        final_entity.append(nest_list[0])
                        nest_list=[]
                        nest_list.append(segs)
                        if int(segs[1])>max_eid:
                            max_eid=int(segs[1])
                    else:
                        tem=nest_overlap_entity(nest_list)
                        final_entity.extend(tem)
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
                    final_entity.append(nest_list[0])

                else:
                    tem=nest_overlap_entity(nest_list)#find max entity
                    final_entity.extend(tem)
        
        fout.write(lines_ml[0]+'\n')
        for ele in final_entity:
            fout.write('\t'.join(ele)+'\n')
        fout.write('\n')
    return fout.getvalue()  
                
