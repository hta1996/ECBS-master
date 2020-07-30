import numpy as np
import networkx as nx
import pylab
import time
import matplotlib.pyplot as plt
import random as rd
import gurobipy as grb
from itertools import permutations as PERM
from itertools import combinations as COMB


def printTime(BaselineTime1,BaselineTime2,BaselineTime3,MLTime,name):
    
    MLTime.sort()
    MLTime=[x/60 for x in MLTime]
    print(MLTime)
    MLTimeY=[i+1 for i in range(len(MLTime))]
    MLTime.append(5)
    MLTimeY.append(len(MLTime)-1)

    BaselineTime1.sort()
    BaselineTime1=[x/60 for x in BaselineTime1]
    BaselineTime1Y=[i+1 for i in range(len(BaselineTime1))]
    BaselineTime1.append(5)
    BaselineTime1Y.append(len(BaselineTime1)-1)
    
    BaselineTime2.sort()
    BaselineTime2=[x/60 for x in BaselineTime2]
    BaselineTime2Y=[i+1 for i in range(len(BaselineTime2))]
    BaselineTime2.append(5)
    BaselineTime2Y.append(len(BaselineTime2)-1)
    
    BaselineTime3.sort()
    BaselineTime3=[x/60 for x in BaselineTime3]
    BaselineTime3Y=[i+1 for i in range(len(BaselineTime3))]
    BaselineTime3.append(5)
    BaselineTime3Y.append(len(BaselineTime3)-1)

    print(len(MLTime))
    print(len(BaselineTime1))
    print(len(BaselineTime2))
    print(len(BaselineTime3))

    
    FTsize=20
    NBsize=15
    LBsize=25
    plt.figure(figsize=(8,7))

    #x=np.array((0,10,20,30,40,50,60))
    x=np.array((0,1,2,3,4,5))
    #t1=np.array((25.13953488/60,315.75/60,1245/60,2701.875/60))
    BaselineTime1Y=[x/25.*100 for x in BaselineTime1Y]
    plt.plot(BaselineTime1,BaselineTime1Y,'go-',mew=1,linewidth=1,label="Baseline1")
    
    
    BaselineTime2Y=[x/25.*100 for x in BaselineTime2Y]
    plt.plot(BaselineTime2,BaselineTime2Y,'r^-',mew=1,linewidth=1,label="Baseline2")
    
    BaselineTime3Y=[x/25.*100 for x in BaselineTime3Y]
    plt.plot(BaselineTime3,BaselineTime3Y,'b+-',mew=1,linewidth=1,label="Baseline3")
    #plt.errorbar(x,t1,yerr=te1/3,fmt='o',ecolor='g',color='g',elinewidth=2,capsize=4,alpha=0.5)
    MLTimeY=[x/25.*100 for x in MLTimeY]
    plt.plot(MLTime,MLTimeY,'y*-',mew=1,linewidth=1,label="ML-guided")
    #plt.errorbar(x-0.1,t2,yerr=te2/3,fmt='*',ecolor='y',color='y',elinewidth=2,capsize=4)

    #plt.plot(x,t3,'r+-',mew=1,linewidth=1,label="T-Sampling")
    #plt.errorbar(x,t3,yerr=te3/3,fmt='+',ecolor='r',color='r',elinewidth=2,capsize=4)

    #plt.plot(x,t4,'b^-',mew=1,linewidth=1,label="GSA")
    #plt.errorbar(x+0.1,t4,yerr=te4/3,fmt='^',ecolor='b',color='b',elinewidth=2,capsize=4)

    #y=np.array((0,2,4,6,8,10,12,14,16,18))
    plt.xticks(x,fontsize=NBsize)
    plt.yticks(fontsize=NBsize)
    plt.legend(fontsize=FTsize,bbox_to_anchor=(0.6,0.4))
    plt.xlabel("Runtime Limit (min)",fontsize=LBsize)
    plt.ylabel("Succes Rate (%)",fontsize=LBsize)
    plt.savefig(name)
    plt.show()
    
    

def printSuccessRate(a,b,c,d,name):
    FTsize=20
    NBsize=15
    LBsize=25
    plt.figure(figsize=(8,7))
    x=[75,80,85,90,95,100,105,110]
    x=np.array(x)
    #x=np.array((0,4500,9000,13500,18000,22500,27000))#large 100
    #x=np.array((0,15000,30000,45000,60000,75000))#dense17
    #x=np.array((0,14000,28000,42000,56000,70000))#dense 20
    #t1=np.array((25.13953488/60,315.75/60,1245/60,2701.875/60))

    plt.plot(x,a,'go-',mew=1,linewidth=1,label="Baseline1")
    plt.plot(x,b,'r^-',mew=1,linewidth=1,label="Baseline2")
    plt.plot(x,c,'b+-',mew=1,linewidth=1,label="Baseline3")


    #plt.errorbar(x,t1,yerr=te1/3,fmt='o',ecolor='g',color='g',elinewidth=2,capsize=4,alpha=0.5)

    plt.plot(x,d,'y*-',mew=1,linewidth=1,label="ML-guided")
    #x=[i for i in range(20,25)]
    #x=np.array(x)
    #plt.plot(x,MLnew,'r+-',mew=1,linewidth=1,label="ML-guided new")

    #plt.plot(x,MLcomb,'b^-',mew=1,linewidth=1,label="ML-guided comb")


    #plt.errorbar(x-0.1,t2,yerr=te2/3,fmt='*',ecolor='y',color='y',elinewidth=2,capsize=4)

    #plt.plot(x,t3,'r+-',mew=1,linewidth=1,label="T-Sampling")
    #plt.errorbar(x,t3,yerr=te3/3,fmt='+',ecolor='r',color='r',elinewidth=2,capsize=4)

    #plt.plot(x,t4,'b^-',mew=1,linewidth=1,label="GSA")
    #plt.errorbar(x+0.1,t4,yerr=te4/3,fmt='^',ecolor='b',color='b',elinewidth=2,capsize=4)


    plt.xticks(x,fontsize=NBsize)
    plt.yticks(fontsize=NBsize)
    plt.legend(fontsize=FTsize)
    plt.xlabel("#Agents",fontsize=LBsize)
    plt.ylabel("Success Rate (%)",fontsize=LBsize)
    plt.savefig(name+".png")
    plt.show()


a=[ 88,76,68,64,48,24,16,8]
b=[88,76,68,56,40,24,24,8]
c=[88,72,80,56,40,36,12,12]
d=[92,96,92,76,60,44,28,16]
printSuccessRate(a,b,c,d,"successRate")
exit()
    

a=[]
b=[]
c=[]
d=[]
g = (input("#Agents: "))
with open("data"+str(g)+".txt","r") as f:
    i=0
    for line in f:
        t=eval(line)
        if t>=300:
            i+=1
            continue
        if i<25:
            a.append(t)
        elif i<50:
            b.append(t)
        elif i<75:
            c.append(t)
        else:
            d.append(t)
        i+=1

printTime(a,b,c,d,"Cutoff"+str(g)+".png")
