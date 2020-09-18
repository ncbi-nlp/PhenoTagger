# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 20:08:30 2020

@author: luol2
"""

def combine_overlap(mention_list):
   
    entity_list=[]
    if len(mention_list)>2:
        
        first_entity=mention_list[0]
        nest_list=[first_entity]
        max_eid=int(first_entity[1])
        for i in range(1,len(mention_list)):
            segs=mention_list[i]
            if int(segs[0])> max_eid:
                if len(nest_list)==1:
                    entity_list.append(nest_list[0])
                    nest_list=[]
                    nest_list.append(segs)
                    if int(segs[1])>max_eid:
                        max_eid=int(segs[1])
                else:
                    tem=find_max_entity(nest_list)#find max entity
                    entity_list.append(tem)
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
                tem=find_max_entity(nest_list)#find max entity
                entity_list.append(tem)
    else:
        entity_list=mention_list
        
    return entity_list

def find_max_entity(nest_list):
    max_len=0
    max_entity=[]
    for i in range(0, len(nest_list)):
        length=int(nest_list[i][1])-int(nest_list[i][0])
        if length>max_len:
                max_len=length
                max_entity=nest_list[i]
    
    return max_entity