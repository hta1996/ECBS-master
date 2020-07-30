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

w_warehouse=[[1.0097, 1.0187, 1.0254, 1.0283, 1.0253, 1.0228, 1.0217, 1.0215, 1.0197, 1.0191],  # 120 agents
    [1.0098, 1.0194, 1.0278, 1.0337, 1.0353, 1.0331, 1.0327, 1.0301, 1.0294, 1.0283],  # 140 agents
    [1.0098, 1.0198, 1.029, 1.037, 1.0392, 1.0368, 1.0356, 1.0341, 1.0326, 1.0329],  # 160 agents
    ['NaN', 'NaN', 1.0288, 1.0374, 1.0395, 1.04, 1.0376, 1.0384, 1.0362, 1.0364],  # 180 agents
    ['NaN', 'NaN', 'NaN', 1.0385, 1.0443, 1.0459, 1.0459, 1.0457, 1.0435, 1.0417],  # 200 agents
    ['NaN', 'NaN', 'NaN', 1.0388, 1.047, 1.0503, 1.052, 1.0514, 1.0481, 1.0468],  # 220 agents
    ['NaN', 'NaN', 'NaN', 'NaN', 1.0478, 1.0543, 1.0587, 1.0584, 1.0562, 1.0521],  # 240 agents
    ['NaN', 'NaN', 'NaN', 'NaN', 1.0493, 1.0583, 1.0624, 1.0643, 1.0614, 1.0615],  # 260 agents
    ['NaN', 'NaN', 'NaN', 'NaN', 'NaN', 1.0592, 1.0664, 1.0692, 1.0691, 1.0665],  # 280 agents
    ['NaN', 'NaN', 'NaN', 'NaN', 'NaN', 1.0598, 1.0681, 1.0739, 1.0751, 1.0741]]  # 300 agents]
for i in range(10):
    for j in range(10):
        if type(w_warehouse[i][j])==type("a"): continue
        w_warehouse[i][j]=1+(j+1)*0.01-w_warehouse[i][j]
        w_warehouse[i][j]=float("{:.4f}".format(w_warehouse[i][j]))
    print(w_warehouse[i])
#print(w_warehouse)
