#! /home/rdaneel/anaconda3/envs/FlatlandChallenge/bin/python3.6
# -*- coding: UTF-8 -*-

import argparse
import logging
import os
import sys
from functools import reduce
from typing import AnyStr, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.pyplot import axis, tick_params, xticks




with open("dataSol.txt","r") as f:
    i=0
    x=0
    y=0
    for line in f:
        if i==25:
            print(x*1./25)
            #print(y*1./25)
            x=0
            y=0
            i=0
        c=eval(line)
        if c>0:
            x+=1
        y+=c
        i+=1
    print(x*1./25)
    #print(y*1./25)
    
with open("dataTime.txt","r") as f:
    i=0
    x=0
    y=0
    for line in f:
        if i==25:
            #print(x*1./25)
            print(y*1./25)
            x=0
            y=0
            i=0
        c=eval(line)
        if c>0:
            x+=1
        y+=c
        i+=1
    #print(x*1./25)
    print(y*1./25)
exit()


a=[]
b=[]
c=[]
d=[]
plt.figure(figsize=(8,8))
with open("data75.txt","r") as f:
    i=0
    for line in f:
        t=eval(line)
        if i<25:
            a.append(t)
        elif i<50:
            b.append(t)
        elif i<75:
            c.append(t)
        else:
            d.append(t)
        i+=1
        
x=[]
y=[]
k=0
for i in range(len(a)):
    X=min(a[i],min(b[i],c[i]))
    if X<300 and d[i]<300:
        y.append(X)
        x.append(d[i])
        k=max(k,max(X,d[i]))

print(sum(x)*1./len(x))
print(sum(y)*1./len(y))


print(len(x))
plt.scatter(x,y)
plt.plot([0,k],[0,k])
LBsize=25
plt.ylabel("Baseline Runtime (s)",fontsize=LBsize)
plt.xlabel("ECBS+ML Runtime (s)",fontsize=LBsize)
plt.show()


