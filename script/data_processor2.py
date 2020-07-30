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

class DataProcessor:
    def __init__(self, in_config):
        config_dict = dict()
        config_dict = os.path.join(os.path.dirname(os.path.realpath(__file__)), in_config)
        with open(config_dict, 'r') as fin:
            config_dict = yaml.load(fin, Loader=yaml.FullLoader)

        self.exp_dir = '/home/rdaneel/my_exp_hpc'
        self.ins_num = 25
        self.time_limit = 300

        # self.todo_function = config_dict['function']
        self.map_name: str = config_dict['map_name']
        self.scen_list: List[str] = list(config_dict['scen_dict'].keys())
        self.sid_dict: Dict[str, List[int]] = config_dict['scen_dict']
        self.focal_w: List[float] = config_dict['focal_w']
        self.num_of_agent: int = config_dict['num_of_agent']
        self.cbs_types: List[str] = config_dict['cbs_types']
        self.merge_th: List[int] = config_dict['merge_th']
        # self.map_list: List[str] = ['random-32-32-20', 'den520d','ost003d']
        self.map_list: List[str] = list()
        self.result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()

        self.num_list: List[int] = list()
        if 'num_list' in config_dict.keys():
            self.num_list = config_dict['num_list']
        else:
            self.num_list = range(10, 110, 10)

        # Plot parameters
        self.fig_h = 12
        self.fig_w = 8
        self.ms = 10
        self.lw = 1.5
        self.num_size = 14
        self.label_size = 16
        self.title_size = 18
        self.legend_size = 14
        self.colors = ['blue', 'purple', 'green', 'red', 'orange', 'brown', 'pink', 'grey', 'deepskyblue', 'cyan', 'yellowgreen', 'violet', 'magenta', 'olive', 'darkgreen', 'teal', 'darkorange', 'deeppink', 'gold', 'silver']
        self.marks = ['o', 's', 'D', 'X', '^', 'H', 'v', 'P', '1', '<', 'd', '*', '>', 'p', 'x', '8', '|', '1', '2', '3']
        self.tmp_tp = {
            (-1, 'CBS'): 0, 
            (-1, 'ECBS'): 1, 
            (1, 'MAECBS'): 2, 
            (10, 'MAECBS'): 3, 
            (25, 'MAECBS'): 4, 
            (1, 'MACBS_EPEA'): 5, 
            (10, 'MACBS_EPEA'): 6,
            (25, 'MACBS_EPEA'): 7,
            (1, 'MAECBS_EPEA'):8,
            (10, 'MAECBS_EPEA'):9,
            (25, 'MAECBS_EPEA'):10,
            (1, 'MACBS_EPEA_mr'): 11,
            (10, 'MACBS_EPEA_mr'): 12,
            (25, 'MACBS_EPEA_mr'): 13,
            (1, 'MAECBS_EPEA_mr'): 14,
            (10, 'MAECBS_EPEA_mr'): 15,
            (25, 'MAECBS_EPEA_mr'): 16,
            (1, 'MAECBS_mr'): 17,
            (10, 'MAECBS_mr'): 18,
            (25, 'MAECBS_mr'): 19}

    def checkValid(self, cbs_type, merge_th):
        if cbs_type == 'MACBS' and merge_th == -1:
            sys.exit('merge threshold should >= 0 for MACBS!!!')
        return

    def readFile(self, f_name: str):
        if os.path.exists(f_name):
            return pd.read_csv(f_name)
        else:
            logging.error('{0} does not exist!'.format(f_name))
            exit(1)

    def getFileDir(self, cbs_type, merge_th=-1, num_of_ag=None, in_map=None):
        if num_of_ag is None:
            num_of_ag = self.num_of_agent
        if in_map is None:
            in_map = self.map_name
        map_dir = os.path.join(self.exp_dir, in_map) 
        # out_dir = os.path.join(map_dir, 'a'+str(num_of_ag), cbs_type)
        out_dir = os.path.join(map_dir, cbs_type)

        # if cbs_type == 'MACBS' or cbs_type == 'MAECBS' or cbs_type == 'MACBS_EPEA':
        #     out_dir = os.path.join(out_dir, 'b'+str(merge_th))
        return out_dir

    def getFileName(self, scen_name, f_weight, cbs_type, sid=0, merge_th=-1, num_of_ag=None, in_map=None):
        self.checkValid(cbs_type, merge_th)
        if num_of_ag is None:
            num_of_ag = self.num_of_agent
        if in_map is None:
            in_map = self.map_name
        out_name =  in_map + '-' + scen_name + '-' + str(num_of_ag) + '-' + \
            '{0:.2f}'.format(f_weight) + '-' + str(sid)
        if cbs_type == 'ECBS':
            out_name = out_name + '-' + cbs_type + '.csv'
        elif cbs_type == 'CBS':
            out_name = out_name + '-' + cbs_type + '.csv'
        elif cbs_type == 'MACBS' or cbs_type == 'MAECBS' or cbs_type == 'MAECBS_mr' or cbs_type == 'MACBS_EPEA' or cbs_type == 'MACBS_mr' or cbs_type == 'MACBS_EPEA_mr' or cbs_type == 'MAECBS_EPEA' or 'MAECBS_EPEA_mr':
            out_name = out_name + '-' + str(merge_th) + '-' + cbs_type  + '.csv'
        return out_name

    def getCSVIns(self, scen_name, f_weight, cbs_type, sid=0, merge_th=-1, num_of_ag=None, in_map=None):
        return self.readFile(os.path.join(
            self.getFileDir(cbs_type, merge_th, num_of_ag, in_map),
            self.getFileName(scen_name, f_weight, cbs_type, sid, merge_th, num_of_ag, in_map)))

    def getIns(self, scen_name, f_weight, cbs_type, merge_th=-1):
        sid_list = self.sid_dict[scen_name]
        df = self.getCSVIns(scen_name, f_weight, cbs_type, min(sid_list), merge_th)
        tmp_key: Tuple[str, float, int, int, str] = (scen_name, f_weight, min(sid_list), merge_th, cbs_type)
        out_dict: Dict[Tuple[str, float, int, int, str], pd.Series] = {tmp_key: df['instance name']}
        
        for sid in sid_list:
            if sid > min(sid_list):
                tmp_df = self.getCSVIns(scen_name, f_weight, cbs_type, sid, merge_th)
                out_dict[(scen_name, f_weight, sid, merge_th, cbs_type)] = tmp_df['instance name']
                df = df.append(tmp_df, ignore_index=True)
        
        return df, out_dict

    def getInsByDF(self, f_ins, scen_name, f_weight, cbs_type, merge_th=-1):
        sid_list = self.sid_dict[scen_name]
        df = self.getCSVIns(scen_name, f_weight, cbs_type, min(sid_list), merge_th)
        cond = df['instance name'].isin(f_ins) == False
        df = df.drop(df[cond].index)
        
        for sid in sid_list:
            if sid > min(sid_list):
                tmp_df = self.getCSVIns(scen_name, f_weight, cbs_type, sid, merge_th)
                cond = tmp_df['instance name'].isin(f_ins) == False
                tmp_df = tmp_df.drop(tmp_df[cond].index)
                df = df.append(tmp_df, ignore_index=True)

        return df

    # def cal_iteration(self, cbs_type, focal_list, result):
    #     for fw in focal_list:
    #         if fw not in result.keys():
    #             result[fw]: Dict[Tuple[int, str], List[float]] = dict()

    #         for mth in self.merge_th:
    #             result[fw][(mth, cbs_type)] = {'num': list(), 'success': list()}
    #             for na in self.num_list:
    #                 success_num = 0
    #                 total_num = 0
    #                 for scen in self.scen_list:
    #                     for sid in self.sid_dict[scen]:
    #                         tmp_dir = self.getFileDir(cbs_type, mth, na)
    #                         tmp_file = self.getFileName(scen, fw, cbs_type, sid, mth, na)
                        
    #                         if os.path.exists(os.path.join(tmp_dir, tmp_file)):
    #                             tmp_df = self.getCSVIns(scen, fw, cbs_type, sid, mth, na)
                                
    #                             for _, row in tmp_df.iterrows():
    #                                 if 0 <= row['solution cost']:
    #                                     success_num += 1
    #                             total_num += tmp_df.shape[0]
                                
    #                             # if less than ins_num is save
    #                             if tmp_df.shape[0] < self.ins_num:
    #                                 remain_num = self.ins_num - tmp_df.shape[0]
    #                                 for _ in range(remain_num):
    #                                     total_num += 1
                                
    #                         else: 
    #                             total_num += self.ins_num

    #                 success_rate = success_num / total_num
    #                 result[fw][(mth, cbs_type)]['num'].append(na)
    #                 result[fw][(mth, cbs_type)]['success'].append(success_rate)



    def plot_num_success(self):
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        # num_list = range(10, 110, 10)
        num_list = range(50, 260, 50)
        num_list = list(num_list)

        for tp in self.cbs_types:
            if tp == 'MACBS':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]
                                        
                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'CBS':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in [-1]:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)


            if tp == 'MACBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)


            if tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            if tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)


            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in [-1]:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in num_list:
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                success_num += 1
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                total_num += 1
                                        
                                    else: 
                                        total_num += self.ins_num

                            success_rate = success_num / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)           

        for tp in self.cbs_types:
            if tp == 'MACBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = tp + '(CSB, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            if tp == 'CBS':
                for fw in [1.00]:
                    for mth in [-1]:
                        tmp_label = tp
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            if tp == 'MACBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            if tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            if tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'ECBS':
                for fw in self.focal_w:
                    for mth in [-1]:
                        tmp_label = tp
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xticks(num_list)
        plt.xlabel('#agents', fontsize=self.label_size)
        plt.yticks(np.arange(0, 105, 10))
        plt.ylabel('Success Rate (%)', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_success.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()


    def plot_num_runtime(self):
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        # num_list = range(10, 110, 10)
        num_list = range(50, 260, 50)
        num_list = list(num_list)
        
        for tp in self.cbs_types:
            if tp == 'CBS':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in [-1]:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)


            elif tp == 'ECBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in [-1]:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)


            elif tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            if 0 <= row['solution cost']:
                                                runtime += row['runtime']
                                            else:
                                                runtime += self.time_limit
                                        total_num += tmp_df.shape[0]

                                        # if less than ins_num is save
                                        if tmp_df.shape[0] < self.ins_num:
                                            remain_num = self.ins_num - tmp_df.shape[0]
                                            for _ in range(remain_num):
                                                runtime += self.time_limit
                                                total_num += 1
                                        
                                    else: 
                                        # logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                        # exit(1)
                                        runtime += self.time_limit * self.ins_num
                                        total_num += self.ins_num

                            y_val = runtime / total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)
                                    
        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)           

        for tp in self.cbs_types:
            if tp == 'CBS':
                for fw in [1]:
                    for mth in [-1]:
                        tmp_label = tp
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'ECBS':
                for fw in self.focal_w:
                    for mth in [-1]:
                        tmp_label = tp
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            if tp == 'MACBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (CBS, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            if tp == 'MACBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (CBS, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
                            
            if tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            if tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xticks(num_list)
        plt.xlabel('#agents', fontsize=self.label_size)
        plt.ylabel('Average Runtime (sec)', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_runtime.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return

    def plot_num_maxMA(self):
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        # num_list = range(10, 110, 10)
        num_list = range(50, 260, 50)
        num_list = list(num_list)

        for tp in self.cbs_types:

            if tp == 'MACBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    # else: 
                                    #     logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                    #     exit(1)

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    else: 
                                        total_num += self.ins_num

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    else: 
                                        total_num += self.ins_num
                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    else: 
                                        total_num += self.ins_num

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    # else: 
                                    #     logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                    #     exit(1)

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    # else: 
                                    #     logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                    #     exit(1)

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]
                                        
                                    # else: 
                                    #     logging.error("No such file: {0}".format(os.path.join(tmp_dir, tmp_file)))
                                    #     exit(1)

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)

            elif tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()

                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'x': list(), 'y': list()}
                        for na in num_list:
                            y_val = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        
                                        for _, row in tmp_df.iterrows():
                                            y_val += row['max MA']

                                        total_num += tmp_df.shape[0]

                            y_val /= total_num
                            result[fw][(mth, tp)]['x'].append(na)
                            result[fw][(mth, tp)]['y'].append(y_val)
                                    
        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)           

        for tp in self.cbs_types:
            if tp == 'MACBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (CBS, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            elif tp == 'MACBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (CBS, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            elif tp == 'MACBS_EPEA':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            elif tp == 'MACBS_EPEA_mr':
                for fw in [1.00]:
                    for mth in self.merge_th:
                        tmp_label = 'MACBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            elif tp == 'MAECBS_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (ECBS, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)
            
            elif tp == 'MAECBS_EPEA':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

            elif tp == 'MAECBS_EPEA_mr':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = 'MAECBS (EPEA, mr, b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['x'], result[fw][(mth, tp)]['y'], 
                            linewidth=self.lw, color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_label)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xticks(num_list)
        _, end = ax.get_ylim()
        plt.yticks(np.arange(0, np.ceil(end), 1))
        plt.xlabel('#agents', fontsize=self.label_size)
        plt.ylabel('Avg. Max MA size', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_maxMA.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Take config.yaml as input!')
    parser.add_argument('--config', type=str, default='config.yaml')
    args = parser.parse_args()

    dp = DataProcessor(args.config)
    dp.plot_num_success()
    dp.plot_num_runtime()
    dp.plot_num_maxMA()