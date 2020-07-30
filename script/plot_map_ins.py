#! /home/rdaneel/anaconda3/envs/FlatlandChallenge/bin/python3.6
# -*- coding: UTF-8 -*-

import csv
import logging
import os
from copy import deepcopy
from typing import AnyStr, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.pyplot import axis, tick_params, xticks


class MapInstance:
    def __init__(self):
        self.map_path = '/home/rdaneel/mapf_benchmark/mapf-map/random-32-32-20.map'
        self.agent_path = '/home/rdaneel/mapf_benchmark/scen-even/random-32-32-20-even-24.scen'
        self.start_pos_file = '/home/rdaneel/ECBS/script/map_start_pos.txt'
        self.goal_pos_file = '/home/rdaneel/ECBS/script/map_goal_pos.txt'
        self.num_of_agent = 80
        self.start_map = list()
        self.goal_map = list()
        self.height = -1
        self.width = -1

        with open(self.map_path, 'r', encoding='UTF-8') as fin:
            fin.readline()
            self.height = int(fin.readline().split()[-1])
            self.width = int(fin.readline().split()[-1])
            print(self.height, ' ', self.width)
            fin.readline()

            for _line in fin.readlines():
                tmp_list = list()
                for _pos in _line:
                    if _pos == '\n':
                        continue
                    tmp_list.append(_pos)

                self.start_map.append(tmp_list)

        self.goal_map = deepcopy(self.start_map)

        with open(self.agent_path, 'r', encoding='UTF-8') as fin:
            fin.readline()
            for ag_id in range(self.num_of_agent):
                ag_info = fin.readline().split('\t')
                if self.start_map[int(ag_info[5])][int(ag_info[4])] != '.':
                    if self.start_map[int(ag_info[5])][int(ag_info[4])] == '@':
                        logging.error('Hit obstacle at ({0}, {1})'.format(int(ag_info[5]), int(ag_info[4])))
                    elif int(self.start_map[int(ag_info[5])][int(ag_info[4])]) > 0:
                        logging.error('For {0} -> Occupied by {1} at ({2}, {3})'.format(
                            ag_id,
                            self.start_map[int(ag_info[5])][int(ag_info[4])], 
                            int(ag_info[5]), 
                            int(ag_info[4])))
                else:
                    self.start_map[int(ag_info[5])][int(ag_info[4])] = str(ag_id)

                if self.goal_map[int(ag_info[7])][int(ag_info[6])] != '.':
                    if self.goal_map[int(ag_info[7])][int(ag_info[6])] == '@':
                        logging.error('Hit obstacle at ({0}, {1})'.format(int(ag_info[7]), int(ag_info[6])))
                    elif int(self.goal_map[int(ag_info[7])][int(ag_info[6])]) < 0:
                        logging.error('For {0} -> Occupied by {1} at ({2}, {3})'.format(
                            ag_id,
                            self.goal_map[int(ag_info[7])][int(ag_info[6])], 
                            int(ag_info[7]), 
                            int(ag_info[6])))
                else:
                    self.goal_map[int(ag_info[7])][int(ag_info[6])] = str(-ag_id)

        with open(self.start_pos_file, 'w') as fout:
            csvWriter = csv.writer(fout, delimiter=',')
            csvWriter.writerows(self.start_map)

        with open(self.goal_pos_file, 'w') as fout:
            csvWriter = csv.writer(fout, delimiter=',')
            csvWriter.writerows(self.goal_map)


if __name__ == '__main__':
    map_ins = MapInstance()