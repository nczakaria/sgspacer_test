import pandas as pd
import numpy as np
import datetime
import operator
import csv
import os

def cleanLocation(filename,idx):
    temp_list = []
    with open(filename, 'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            temp_list.append(row)

        temp_list.pop(0) #remove header values from list

    removeColumns = idx #remove first N elements in a list, only keep building info

    new_list = []
    for temp in temp_list:
        temp = [x.strip() for x in temp] #remove whitespace in each element

        #only keep values related to building ( #bldg 1,#floor 1,#time 1 (second))
        result = '' 
        for t in temp[removeColumns:]:
            result = result + ',' + str(t)
        result = result.strip(',,,') 
        result = result.split(",")

        new_list.append(result) 

    return new_list

def assignGroup_backup(item_list):
    offcampusloc_list = ['CREATE','HSSML','KVA','VENT','I3','RVRG','UH','CLIB','CELS']
    dormloc_list = ['YNCRC1','YNCRC2','YNCRC3','UT-BS','UHC-BS','E1','E2','E3','EA','AS4']

    new_list = []
    for val in item_list:
        checkOffCampus = any(item in val for item in offcampusloc_list)
        checkDorm = any(item in val for item in dormloc_list)

        groupstatus = "on-campus"
        if checkOffCampus:
            groupstatus = "left-campus"

        else:
            if checkDorm and (len(set(val[::3]))==1): #check every nth element (location) if they are all the same value
                groupstatus = "stay-in"

        new_list.append(groupstatus)

    return new_list

def assignGroup(item_list):
    group1 = ''
    group2 = ''

    offcampusloc_list = ['CREATE','HSSML','KVA','VENT','I3','RVRG','UH','CLIB','CELS']
    dormloc_list = ['YNCRC1','YNCRC2','YNCRC3','UT-BS','UHC-BS','E1','E2','E3','EA','AS4']

    new_list = []
    for val in item_list:
        checkOffCampus = any(item in val for item in offcampusloc_list)
        checkDorm = any(item in val for item in dormloc_list)

        group2 = 'others'
        if checkDorm and val[0] in dormloc_list:
            group2 = 'dorm'

        group1 = "active"
        if checkOffCampus:
            group1 = "in-the-wild"

        else:
            if checkDorm and (len(set(val[::3]))==1): #check every nth element (location) if they are all the same value
                group1 = "inactive"

        new_list.append(group1 + " (" + group2 +")")

    return new_list

def uniquePlaces(item_list,count):
    new_list = []
    for val in item_list:
        temp_list = val[::3]
        temp = set(temp_list)

        if count:
            new_list.append(len(list(temp)))
        else: 
            new_list.append(list(temp))

    return new_list

def totalTime(item_list):
    new_list = []
    for val in item_list:
        temp_list = val[2::3]
        temp = sum(int(t) for t in temp_list)
        new_list.append(temp)

    return new_list

def totalTimePlace(user_list,item_list):
    uniquePlaces_keys = uniquePlaces(item_list,False)

    new_list=[]
    for idx,val in enumerate(user_list):
        places_dict = dict.fromkeys(uniquePlaces_keys[idx],0)
        #print(places_dict,"...",val)

        plc = item_list[idx]
        temp_list = plc[::3]
        temp_list2 = plc[2::3]

        #print(temp_list,temp_list2)

        for index,t in enumerate(temp_list):
           places_dict[t] +=  int(temp_list2[index])

        new_list.append(places_dict.copy())

    return new_list

########read all user info
filename = "transitions_march_21_0800.csv"
id_list = pd.read_csv(filename)['clientmac'].tolist()
transition_list = pd.read_csv(filename)[' # of transitions'].tolist()

places_list = cleanLocation(filename,5)

group_list = assignGroup(places_list)

uniquePlaces_list = uniquePlaces(places_list,True)

totalTime_list = totalTime(places_list)

totalTimePlace_list = totalTimePlace(id_list,places_list)

# print('id:',id_list[4])
# print('transition:',transition_list[4])
# print('places:',places_list[4])
# print('group_list:',group_list[4])
# print('uniquePlaces:',uniquePlaces_list[4])
# print('totalTime:',totalTime_list[4])
# print('totalTimePlace:',totalTimePlace_list[4])

# ########process csv to display bubble chart -- groups of stay-in, on-campus, left-campus
with open('bubbleplot.csv', 'w', newline='') as newfile:
    wr = csv.writer(newfile)
    wr.writerow(("clientMac","group","transition","uniquePlaces","totalTime"))
    wr.writerows(zip(id_list,group_list,transition_list,uniquePlaces_list,totalTime_list))

# ########process csv to display tree map -- total time spent at different locations per person
with open('treemap.csv', 'w', newline='') as newfile:
    wr = csv.writer(newfile)
    wr.writerow(("name","parent","value"))
    for idx,val in enumerate(id_list):
        #wr.writerow((val,"",""))

        temp_dict = totalTimePlace_list[idx]
        for m, k in temp_dict.items(): 
            wr.writerow((m,val,k))
