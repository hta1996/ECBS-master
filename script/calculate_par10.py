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


t1=0
t2=0
with open("data.txt","r") as f:
    i=0
    for line in f:
        t=eval(line)
        if t>=300: t*=10
        if i%2==0:
            t1+=t
        else:
            t2+=t
        i+=1

print(t1/25,t2/25)
