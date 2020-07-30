#! /home/rdaneel/anaconda3/envs/FlatlandChallenge/bin/python3.6
# -*- coding: UTF-8 -*-

import argparse
import logging
import os
import sys
from functools import reduce
from operator import index
from os.path import split
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
        # self.exp_dir2 = '/home/rdaneel/my_exp_hpc/sConf1'
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
        self.y_val = 0
        self.total_num = 0
        self.plot_common = config_dict['plot_common']

        self.num_list: List[int] = list()
        if 'num_list' in config_dict.keys():
            self.num_list = config_dict['num_list']
        else:
            self.num_list = range(10, 110, 10)


        
        self.opt_list = ['CBS', 'MACBS_EPEA', 'MACBS_EPEA_mr', 'MACBS', 'MACBS_mr']
        self.subopt_list = ['ECBS', 'ECBS1', 'ECBS_rt5', 'ECBS1_rt5', 'MAECBS_EPEA', 'MAECBS_EPEA_mr', 'MAECBS', 'MAECBS_mr', 
            'MAECBS_mr1', 'MAECBS_mrr1', 'MAECBS_mrr0', 'MAECBS_ro', 'MAECBS_ro1', 'MAECBS_ro_rt5']
        self.ma_list = ['MACBS_EPEA', 'MACBS_EPEA_mr', 'MACBS', 'MACBS_mr', 'MAECBS_EPEA', 'MAECBS_EPEA_mr', 'MAECBS', 
            'MAECBS_mr', 'MAECBS_mr1', 'MAECBS_mrr1', 'MAECBS_mrr0', 'MAECBS_ro', 'MAECBS_ro1', 'MAECBS_ro_rt5']

        self.common_ins = self.get_common_ins()

        # Plot parameters
        self.fig_h = 8
        self.fig_w = 6
        self.ms = 10
        self.lw = 1.5
        self.num_size = 14
        self.label_size = 16
        self.title_size = 18
        self.legend_size = 14
        self.colors = ['blue', 'purple', 'green', 'red', 'orange', 'brown', 'pink', 'grey', 'deepskyblue', 'cyan', 
            'yellowgreen', 'violet', 'magenta', 'olive', 'darkgreen', 'teal', 'darkorange', 'deeppink', 'gold', 'silver']
        self.marks = ['o', 's', 'D', 'X', '^', 'H', 'v', 'P', '1', '<', 'd', '*', '>', 'p', 'x', '8', '|', '1', '2', '3']
        
        self.tmp_tp = {
            (self.focal_w[0], -1, 'ECBS'): 0,
            (self.focal_w[0], 1, 'MAECBS'): 2,
            (self.focal_w[0], 25, 'MAECBS'): 3,
            (self.focal_w[0], 50, 'MAECBS'): 4,
            (self.focal_w[0], 100, 'MAECBS'): 5,
            (self.focal_w[0], 150, 'MAECBS'): 6,
            (self.focal_w[0], 1, 'MAECBS_EPEA'): 2,
            (self.focal_w[0], 25, 'MAECBS_EPEA'): 3,
            (self.focal_w[0], 50, 'MAECBS_EPEA'): 4,
            (self.focal_w[0], 100, 'MAECBS_EPEA'): 5,
            (self.focal_w[0], 150, 'MAECBS_EPEA'): 6,
        }

        # self.tmp_tp = {
        #     (self.focal_w[0], 25, 'MAECBS_mrr0'): 3,
        #     (self.focal_w[1], 25, 'MAECBS_mrr0'): 4,
        #     (self.focal_w[2], 25, 'MAECBS_mrr0'): 5,
        #     (self.focal_w[3], 25, 'MAECBS_mrr0'): 6,
        #     (self.focal_w[4], 25, 'MAECBS_mrr0'): 7
        # }

        # self.tmp_tp = {
        #     (self.focal_w[0], 25, 'MAECBS'): 3,
        #     (self.focal_w[1], 25, 'MAECBS'): 4,
        #     (self.focal_w[2], 25, 'MAECBS'): 5,
        #     (self.focal_w[3], 25, 'MAECBS'): 6,
        #     (self.focal_w[4], 25, 'MAECBS'): 7,
        # }

        # self.tmp_tp = {
        #     (self.focal_w[0], -1, 'CBS'): 0, 
        #     (self.focal_w[0], -1, 'ECBS'): 1, 
        #     (self.focal_w[0], 1, 'MAECBS'): 2, 
        #     (self.focal_w[0], 10, 'MAECBS'): 3, 
        #     (self.focal_w[0], 25, 'MAECBS'): 4, 
        #     (self.focal_w[0], 1, 'MACBS_EPEA'): 5, 
        #     (self.focal_w[0], 10, 'MACBS_EPEA'): 6,
        #     (self.focal_w[0], 25, 'MACBS_EPEA'): 7,
        #     (self.focal_w[0], 1, 'MAECBS_EPEA'):8,
        #     (self.focal_w[0], 10, 'MAECBS_EPEA'):9,
        #     (self.focal_w[0], 25, 'MAECBS_EPEA'):10,
        #     (self.focal_w[0], 1, 'MACBS_EPEA_mr'): 11,
        #     (self.focal_w[0], 10, 'MACBS_EPEA_mr'): 12,
        #     (self.focal_w[0], 25, 'MACBS_EPEA_mr'): 13,
        #     (self.focal_w[0], 1, 'MAECBS_EPEA_mr'): 14,
        #     (self.focal_w[0], 10, 'MAECBS_EPEA_mr'): 15,
        #     (self.focal_w[0], 25, 'MAECBS_EPEA_mr'): 16,
        #     (self.focal_w[0], 1, 'MAECBS_mr'): 17,
        #     (self.focal_w[0], 10, 'MAECBS_mr'): 18,
        #     (self.focal_w[0], 25, 'MAECBS_mr'): 19}

        # self.tmp_tp = {
        #     (self.focal_w[0], 10, 'MAECBS'): 1, 
        #     (self.focal_w[1], 10, 'MAECBS'): 2, 
        #     (self.focal_w[2], 10, 'MAECBS'): 3, 
        # }

        # self.tmp_tp = {
        #     (1.00, -1, 'CBS'): 0, 
        #     (self.focal_w[0], -1, 'ECBS'): 1, 
        #     (1.00, 1, 'MACBS_EPEA'): 2, 
        #     (1.00, 10, 'MACBS_EPEA'): 3, 
        #     (1.00, 25, 'MACBS_EPEA'): 4,
        #     (1.00, 50, 'MACBS_EPEA'): 5, 
        #     (1.00, 100, 'MACBS_EPEA'): 6,
        #     (self.focal_w[0], 1, 'MAECBS_mr'): 7, 
        #     (self.focal_w[0], 10, 'MAECBS_mr'): 8, 
        #     (self.focal_w[0], 25, 'MAECBS_mr'): 9,
        #     (self.focal_w[0], 50, 'MAECBS_mr'): 10, 
        #     (self.focal_w[0], 100, 'MAECBS_mr'): 11}

        # self.tmp_tp = {
        #     (self.focal_w[0], -1, 'CBS'): 0, 
        #     (self.focal_w[0], -1, 'ECBS'): 1, 
        #     (self.focal_w[0], 1, 'MAECBS_EPEA'): 2, 
        #     (self.focal_w[0], 10, 'MAECBS_EPEA'): 3, 
        #     (self.focal_w[0], 25, 'MAECBS_EPEA'): 4,
        #     (self.focal_w[0], 50, 'MAECBS_EPEA'): 5, 
        #     (self.focal_w[0], 100, 'MAECBS_EPEA'): 6,
        #     (self.focal_w[0], 1, 'MAECBS_mrr0'): 7, 
        #     (self.focal_w[0], 10, 'MAECBS_mrr0'): 8, 
        #     (self.focal_w[0], 25, 'MAECBS_mrr0'): 9,
        #     (self.focal_w[0], 50, 'MAECBS_mrr0'): 10, 
        #     (self.focal_w[0], 100, 'MAECBS_mrr0'): 11,
        #     (self.focal_w[0], 125, 'MAECBS_mrr0'): 12,
        #     (self.focal_w[0], 150, 'MAECBS_mrr0'): 13}

        # self.tmp_tp = {
        #     (self.focal_w[0], -1, 'ECBS'): 0, 
        #     (self.focal_w[0], -1, 'ECBS_rt5'): 1, 
        #     (self.focal_w[0], 25, 'MAECBS'): 4,
        #     (self.focal_w[0], 100, 'MAECBS'): 6,
        #     (self.focal_w[0], 25, 'MAECBS_mrr0'): 9,
        #     (self.focal_w[0], 100, 'MAECBS_mrr0'): 11,
        #     (self.focal_w[0], 125, 'MAECBS_mrr0'): 15,
        #     (self.focal_w[0], 150, 'MAECBS_mrr0'): 10,
        #     (self.focal_w[0], 25, 'MAECBS_mr'): 12,
        #     (self.focal_w[0], 100, 'MAECBS_mr'): 13,
        #     (self.focal_w[0], 25, 'MAECBS_ro_rt5'): 14,
        #     (self.focal_w[0], 100, 'MAECBS_ro_rt5'): 16,
        #     (self.focal_w[0], 25, 'MAECBS_ro'): 17,
        #     (self.focal_w[0], 100, 'MAECBS_ro'): 18,
        #     (self.focal_w[0], 125, 'MAECBS_ro'): 2,
        #     (self.focal_w[0], 150, 'MAECBS_ro'): 3
        #     }

        # self.tmp_tp = {
        #     (self.focal_w[0], -1, 'ECBS'): 1,
        #     (self.focal_w[0], 100, 'MAECBS_EPEA'): 6,
        #     (self.focal_w[0], 100, 'MAECBS_EPEA_mr'): 11,
        #     (self.focal_w[0], 10, 'MAECBS'): 3,
        #     (self.focal_w[0], 10, 'MAECBS_mr'): 8
        # }

        # self.tmp_tp = {
        #     (self.focal_w[0], -1, 'ECBS'): 1, 
        #     (self.focal_w[0], -1, 'ECBS_rt5'): 11,
        #     (self.focal_w[0], self.merge_th[0], 'MAECBS_mrr0'): 7,
        #     (self.focal_w[0], self.merge_th[0], 'MAECBS'): 8,
        #     (self.focal_w[0], self.merge_th[0], 'MAECBS_ro'): 9
        # }

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
        out_dir = os.path.join(map_dir, cbs_type)

        return out_dir

    def getFileName(self, scen_name, f_weight, cbs_type, sid=0, merge_th=-1, num_of_ag=None, in_map=None):
        self.checkValid(cbs_type, merge_th)
        if num_of_ag is None:
            num_of_ag = self.num_of_agent
        if in_map is None:
            in_map = self.map_name
        out_name =  in_map + '-' + scen_name + '-' + str(num_of_ag) + '-' + \
            '{0:.2f}'.format(f_weight) + '-' + str(sid)
        if cbs_type == 'ECBS' or cbs_type == 'ECBS1' or cbs_type == 'ECBS_rt5' or cbs_type == 'ECBS1_rt5':
            out_name = out_name + '-' + cbs_type + '.csv'
        elif cbs_type == 'CBS':
            out_name = out_name + '-' + cbs_type + '.csv'
        elif cbs_type in self.ma_list:
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


    def cal_iteration(self, cbs_type, focal_list, mth_list, in_mode):
        for fw in focal_list:
            if fw not in self.result.keys():
                self.result[fw]: Dict[Tuple[int, str], List[float]] = dict()

            for mth in mth_list:
                self.result[fw][(mth, cbs_type)] = {'x': list(), 'y': list()}
                for na in self.num_list:
                    self.y_val = 0
                    self.total_num = 0
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_dir = self.getFileDir(cbs_type, mth, na)
                            tmp_file = self.getFileName(scen, fw, cbs_type, sid, mth, na)
                        
                            if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                self.get_y_val(in_mode, scen, fw, cbs_type, sid, mth, na)
                            else:  # if the csv file does not exist
                                self.total_num += self.ins_num
                    try:
                        self.y_val /= self.total_num 
                    except ZeroDivisionError:
                        if in_mode == 4:
                            self.y_val = np.inf
                        else:
                            self.y_val = 0.0

                    self.result[fw][(mth, cbs_type)]['x'].append(na)
                    self.result[fw][(mth, cbs_type)]['y'].append(self.y_val)

    def cal_iteration_ratio(self, cbs_type, focal_list, mth_list):
        for fw in focal_list:
            if fw not in self.result.keys():
                self.result[fw]: Dict[Tuple[int, str], List[float]] = dict()

        for mth in mth_list:
            self.result[fw][(mth, cbs_type)] = {'x': list(), 'y': list()}
            for na in self.num_list:
                self.y_val = 0
                for scen in self.scen_list:
                    for sid in self.sid_dict[scen]:
                        tmp_dir = self.getFileDir(cbs_type, mth, na)
                        tmp_file = self.getFileName(scen, fw, cbs_type, sid, mth, na)
                    
                        if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                            self.get_y_val(2, scen, fw, cbs_type, sid, mth, na)
                            max_MA = self.y_val
                            self.get_y_val(3, scen, fw, cbs_type, sid, mth, na)
                            HL_merge = self.y_val
                self.y_val = max_MA / HL_merge

                self.result[fw][(mth, cbs_type)]['x'].append(na)
                self.result[fw][(mth, cbs_type)]['y'].append(self.y_val)


    def get_common_ins(self):
        common_ins: Dict[Tuple[int, str, int], List[str]] = dict()
        for na in self.num_list:
            for scen in self.scen_list:
                for sid in self.sid_dict[scen]:
                    df_list: List[pd.DataFrame] = list()
                    for fw in self.focal_w:
                        for tp in self.cbs_types:
                            if tp == 'ECBS' or tp == 'ECBS1' or tp == 'ECBS_rt5' or tp == 'ECBS1_rt5':
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                cond = tmp_df['solution cost'] == -1
                                tmp_df = tmp_df.drop(tmp_df[cond].index)
                                df_list.append(tmp_df['instance name'])

                            elif tp in self.ma_list:
                                for mth in self.merge_th:
                                    if tp in self.subopt_list:
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                    elif tp in self.opt_list:
                                        tmp_df = self.getCSVIns(scen, 1.00, tp, sid, mth, na)
                                    cond = tmp_df['solution cost'] == -1
                                    tmp_df = tmp_df.drop(tmp_df[cond].index)
                                    df_list.append(tmp_df['instance name'])

                    in_common = reduce(np.intersect1d, df_list)
                    in_common = in_common.tolist()
                    common_ins[(na, scen, sid)] = in_common
        return common_ins


    def plot_best_case(self, in_mode):        
        type_list = [(-1, 'ECBS'), (-1, 'ECBS_rt5'), (100, 'MAECBS_mrr0'), (100, 'MAECBS_ro')]
        
        self.result = dict()  # Reset the dictionary
        for tp in type_list:
            if tp[1] in self.opt_list:  # optimal cases
                if tp[1] == 'CBS':
                    self.cal_iteration(tp[1], [1.00], [-1], in_mode)
                else:
                    self.cal_iteration(tp[1], [1.00], [tp[0]], in_mode)
                    
            elif tp[1] in self.subopt_list:  # sub-optimal cases
                if tp[1] == 'ECBS':
                    self.cal_iteration(tp[1], self.focal_w, [-1], in_mode)
                else:
                    self.cal_iteration(tp[1], self.focal_w, [tp[0]], in_mode)

        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)

        for tp in type_list:
            if tp[1] in self.opt_list:  # optimal cases
                if tp[1] in self.ma_list:
                    self.plot_y_val(tp[1], [1.00], [tp[0]], in_mode)
                else:
                    self.plot_y_val(tp[1], [1.00], [-1], in_mode)

            elif tp[1] in self.subopt_list:
                if tp[1] in self.ma_list:
                    self.plot_y_val(tp[1], self.focal_w, [tp[0]], in_mode)
                else:
                    self.plot_y_val(tp[1], self.focal_w, [-1], in_mode)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        out_file: str = "temp.png"
        if in_mode == 0:  # num-success rate
            plt.yticks(np.arange(0, 105, 10))
            plt.ylabel('Success Rate (%)', fontsize=self.label_size)
            out_file = self.map_name + '_' + str(self.num_of_agent) + '_num_success.png'

        elif in_mode == 1:  # num-runtime
            plt.ylabel('Average Runtime (sec)', fontsize=self.label_size)
            out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_runtime.png'

        elif in_mode == 2:  # num-max MA size
            _, end = ax.get_ylim()
            plt.yticks(np.arange(0, np.ceil(end), 1))
            plt.ylabel('Avg. Max MA size', fontsize=self.label_size)
            out_file = self.map_name + '_' + str(self.num_of_agent) + '_num_maxMA.png'

        else:
            logging.error("in_mode is required!")
            exit(1)

        plt.rcParams.update(params)
        plt.xticks(self.num_list)
        plt.xlabel('#agents', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)
        
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return

            

    def get_y_val(self, in_mode, scen, fw, cbs_type, sid, mth, na):
        tmp_df = self.getCSVIns(scen, fw, cbs_type, sid, mth, na)

        if self.plot_common:
            cond = tmp_df['instance name'].isin(self.common_ins[(na, scen, sid)]) == False
            tmp_df = tmp_df.drop(tmp_df[cond].index)

        if in_mode == 0:  # num - successRate
            for _, row in tmp_df.iterrows():
                if row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:
                    self.y_val += 1
            self.total_num += tmp_df.shape[0]
            
            # if less than ins_num is save
            if tmp_df.shape[0] < self.ins_num and not self.plot_common:
                print('-------------------------------------------------------------------------------')
                logging.warn("#agent={0} in {1}".format(na, self.map_name))
                logging.warn("Number of instances < {0} in {1}, w={2}, b={3}.".format(self.ins_num, cbs_type, fw, mth))
                print('-------------------------------------------------------------------------------')

                remain_num = self.ins_num - tmp_df.shape[0]
                for _ in range(remain_num):
                    self.total_num += 1

        elif in_mode == 1:  # num - runtime
            for _, row in tmp_df.iterrows():
                if row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:
                    self.y_val += row['runtime']
                elif not self.plot_common:
                    self.y_val += self.time_limit
            self.total_num += tmp_df.shape[0]

            # if less than ins_num is save
            if tmp_df.shape[0] < self.ins_num and not self.plot_common:
                print('-------------------------------------------------------------------------------')
                logging.warn("#agent={0} in {1}".format(na, self.map_name))
                logging.warn("Number of instances {0} < {1} in {2}, w={3}, b={4}.".format(tmp_df.shape[0], self.ins_num, cbs_type, fw, mth))
                print('-------------------------------------------------------------------------------')
            
                remain_num = self.ins_num - tmp_df.shape[0]
                for _ in range(remain_num):
                    self.y_val += self.time_limit
                    self.total_num += 1

        elif in_mode == 2:  # num - max_MA
            for _, row in tmp_df.iterrows():
                self.y_val += row['max MA']
            self.total_num += tmp_df.shape[0]

        elif in_mode == 3:  # num - HL_merge
            for _, row in tmp_df.iterrows():
                self.y_val += row['#high-level merged']
            self.total_num += tmp_df.shape[0]

        elif in_mode == 4:  # num- avg. lower bound improvement
            tmp_df_ecbs = self.getCSVIns(scen, fw, 'ECBS', sid, -1, na)
            for _, row in tmp_df.iterrows():
                ins_idx = int(row['instance name'].split('/')[-1].split('-')[-1].split('.')[0]) - 1
                if row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:
                    self.y_val += (row['root f value'] - tmp_df_ecbs.loc[ins_idx]['root f value'])
                    self.total_num += 1
        return


    def get_cbs_label(self, cbs_type, fw, mth):
        if cbs_type == 'CBS' or cbs_type == 'ECBS':
            out_str = cbs_type

        elif cbs_type == 'ECBS_rt5':
            out_str = 'ECBS (rt=5)'

        elif cbs_type == 'MACBS_EPEA':
            out_str = 'MACBS-EPEA* (b=' + str(mth) + ')'
        
        elif cbs_type == 'MACBS_EPEA_mr':
            out_str = 'MACBS-EPEA* (MR, b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS_EPEA':
            out_str = 'MAECBS-EPEA* (b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS_EPEA_mr':
            out_str = 'MAECBS-EPEA* (MR, b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS':
            out_str = 'NECBS (b=' + str(mth) + ')'

        elif cbs_type == 'MAECBS_mr':
            out_str = 'NECBS (MR, b=' + str(mth) + ')'

        elif cbs_type == 'MAECBS_mr1':
            out_str = 'NECBS (MR, c=1, b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS_mrr1':
            out_str = 'NECBS (MRR, c=1, b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS_mrr0':
            out_str = 'NECBS (MRR, b=' + str(mth) + ')'

        elif cbs_type == 'MAECBS_ro':
            out_str = 'ECBS (R, b=' + str(mth) + ')'

        elif cbs_type == 'MAECBS_ro1':
            out_str = 'ECBS (R, c=1, b=' + str(mth) + ')'
        
        elif cbs_type == 'MAECBS_ro_rt5':
            out_str = 'ECBS (R, rt=5, b=' + str(mth) + ')'


        return out_str        

    
    def plot_y_val(self, cbs_type, focal_list, mth_list, in_mode):
        for fw in focal_list:
            for mth in mth_list:
                tmp_label = self.get_cbs_label(cbs_type, fw, mth)
                if in_mode == 0:
                    plt.plot(self.result[fw][(mth, cbs_type)]['x'], [x*100 for x in self.result[fw][(mth, cbs_type)]['y']], 
                        linewidth=self.lw, 
                        color=self.colors[self.tmp_tp[(fw, mth, cbs_type)]], 
                        marker=self.marks[self.tmp_tp[(fw, mth, cbs_type)]], 
                        ms=self.ms, 
                        label=tmp_label)
                else:
                    if in_mode == 2 and cbs_type not in self.ma_list:
                        continue
                    plt.plot(self.result[fw][(mth, cbs_type)]['x'], self.result[fw][(mth, cbs_type)]['y'], 
                        linewidth=self.lw, 
                        color=self.colors[self.tmp_tp[(fw, mth, cbs_type)]], 
                        marker=self.marks[self.tmp_tp[(fw, mth, cbs_type)]], 
                        ms=self.ms, 
                        label=tmp_label)
        return

    def plot_num_y_val(self, in_mode):
        self.result = dict()  # Reset the dictionary
        for tp in self.cbs_types:
            if tp in self.opt_list:  # optimal cases
                if tp == 'CBS':
                    self.cal_iteration(tp, [1.00], [-1], in_mode)
                else:
                    self.cal_iteration(tp, [1.00], self.merge_th, in_mode)
                    
            elif tp in self.subopt_list:  # sub-optimal cases
                if tp == 'ECBS' or tp == 'ECBS1' or tp == 'ECBS_rt5' or tp == 'ECBS1_rt5':
                    self.cal_iteration(tp, self.focal_w, [-1], in_mode)
                else:
                    self.cal_iteration(tp, self.focal_w, self.merge_th, in_mode)

        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)

        for tp in self.cbs_types:
            if tp in self.opt_list:  # optimal cases
                if tp in self.ma_list:
                    self.plot_y_val(tp, [1.00], self.merge_th, in_mode)
                else:
                    self.plot_y_val(tp, [1.00], [-1], in_mode)

            elif tp in self.subopt_list:
                if tp in self.ma_list:
                    self.plot_y_val(tp, self.focal_w, self.merge_th, in_mode)
                else:
                    self.plot_y_val(tp, self.focal_w, [-1], in_mode)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        out_file: str = "temp.png"
        if in_mode == 0:  # num-success rate
            plt.yticks(np.arange(0, 105, 10))
            plt.ylabel('Success Rate (%)', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_success.png'

        elif in_mode == 1:  # num-runtime
            plt.ylabel('Average Runtime (sec)', fontsize=self.label_size)
            out_file: str = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_runtime.png'

        elif in_mode == 2:  # num-max MA size
            _, end = ax.get_ylim()
            plt.yticks(np.arange(0, np.ceil(end), 1))
            plt.ylabel('Avg. Max MA size', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_maxMA.png'

        elif in_mode == 3:  # num-HL_merge
            plt.ylabel('#HL-restart', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_HLRestart.png'

        elif in_mode == 4:  # num-Lower bound improvement
            plt.ylabel('Lower bound improvement', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_LBImprove.png'

        else:
            logging.error("in_mode is required!")
            exit(1)

        plt.rcParams.update(params)
        plt.xticks(self.num_list)
        plt.xlabel('#agents', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)
        
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return

    def plot_instances(self, cbs_type, fw, mth):

        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
            'lines.markersize': self.ms
        }
        plt.rcParams.update(params)

        max_val = -1
        max_our = -1
        max_ecbs = -1
        our_exp = dict()
        ecbs_exp = dict()
        for na_id, na in enumerate(self.num_list):
            our_exp[na] = dict()
            ecbs_exp[na] = dict()

            for scen in self.scen_list:
                for sid in self.sid_dict[scen]:
                    tmp_dir = self.getFileDir(cbs_type, mth, na)
                    tmp_file = self.getFileName(scen, fw, cbs_type, sid, mth, na)
                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                        tmp_df = self.getCSVIns(scen, fw, cbs_type, sid, mth, na)
                        for _, row in tmp_df.iterrows():
                            ins_idx = int(row['instance name'].split('/')[-1].split('-')[-1].split('.')[0])
                            if np.sign(row['solution cost']) > 0:
                                our_exp[na][ins_idx] = row['#high-level generated']
                            else:
                                our_exp[na][ins_idx] = -1

                        for i in range(1, self.ins_num + 1):
                            if i not in our_exp[na].keys():
                                our_exp[na][i] = -1

                    tmp_dir = self.getFileDir('ECBS', mth, na)
                    tmp_file = self.getFileName(scen, fw, 'ECBS', sid, mth, na)
                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                        tmp_df = self.getCSVIns(scen, fw, 'ECBS', sid, mth, na)
                        for _, row in tmp_df.iterrows():
                            ins_idx = int(row['instance name'].split('/')[-1].split('-')[-1].split('.')[0])
                            if np.sign(row['solution cost']) > 0:
                                ecbs_exp[na][ins_idx] = row['#high-level generated']
                            else:
                                ecbs_exp[na][ins_idx] = -1

                        for i in range(1, self.ins_num + 1):
                            if i not in ecbs_exp[na].keys():
                                ecbs_exp[na][i] = -1

            print('number of agents: ', na)
            print('ecbs: ', ecbs_exp[na].values())
            print('ours: ', our_exp[na].values())
            print('-------------------------------------------')

            if max_val < max(max(ecbs_exp[na].values()), max(our_exp[na].values())):
                max_val = max(max(ecbs_exp[na].values()), max(our_exp[na].values()))

            if max_our < max(our_exp[na].values()):
                max_our = max(our_exp[na].values())

            if max_ecbs < max(ecbs_exp[na].values()):
                max_ecbs = max(ecbs_exp[na].values())
    
        plt.xscale('symlog')
        x = np.linspace(0, max_our+150, 100)
        plt.plot(x, x, 'k--', label='y=x')
        plt.xlim(-1, max_ecbs)
        plt.ylim(-50, max_our)
        plt.xlabel('ECBS (log)', fontsize=self.label_size)
        plt.ylabel('NECBS (MR, b='+str(mth)+')', fontsize=self.label_size)

        tmp_list = ax.get_xticks()
        tmp_x_range = tmp_list[-1] // tmp_list[-2]
        tmp_list = np.append(tmp_list, [tmp_list[-1] * tmp_x_range])
        ax.set_xticks(tmp_list)
        plt.xlim(-1, tmp_list[-1]*20)

        tmp_list = ['$10^{'+str(int(np.log10(i)))+'}$' if i > 0 else '$'+str(int(i))+'$' for i in tmp_list]
        tmp_list[-1] = '$\infty$'
        ax.set_xticklabels(tmp_list)

        tmp_list_y = ax.get_yticks()
        tmp_y_range = tmp_list_y[-1] - tmp_list_y[-2]
        tmp_list_y = np.append(tmp_list_y, [tmp_list_y + tmp_y_range])
        ax.set_yticks(tmp_list_y)
        plt.ylim(-50, tmp_list_y[-1]+150)

        tmp_list_y = ['$'+str(int(i))+'$' for i in tmp_list_y]
        tmp_list_y[-1] = '$\infty$'
        ax.set_yticklabels(tmp_list_y)

        # plt.axvline(x=ax.get_xticks()[-1], color='k')
        for na_id, na in enumerate(self.num_list):
            for tmp_id, val in ecbs_exp[na].items():
                if val == -1:
                    ecbs_exp[na][tmp_id] = ax.get_xticks()[-1]
            
            for tmp_id, val in our_exp[na].items():
                if val == -1:
                    our_exp[na][tmp_id] = ax.get_yticks()[-1]

            plt.scatter(ecbs_exp[na].values(), our_exp[na].values(), 
                marker=self.marks[na_id], c=self.colors[na_id], label='N='+str(na))

        ax.legend(fontsize=self.legend_size)
        plt.show()
        return


    def cal_num_ins(self, cbs_type, in_focal_w, mth_list, in_mode=4):

        """[summary]
        Plot value among all instances
        Args:
            cbs_type (string): type of CBS
            in_focal_w (float): focal weight, the suboptimal bound
            mth_list (List[int]): list of merge threshold, [-1] for ECBS
            in_mode (int): which statistic to plot
        """
        fw = in_focal_w
        
        if fw not in self.result.keys():
            self.result[fw]: Dict[Tuple[int, str], List[float]] = dict()

        for mth in mth_list:
            self.result[fw][(mth, cbs_type)] = {'x': list(), 'y': list()}

            x_idx = 0
            for na in self.num_list:
                for scen in self.scen_list:
                    for sid in self.sid_dict[scen]:
                        y_list_per_csv = [np.inf for i in range(self.ins_num)]
                        tmp_dir = self.getFileDir(cbs_type, mth, na)
                        tmp_file = self.getFileName(scen, fw, cbs_type, sid, mth, na)
                    
                        if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                            tmp_df = self.getCSVIns(scen, fw, cbs_type, sid, mth, na)
                            tmp_df_ecbs = self.getCSVIns(scen, fw, 'ECBS', sid, -1, na)

                            for _, row in tmp_df.iterrows():
                                ins_idx = int(row['instance name'].split('/')[-1].split('-')[-1].split('.')[0]) - 1
                                if in_mode == 4 and row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:  # Lower bound improvement
                                    y_list_per_csv[ins_idx] = row['root f value'] - tmp_df_ecbs.loc[ins_idx]['root f value']
                                
                                elif in_mode == 5 and row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:  # runtime per instance
                                    y_list_per_csv[ins_idx] = row['runtime']
                                
                                elif in_mode == 6: # and row['solution cost'] >= 0 and row['runtime'] <= self.time_limit:  # runtime per instance
                                    # y_list_per_csv[ins_idx] = row['#high-level merged']
                                    y_list_per_csv[ins_idx] = row['#high-level generated']

                            for yval in y_list_per_csv:
                                self.result[fw][(mth, cbs_type)]['y'].append(yval)                
                            for i in range(x_idx, x_idx+self.ins_num):
                                self.result[fw][(mth, cbs_type)]['x'].append(i)
                            x_idx += self.ins_num
        return


    def plot_num_ins_y_val(self, in_mode=4):
        self.result = dict()  # Reset the dictionary
        for tp in self.cbs_types:
            if tp in self.opt_list:  # optimal cases
                if tp == 'CBS':
                    self.cal_num_ins(tp, 1.00, [-1], in_mode)
                else:
                    self.cal_num_ins(tp, 1.00, self.merge_th, in_mode)
                    
            elif tp in self.subopt_list:  # sub-optimal cases
                if tp == 'ECBS' or tp == 'ECBS1' or tp == 'ECBS_rt5' or tp == 'ECBS1_rt5':
                    self.cal_num_ins(tp, self.focal_w[0], [-1], in_mode)
                else:
                    self.cal_num_ins(tp, self.focal_w[0], self.merge_th, in_mode)

        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)

        for tp in self.cbs_types:
            if tp in self.opt_list:  # optimal cases
                if tp in self.ma_list:
                    self.plot_y_val(tp, [1.00], self.merge_th, in_mode)
                else:
                    self.plot_y_val(tp, [1.00], [-1], in_mode)

            elif tp in self.subopt_list:
                if tp in self.ma_list:
                    self.plot_y_val(tp, self.focal_w, self.merge_th, in_mode)
                else:
                    self.plot_y_val(tp, self.focal_w, [-1], in_mode)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        if in_mode == 4:  # Lower bound improvement
            plt.ylabel('Lower bound improvement', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_lb_improve.png'

        elif in_mode == 5:  # runtime of instances
            plt.ylabel('Runtime (sec)', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_ins_runtime.png'

        elif in_mode == 6:  # runtime of instances
            plt.yticks(np.arange(0, 1751, 250))
            # plt.ylabel('#Restart', fontsize=self.label_size)
            plt.ylabel('#HL-generated', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_ins_restart.png'

        else:
            pass

        plt.rcParams.update(params)
        plt.xlabel('Instances', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)
        
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()


    def plot_fmin_yval(self, in_mode):
        if len(self.focal_w) <= 1:
            logging.error('focal_weight in config.yaml should be more than one.')
            exit(-1)
        
        self.result = dict()  # Reset the dictionary
        for tp in self.cbs_types:
            for mth in self.merge_th:
                if (mth, tp) not in self.result.keys():
                    self.result[(mth, tp)]: Dict[float, float] = dict()

            for fw in self.focal_w:
                    self.y_val = 0
                    self.total_num = 0

                    for na in self.num_list:
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_dir = self.getFileDir(tp, mth, na)
                                tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                            
                                if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                    self.get_y_val(in_mode, scen, fw, tp, sid, mth, na)
                                else:  # if the csv file does not exist
                                    self.total_num += self.ins_num

                    try:
                        self.result[(mth, tp)][fw] = self.y_val / self.total_num
                    except ZeroDivisionError:
                        self.result[(mth, tp)][fw] = 0.0
                        
        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)

        for _k in self.result.keys():
            fw_0 = 1.02 # self.result[_k].keys()[0]
            mth = _k[0]
            cbs_type = _k[1]
            tmp_label = self.get_cbs_label(cbs_type, fw_0, mth)
            
            if in_mode == 0:
                plt.plot(list(self.result[_k].keys()), [x*100 for x in list(self.result[_k].values())],
                    linewidth=self.lw,
                    color=self.colors[self.tmp_tp[(fw_0, mth, cbs_type)]],
                    marker=self.marks[self.tmp_tp[(fw_0, mth, cbs_type)]],
                    ms=self.ms,
                    label=tmp_label)
            else:
                plt.plot(list(self.result[_k].keys()), list(self.result[_k].values()),
                    linewidth=self.lw,
                    color=self.colors[self.tmp_tp[(fw_0, mth, cbs_type)]],
                    marker=self.marks[self.tmp_tp[(fw_0, mth, cbs_type)]],
                    ms=self.ms,
                    label=tmp_label)

        ax.yaxis.grid(True)
        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        out_file: str = "temp.png"
        if in_mode == 0:  # num-success rate
            plt.yticks(np.arange(0, 105, 10))
            plt.ylabel('Success Rate (%)', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_success.png'

        elif in_mode == 1:  # num-runtime
            plt.ylabel('Average Runtime (sec)', fontsize=self.label_size)
            out_file: str = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_runtime.png'

        elif in_mode == 4:  # num-Lower bound improvement
            plt.ylabel('Lower bound improvement', fontsize=self.label_size)
            out_file = self.map_name + '_f' + str(self.focal_w[0]) + '_b' + str(self.merge_th[0]) + '_num_LBImprove.png'

        else:
            logging.error("in_mode is required!")
            exit(1)

        plt.rcParams.update(params)
        plt.xticks(self.focal_w)
        plt.xlabel('$f_{min}$', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)
        
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return
             

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Take config.yaml as input!')
    parser.add_argument('--config', type=str, default='config.yaml')
    args = parser.parse_args()

    dp = DataProcessor(args.config)
    dp.plot_num_y_val(0)
    # dp.plot_fmin_yval(0)
    # dp.plot_fmin_yval(4)
    # dp.plot_num_y_val(1)
    # dp.plot_num_y_val(2)
    # dp.plot_num_y_val(3)
    # dp.plot_num_y_val(4)
    # dp.plot_instances('MAECBS_mr', 1.05, 100)
    # dp.plot_best_case(0)
    # dp.plot_best_case(1)
    # dp.plot_best_case(2)
    # dp.plot_num_ins_y_val(4)
    # dp.plot_num_ins_y_val(5)
    # dp.plot_num_ins_y_val(6)
    