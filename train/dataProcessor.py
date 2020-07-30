#import gurobipy as grb
#import numpy as np
#import networkx as nx
import matplotlib.pyplot as plt
from random import sample
import math
import random
#import osmnx as ox
#import shapefile
import csv
#import fiona
import sys
import os
#import matplotlib.lines as mlines

filename="featureMix_"

FT=2

def relabel(data):
    return data
    score=[]
    datanew=[]
    for t in data:
        score.append(eval(t[FT-1]))
    score.sort(reverse=True)
    tp=int(len(score)/10)
    tpj=tp+1
    while tpj<len(score):
        if score[tpj]!=score[tp]: break
        tpj+=1
    if tpj*1./len(score)>=0.2:
        tpk=tp
        while tp>0:
            if score[tpk]!=score[tp]: break
            tp-=1
    for t in data:
        s=t
        if eval(s[FT-1])+1e-8>=score[tp]:
            s[0]="1"
        else:
            s[0]="0"
        datanew.append(s)
    return datanew

def printdata(t,count,f):
    c0=[]
    c1=[]
    for s in t:
        ratio=eval(s[0])
        dis=eval(s[1])
        score=int(dis*1000+(ratio-1)*1000)
        if score>1e9:
            c1.append(s)
        else:
            c0.append(s)
    
    if len(c0)*9<len(c1):
        random.shuffle(c1)
        c1=c1[:len(c0)*9]

    t=c0+c1
    
    cc0=0
    cc1=0
    for s in t:
        ratio=eval(s[0])
        dis=eval(s[1])
        score=int(dis*1000+(ratio-1)*1000)
        if score>1e9:
            score=1e9
            cc1+=1
        else:
            if dis<10:
                score=0
            elif dis<30:
                score=1
            elif dis<60:
                score=2
            else:
                score=3
            cc0+=1
        f.write(str(score)+" qid:"+str(count)+" ")
        ss=s[FT:]
        for i in range(len(ss)-1):
            f.write(str(i+1)+":"+ss[i]+" ")
        f.write("\n")
    print(cc0*1./(cc1+cc0+0.0001))
'''

data=[]
fileIndex=[x for x in range(0,50)]
random.shuffle(fileIndex)
for i in range(20):
    datap=[]
    FullFilename=filename+str(fileIndex[i])+".txt";
    if fileIndex[i]<10:
        FullFilename=filename+"0"+str(fileIndex[i])+".txt";
    with open(FullFilename,'r') as f:
        countd=0
        for line in f:
            t=[x for x in line.split(' ')]
            if len(t)<2:
                if notAllSame(datap):
                    relabel(datap)
                    data.append(datap)
                    #countd+=1
                datap=[]
                if countd>=500: break
                continue
            datap.append(t)
    if len(datap)>0 and countd<500:
        if notAllSame(datap):
            relabel(datap)
            data.append(datap)
        datap=[]
L=4000
random.shuffle(data)
print(len(data))
traindata=data[:]
if len(data)>L:
    traindata=data[:L]
count=0

with open(filename+"train.txt",'w') as f:
    for i in traindata:
        count+=1
        tt=normalize(i)
        printdata(tt,count,f)
'''

    
    



RunEcbs0="./../build/ECBS -m ../instances/mapf-map/random-32-32-20.map -a ../instances/scen-random/random-32-32-20-random-"
TestEcbs0="./../build/ECBS -m ../instances/mapf-map/random-32-32-20.map -a ../instances/scen-random/random-32-32-20-random-"

RunEcbs1=".scen -n "
RunEcbs2=" -o tmp.csv -t 300 -w 1.1 -s 2 --featFile "
TestEcbs2=" -o base3_%d_1.1.csv -t 300 --testing 1 -w 1.1 -s 2 "

'''
for i in range(11):
    TestCommand="./svm_rank_classify feature_train.txt model"+str(i)+""
    os.system(TestCommand)
exit()
'''
'''
for scen in range(25):
    featName="feature_"+str(scen+1)+"_"+str(15)+"_"+str(85)+".txt"
    featFile="../train/TRAIN"+str(N)+"/"+featName
    weightFile=" --weightFile ../train/TRAIN"+str(N)+"/model"+str(14)+"_coef.txt"
    RunEcbs=RunEcbs0+str(scen+1)+RunEcbs1+str(85)+RunEcbs2+featFile+weightFile
    os.system(RunEcbs)

exit()
'''
'''
num_of_agent=[105,110,115]
for N in num_of_agent:
    for scen in range(25):
        weightFile=" --weightFile ../train/model9_coef.txt"
        RunEcbs=(TestEcbs0+str(scen+1)+RunEcbs1+str(N)+TestEcbs2)%(N)
        os.system(RunEcbs)
        RunEcbs+=weightFile
        #print(RunEcbs)
        #os.system(RunEcbs)
exit()

TestEcbs2=" -o test_%d_bestAUC_1.1.csv -t 300 --testing 1 -w 1.1 -s 2 "
'''
'''
num_of_agent=[75,80,85,90,95,100]
for N in num_of_agent:
    for scen in range(25):
        weightFile=" --weightFile ../train/model8_coef.txt"
        RunEcbs=(TestEcbs0+str(scen+1)+RunEcbs1+str(N)+TestEcbs2)%(N)
        #os.system(RunEcbs)
        RunEcbs+=weightFile
        print(RunEcbs)
        os.system(RunEcbs)
TestEcbs2=" -o test_%d_last_1.1.csv -t 300 --testing 1 -w 1.1 -s 2 "


num_of_agent=[95,100]
for N in num_of_agent:
    for scen in range(25):
        weightFile=" --weightFile ../train/model12_coef.txt"
        RunEcbs=(TestEcbs0+str(scen+1)+RunEcbs1+str(N)+TestEcbs2)%(N)
        #os.system(RunEcbs)
        RunEcbs+=weightFile
        print(RunEcbs)
        os.system(RunEcbs)

exit()
'''


with open("feature_train.txt",'w') as f:
    f.close()
Iter=0
count=1


N=75
os.system("mkdir TRAIN"+str(N))
os.system("cd TRAIN"+str(N))

#initWeightFile=" --weightFile ../train/TRAIN+"+str(N)+"/model_prev.txt"
initWeightFile=""
for _ in range(15): #rounds of iterations
    for scen in range(25):
        for n in range(1):
            Scen=scen+1
            #N=n*10+70
            featName="feature_"+str(Scen)+"_"+str(_)+"_"+str(N)+".txt"
            featFile="../train/TRAIN+"+str(N)+"/"+featName
            #if _==0 and scen==0 and n==0:
            if _==0:
                weightFile=initWeightFile
            else:
                weightFile=" --weightFile ../train/TRAIN+"+str(N)+"/model"+str(_-1)+"_coef.txt"
            RunEcbs=RunEcbs0+str(Scen)+RunEcbs1+str(N)+RunEcbs2+featFile+weightFile
            print(RunEcbs)
            #if _>0:
            os.system(RunEcbs)
            datap=[]
            with open(featName,'r') as f:
                countd=0
                for line in f:
                    t=[x for x in line.split(' ')]
                    if len(t)<2:
                        relabel(datap)
                        #countd+=1
                        break
                    datap.append(t)
            
            with open("feature_train.txt",'a+') as f:
                printdata(datap,count,f)
            count+=1
            Iter+=1
    TrainCommand="./svm_rank_learn -c 10 -t 0 -e 0.01 -d 2 -s 1 -r 1 -l 2 feature_train.txt model"+str(_)
    TestCommand="./svm_rank_classify feature_train.txt model"+str(_)+" predictions"
    os.system(TrainCommand)
    os.system(TestCommand)

    
    coef=dict()
    for i in range(1000):
        coef[i]=0
    len_coef=0
    with open("model"+str(_),"r") as f:
        countl=0
        for line in f:
            countl+=1
            if countl<12:continue
            t=line.split()
            for i in range(len(t)-2):
                a,b=[eval(x) for x in t[i+1].split(':')]
                coef[a]=b
                len_coef=max(a,len_coef)
    with open("model"+str(_)+"_coef.txt","w") as f:
        for i in range(len_coef):
            f.write("%.8lf "%(coef[i+1]))
            print(coef[i+1]," ")

exit()
num_of_agent=[75,80,85,90,95]
for N in num_of_agent:
    for scen in range(25):
        weightFile=" --weightFile ../train/model9_coef.txt"
        RunEcbs=(TestEcbs0+str(scen+1)+RunEcbs1+str(N)+TestEcbs2)%(N)
        print(RunEcbs)
        #os.system(RunEcbs)
        RunEcbs+=weightFile
        os.system(RunEcbs)
exit()
        
for N in num_of_agent:
    for scen in range(25):
        weightFile=" --weightFile ../train/model14_coef.txt"
        RunEcbs=(TestEcbs0+str(scen+1)+RunEcbs1+str(N)+TestEcbs2)%(N+1)
        print(RunEcbs)
        #os.system(RunEcbs)
        RunEcbs+=weightFile
        os.system(RunEcbs)
exit()


'''

data=[]
for i in range(50,65):
    datap=[]
    with open(filename+str(i)+".txt",'r') as f:
        for line in f:
            t=[x for x in line.split(' ')]
            if len(t)<2:
                if notAllSame(datap):
                    #relabel(datap)
                    data.append(datap)
                datap=[]
                continue
            datap.append(t)
    if len(datap)>0:
        if notAllSame(datap):
            #relabel(datap)
            data.append(datap)




print(len(data))
testdata=data[:]
count=0


with open(filename+"test.txt",'w') as f:
    for i in testdata:
        count+=1
        tt=normalize(i)
        printdata(tt,count,f)

'''


exit()

for i in range(10):
    datap=[]
    with open(filename+str(i)+".txt",'r') as f:
        for line in f:
            t=[x for x in line.split(' ')]
            if len(t)<2:
                data.append(datap)
                datap=[]
                continue
            datap.append(t)
    if len(datap)>0:
        data.append(datap)



splitFeat=int(len(data)*0.6)
random.shuffle(data)

print(len(data))

Ttest=1000;

if splitFeat>Ttest:
    splitFeat=Ttest

traindata=data[:splitFeat]
testdata=data[splitFeat:]

count=0


    
with open(filename+"train.txt",'w') as f:
    for i in traindata:
        count+=1
        printdata(i,count,f)

with open(filename+"test.txt",'w') as f:
    for i in testdata:
        count+=1
        printdata(i,count,f)

