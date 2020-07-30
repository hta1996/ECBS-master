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
        config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), in_config)
        with open(config_dir, 'r') as fin:
            config_dict = yaml.load(fin, Loader=yaml.FullLoader)

        self.exp_dir = '/home/rdaneel/my_exp2'
        self.ins_num = 25
        self.time_limit = 600

        self.todo_function = config_dict['function']
        self.map_name: str = config_dict['map_name']
        self.scen_list: List[str] = list(config_dict['scen_dict'].keys())
        self.sid_dict: Dict[str, List[int]] = config_dict['scen_dict']
        self.focal_w: List[float] = config_dict['focal_w']
        self.num_of_agent: int = config_dict['num_of_agent']
        self.cbs_types: List[str] = config_dict['cbs_types']
        self.merge_th: List[int] = config_dict['merge_th']
        # self.map_list: List[str] = ['random-32-32-20', 'den520d','ost003d']
        self.map_list: List[str] = []

        # Plot parameters
        self.fig_h = 12
        self.fig_w = 8
        self.ms = 10
        self.lw = 1.5
        self.num_size = 14
        self.label_size = 16
        self.title_size = 18
        self.legend_size = 14
        self.colors = ['blue', 'red', 'green', 'purple', 'orange', 'grey', 'brown', 'pink', 'black', 'cyan']
        self.marks = ['o', 's', 'D', 'X', '^', 'H', 'v', 'P', '#', '<']
        self.tmp_tp = {(-1, 'ECBS'): 7, (1, 'MACBS'): 1, (10, 'MACBS'): 2, (1, 'MAECBS'): 3, (10, 'MAECBS'): 4,
            (50, 'MACBS'): 5, (50, 'MAECBS'): 6, (-1, 'CBS'): 0, (-1, 'MACBS_EPEA'):8}

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
        out_dir = os.path.join(map_dir, 'a'+str(num_of_ag), cbs_type)

        if cbs_type == 'MACBS' or cbs_type == 'MAECBS' or cbs_type == 'MACBS_EPEA':
            out_dir = os.path.join(out_dir, 'b'+str(merge_th))
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

        elif cbs_type == 'MACBS' or cbs_type == 'MAECBS' or cbs_type == 'MACBS_EPEA':
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

    def plot_time_soc(self):

        common_ins: Dict[Tuple[str, int], List[str]] = dict()
        for scen in self.scen_list:
            for sid in self.sid_dict[scen]:
                df_list: List[pd.DataFrame] = list()
                for fw in self.focal_w:
                    for tp in self.cbs_types:
                        if tp == 'ECBS':
                            tmp_df = self.getCSVIns(scen, fw, tp, sid)
                            df_list.append(tmp_df['instance name'])
                        elif tp == 'MACBS' or tp == 'MAECBS':
                            for mth in self.merge_th:
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, mth)
                                df_list.append(tmp_df['instance name'])

                in_common = reduce(np.intersect1d, df_list)
                in_common = in_common.tolist()
                common_ins[(scen, sid)] = in_common
                                            
        result = dict()
        for tp in self.cbs_types:
            if tp == 'ECBS':
                r_idx: Tuple[int, str] = (-1, tp)
                for fw in self.focal_w:                    
                    _df = pd.DataFrame()
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_ins = self.getCSVIns(scen, fw, tp, sid)
                            cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                            tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                            _df = _df.append(tmp_ins, ignore_index=True)
                    
                    if r_idx not in result.keys():
                        result[r_idx] = {'time': [], 'cost': []}
                    result[r_idx]['time'].append(_df['runtime'].mean())
                    result[r_idx]['cost'].append(_df['solution cost'].mean())


            elif tp == 'MACBS' or tp == 'MAECBS':
                for mth in self.merge_th:
                    r_idx: Tuple[int, str] = (mth, tp)
                    for fw in self.focal_w:
                        _df = pd.DataFrame()
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_ins = self.getCSVIns(scen, fw, tp, sid, mth)
                                cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                                tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                                _df = _df.append(tmp_ins, ignore_index=True)
                    
                        if r_idx not in result.keys():
                            result[r_idx] = {'time': [], 'cost': []}
                        result[r_idx]['time'].append(_df['runtime'].mean())
                        result[r_idx]['cost'].append(_df['solution cost'].mean())


        # debug
        print('-------------------------------------------------')
        for k in result.keys():
            print(k, '| ', 'len: ', len(result[k]['time']))
            print(result[k]['time'])
            print(result[k]['cost'])
        print('-------------------- END ------------------------')

        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = str(self.num_of_agent) + ' agents on ' + self.map_name + ', ' + \
        #     r'$w_{focal} = [$' + str(min(self.focal_w)) + ', ' + str(max(self.focal_w)) + ']'
        # plt.title(fig_title, fontsize=self.title_size)
        idx = 0
        for tp in self.cbs_types:
            if tp == 'ECBS':
                plt.plot(result[(-1, tp)]['time'], result[(-1, tp)]['cost'], linewidth=self.lw, 
                    color=self.colors[self.tmp_tp[(-1, tp)]], marker=self.marks[self.tmp_tp[(-1, tp)]], ms=self.ms, label=tp, zorder=idx+10)
                idx += 1
            elif tp == 'MACBS' or tp == 'MAECBS':
                for mth in self.merge_th:
                    tmp_la = tp + '(b=' + str(mth) + ')'
                    plt.plot(result[(mth, tp)]['time'], result[(mth, tp)]['cost'], linewidth=self.lw, 
                        color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_la, zorder=idx)
                    idx += 1
        
        # x_ub = list()
        # for mth in self.merge_th:
        #     x_ub.append(max(result[(mth, 'MACBS')]['time']))

        # plt.xlim(-0.25, max(x_ub) + 0.25)
        # plt.ylim(np.floor(np.min(result[(-1, 'ECBS')]['cost'])) - 0.25, 
        #     np.max(np.ceil(result[(-1, 'ECBS')]['cost'])) + 0.25)
        # plt.grid(True)
        ax.yaxis.grid(True)

        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
            'axes.labelsize': self.label_size,
        }

        plt.rcParams.update(params)
        plt.xlabel('Average Runtime (sec)', fontsize=self.label_size)
        plt.ylabel('Average Sum of Cost', fontsize=self.label_size)
        # ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.1))
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='upper right')

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_time_soc.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()

    def plot_num_success(self):
        result: Dict[float] = dict()
        
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                        result[fw][(-1, tp)] = {'num': list(), 'success': list()}
                        for na in range(10, 110, 10):
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, -1, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                        success_num += tmp_df.shape[0]
                                        total_num += 25

                            if total_num == 0:
                                    success_rate = 0
                            else:        
                                success_rate =  success_num / total_num

                            result[fw][(-1, tp)]['num'].append(na)
                            result[fw][(-1, tp)]['success'].append(success_rate)

            elif tp == 'CBS':  # for CBS
                fw = 1.00
                if fw not in result.keys():
                    result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                result[fw][(-1, tp)] = {'num': list(), 'success': list()}
                for na in range(10, 110, 10):
                    success_num = 0
                    total_num = 0
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_dir = self.getFileDir(tp, -1, na)
                            tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)
                            
                            if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                success_num += tmp_df.shape[0]
                                total_num += 25

                    if total_num == 0:
                        success_rate = 0
                    else:        
                        success_rate =  success_num / total_num
                        
                    result[fw][(-1, tp)]['num'].append(na)
                    result[fw][(-1, tp)]['success'].append(success_rate)

            elif tp == 'MACBS_EPEA':  # for MACBS_EPEA
                fw = 1.00
                if fw not in result.keys():
                    result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                for mth in self.merge_th:
                    result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                    for na in range(10, 50, 10):
                        success_num = 0
                        total_num = 0
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_dir = self.getFileDir(tp, mth, na)
                                tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                    tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                    success_num += tmp_df.shape[0]
                                    total_num += 25
                        if total_num == 0:
                            success_rate = 0
                        else:        
                            success_rate =  success_num / total_num
                            
                        result[fw][(mth, tp)]['num'].append(na)
                        result[fw][(mth, tp)]['success'].append(success_rate)
                        

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                        for na in range(10, 110, 10):
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        success_num += tmp_df.shape[0]
                                        total_num += 25
                            if total_num == 0:
                                success_rate = 0
                            else:        
                                success_rate =  success_num / total_num

                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['success'].append(success_rate)

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                        for mth in self.merge_th:
                            result[fw][(mth, tp)] = {'num': list(), 'success': list()}
                            for na in range(10, 110, 10):
                                success_num = 0
                                total_num = 0
                                for scen in self.scen_list:
                                    for sid in self.sid_dict[scen]:
                                        tmp_dir = self.getFileDir(tp, mth, na)
                                        tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                    
                                        if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                            tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                            success_num += tmp_df.shape[0]
                                            total_num += 25
                                if total_num == 0:
                                    success_rate = 0
                                else:        
                                    success_rate =  success_num / total_num

                                result[fw][(mth, tp)]['num'].append(na)
                                result[fw][(mth, tp)]['success'].append(success_rate)

        # Plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Success Rate on ' + self.map_name
        # plt.title(fig_title, fontsize=20)
        idx = 0
        
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        tmp_label = tp + '(w=' + str(fw) + ')'
                        plt.plot(result[fw][(-1, tp)]['num'], [x*100 for x in result[fw][(-1, tp)]['success']], linewidth=self.lw, 
                            color=self.colors[self.tmp_tp[(-1, tp)]], marker=self.marks[self.tmp_tp[(-1, tp)]], 
                            ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1
            elif tp == 'CBS':
                fw = 1.00
                tmp_label = 'CBS'
                plt.plot(result[fw][(-1, tp)]['num'], [x*100 for x in result[fw][(-1, tp)]['success']], linewidth=self.lw, 
                    # color=self.colors[self.tmp_tp[(-1, tp)]], marker=self.marks[self.tmp_tp[(-1, tp)]],
                    color=self.colors[idx], marker=self.marks[idx],
                    ms=self.ms, label=tmp_label, zorder=idx)
                idx += 1

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = tp + '(w=' + str(fw) + ', b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], linewidth=self.lw, 
                            color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1

            elif tp == 'MACBS_EPEA':
                fw = 1.00
                for mth in self.merge_th:
                    tmp_label = tp + '( b=' + str(mth) + ')'
                    plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], linewidth=self.lw, 
                        color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                    idx += 1

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        for mth in self.merge_th:
                            tmp_label = tp + '(w=' + str(fw) + ', b=' + str(mth) + ')'
                            plt.plot(result[fw][(mth, tp)]['num'], [x*100 for x in result[fw][(mth, tp)]['success']], linewidth=self.lw, 
                                color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                            idx += 1

        # plt.grid(True)
        ax.yaxis.grid(True)

        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xticks(np.arange(10, 41, 10))
        plt.xlabel('Number of agents', fontsize=self.label_size)
        plt.yticks(np.arange(0, 105, 10))
        plt.ylabel('Success Rate (%)', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(fontsize=self.legend_size)

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_success.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()

    def plot_num_runtime(self):
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        num_list = range(10, 50, 10)
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                        result[fw][(-1, tp)] = {'num': list(), 'runtime': list()}
                        for na in num_list:
                            ins_runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, -1, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)

                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                        ins_runtime += tmp_df['runtime'].sum()
                                        ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                    else:
                                        ins_runtime += self.time_limit * 25
                                    total_num += 25

                            mean_runtime =  ins_runtime / total_num
                            result[fw][(-1, tp)]['num'].append(na)
                            result[fw][(-1, tp)]['runtime'].append(mean_runtime)

            elif tp == 'CBS':  # for CBS
                fw = 1.00
                if fw not in result.keys():
                    result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                result[fw][(-1, tp)] = {'num': list(), 'runtime': list()}
                for na in num_list:
                    ins_runtime = 0
                    total_num = 0
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_dir = self.getFileDir(tp, -1, na)
                            tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)

                            if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                ins_runtime += tmp_df['runtime'].sum()
                                ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                            else:
                                ins_runtime += self.time_limit * 25
                            total_num += 25
                            
                    mean_runtime =  ins_runtime / total_num
                    result[fw][(-1, tp)]['num'].append(na)
                    result[fw][(-1, tp)]['runtime'].append(mean_runtime)

            elif tp == 'MACBS_EPEA':  # for MACBS_EPEA
                fw = 1.00
                if fw not in result.keys():
                    result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                for mth in self.merge_th:
                    result[fw][(mth, tp)] = {'num': list(), 'runtime': list()}
                    for na in range(10, 50, 10):
                        ins_runtime = 0
                        total_num = 0
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_dir = self.getFileDir(tp, mth, na)
                                tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                
                                if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                    tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                    ins_runtime += tmp_df['runtime'].sum()
                                    ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                else:
                                    ins_runtime += self.time_limit * 25
                                total_num += 25
                        
                        mean_runtime =  ins_runtime / total_num
                        result[fw][(mth, tp)]['num'].append(na)
                        result[fw][(mth, tp)]['runtime'].append(mean_runtime)

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw not in result.keys():
                        result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                    for mth in self.merge_th:
                        result[fw][(mth, tp)] = {'num': list(), 'runtime': list()}
                        for na in num_list:
                            ins_runtime = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, mth, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)

                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        ins_runtime += tmp_df['runtime'].sum()
                                        ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                    else:
                                        ins_runtime += self.time_limit * 25
                                    total_num += 25

                            mean_runtime =  ins_runtime / total_num
                            result[fw][(mth, tp)]['num'].append(na)
                            result[fw][(mth, tp)]['runtime'].append(mean_runtime)

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                        for mth in self.merge_th:
                            result[fw][(mth, tp)] = {'num': list(), 'runtime': list()}
                            for na in num_list:
                                ins_runtime = 0
                                total_num = 0
                                for scen in self.scen_list:
                                    for sid in self.sid_dict[scen]:
                                        tmp_dir = self.getFileDir(tp, mth, na)
                                        tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)

                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                        ins_runtime += tmp_df['runtime'].sum()
                                        ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                    else:
                                        ins_runtime += self.time_limit * 25
                                    total_num += 25

                                mean_runtime =  ins_runtime / total_num
                                result[fw][(mth, tp)]['num'].append(na)
                                result[fw][(mth, tp)]['runtime'].append(mean_runtime)

        # plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Runtime on ' + self.map_name
        # plt.title(fig_title, fontsize=20)
        idx = 0
        
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        tmp_label = tp + '(w=' + str(fw) + ')'
                        plt.plot(result[fw][(-1, tp)]['num'], result[fw][(-1, tp)]['runtime'], linewidth=self.lw, 
                            color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1

            elif tp == 'CBS':
                tmp_label = 'CBS'
                fw = 1.00
                plt.plot(result[fw][(-1, tp)]['num'], result[fw][(-1, tp)]['runtime'], linewidth=self.lw, 
                    color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                idx += 1

            elif tp == 'MACBS_EPEA':
                tmp_label = tp
                fw = 1.00
                for mth in self.merge_th:
                    tmp_label = tp + '(b=' + str(mth) + ')'
                    plt.plot(result[fw][(mth, tp)]['num'], result[fw][(mth, tp)]['runtime'], linewidth=self.lw, 
                        color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                    idx += 1

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    for mth in self.merge_th:
                        tmp_label = tp + '(w=' + str(fw) + ', b=' + str(mth) + ')'
                        plt.plot(result[fw][(mth, tp)]['num'], result[fw][(mth, tp)]['runtime'], linewidth=self.lw, 
                            color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1

            elif tp == 'MAECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        for mth in self.merge_th:
                            tmp_label = tp + '(w=' + str(fw) + ', b=' + str(mth) + ')'
                            plt.plot(result[fw][(mth, tp)]['num'], result[fw][(mth, tp)]['runtime'], linewidth=self.lw, 
                                color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                            idx += 1

        # plt.grid(True)
        ax.yaxis.grid(True)

        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xticks(num_list)
        plt.xlabel('Number of agents', fontsize=self.label_size)
        # plt.yticks(np.arange(0.5, 1.05, 0.05))
        plt.ylabel('Average Runtime (sec)', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='best')

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_num_runtime.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return

    def plot_ins_ratio(self):
        # plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Suboptimality under ' + r'$w_{focal}=$' + str(self.focal_w[0]) + \
        #     ' for '+ str(self.num_of_agent) + ' agents on ' + self.map_name
        # plt.title(fig_title, fontsize=self.title_size)

        ins_num = 25
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        for tp in self.cbs_types:
            if tp == 'ECBS' or tp == 'CBS':
                mth = -1

                __df = self.getCSVIns(scen_name=self.scen_list[0], f_weight=self.focal_w[0], cbs_type=tp, 
                    sid=self.sid_dict[self.scen_list[0]][0], merge_th=mth, num_of_ag=self.num_of_agent)
                if self.focal_w[0] not in result.keys():
                    result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                for _, row in __df.iterrows():
                    if (mth, tp) not in result[self.focal_w[0]].keys():
                        result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                    tmp_ratio = row['solution cost'] / row['min f value']
                    if tmp_ratio == 0:
                        tmp_ratio = np.inf
                    if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                        result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                    result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])
            else:
                for mth in self.merge_th:
                    __df = self.getCSVIns(self.scen_list[0], self.focal_w[0], tp, 
                        self.sid_dict[self.scen_list[0]][0], mth, self.num_of_agent)
                    if self.focal_w[0] not in result.keys():
                        result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                    for _, row in __df.iterrows():
                        if (mth, tp) not in result[self.focal_w[0]].keys():
                            result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                        tmp_ratio = row['solution cost'] / row['min f value']
                        if tmp_ratio == 0:
                            tmp_ratio = np.inf
                        if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                            result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                        result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])

        tmp_x = np.arange(ins_num)
        answer_list = list()
        ins_list: List[int] = list()
        remain_ins: List[int] = [item for item in range(1, ins_num+1)]
        reverse_dict: Dict[int, float] = dict()

        for r in sorted(result[self.focal_w[0]][(-1, 'ECBS')].keys()):
            for ins_str in result[self.focal_w[0]][(-1, 'ECBS')][r]:
                answer_list.append(r)
                tmp_str = ins_str.split('/')[-1]
                tmp_str = tmp_str.split('-')[-1]
                tmp_str = tmp_str.split('.')[0]
                ins_list.append(int(tmp_str))
                remain_ins.remove(int(tmp_str))

        while len(answer_list) < ins_num:
            answer_list.append(np.inf)
            remain_i = remain_ins.pop()
            reverse_dict[remain_i] = np.inf
            ins_list.append(remain_i)

        tmp_label = 'ECBS'
        plt.plot(tmp_x+1, answer_list, linewidth=self.lw, color=self.colors[0], 
            marker=self.marks[0], ms=self.ms, label=tmp_label)

        for _, m_tp in enumerate(result[self.focal_w[0]].keys()):
            if m_tp != (-1, 'ECBS'):
                tmp_label = m_tp[1] + '(b=' + str(m_tp[0]) + ')'
                remain_ins: List[int] = [item for item in range(1, ins_num+1)]
                reverse_dict: Dict[int, float] = dict()
                for k in result[self.focal_w[0]][m_tp].keys():
                    for ins in result[self.focal_w[0]][m_tp][k]:
                        tmp_str = ins.split('/')[-1]
                        tmp_str = tmp_str.split('-')[-1]
                        tmp_str = tmp_str.split('.')[0]
                        reverse_dict[int(tmp_str)] = k
                        remain_ins.remove(int(tmp_str))

                answer_list = list()
                for ins in ins_list:
                    if ins in reverse_dict.keys():
                        answer_list.append(reverse_dict[ins])
                    else:
                        answer_list.append(np.inf)
                
                plt.plot(tmp_x+1, answer_list, linewidth=self.lw, color=self.colors[self.tmp_tp[m_tp]], 
                    marker=self.marks[self.tmp_tp[m_tp]], ms=self.ms, label=tmp_label)
    
        plt.xticks(tmp_x+1, ins_list)
        # plt.hlines(y=1.0, xmin=0.0, xmax=26, linestyles='--')
        # plt.hlines(y=self.focal_w[0], xmin=0.0, xmax=26, linestyles='--')
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='best', fontsize=self.legend_size)
        ax.yaxis.grid(True)

        plt.xlabel('Instances', fontsize=self.label_size)
        plt.ylabel('Soc/' + r'$f_{min}$', fontsize=self.label_size)
        plt.show()
        return ins_list

    def plot_ins_runtime(self, ins_list=None):
        # plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Runtime under ' + r'$w_{focal}=$' + str(self.focal_w[0]) + \
        #     ' for '+ str(self.num_of_agent) + ' agents on ' + self.map_name
        # plt.title(fig_title, fontsize=self.title_size)

        ins_num = 25
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        for tp in self.cbs_types:
            if tp == 'ECBS' or tp == 'CBS':
                mth = -1

                __df = self.getCSVIns(scen_name=self.scen_list[0], f_weight=self.focal_w[0], cbs_type=tp, 
                    sid=self.sid_dict[self.scen_list[0]][0], merge_th=mth, num_of_ag=self.num_of_agent)
                if self.focal_w[0] not in result.keys():
                    result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                for _, row in __df.iterrows():
                    if (mth, tp) not in result[self.focal_w[0]].keys():
                        result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                    tmp_ratio = row['runtime']
                    if tmp_ratio == 0:
                        tmp_ratio = np.inf
                    if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                        result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                    result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])
            else:
                for mth in self.merge_th:
                    __df = self.getCSVIns(self.scen_list[0], self.focal_w[0], tp, 
                        self.sid_dict[self.scen_list[0]][0], mth, self.num_of_agent)
                    if self.focal_w[0] not in result.keys():
                        result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                    for _, row in __df.iterrows():
                        if (mth, tp) not in result[self.focal_w[0]].keys():
                            result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                        tmp_ratio = row['runtime']
                        if tmp_ratio == 0:
                            tmp_ratio = np.inf
                        if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                            result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                        result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])

        tmp_x = np.arange(ins_num)
        answer_list = list()
        if ins_list is None:
            ins_list: List[int] = np.range(25) + 1
        remain_ins: List[int] = [item for item in range(1, ins_num+1)]
        reverse_dict: Dict[int, float] = dict()

        # for r in sorted(result[self.focal_w[0]][(-1, 'ECBS')].keys()):
        #     for ins_str in result[self.focal_w[0]][(-1, 'ECBS')][r]:
        #         answer_list.append(r)
        #         tmp_str = ins_str.split('/')[-1]
        #         tmp_str = tmp_str.split('-')[-1]
        #         tmp_str = tmp_str.split('.')[0]
        #         ins_list.append(int(tmp_str))
        #         remain_ins.remove(int(tmp_str))

        # while len(answer_list) < ins_num:
        #     answer_list.append(np.inf)
        #     remain_i = remain_ins.pop()
        #     reverse_dict[remain_i] = np.inf
        #     ins_list.append(remain_i)

        # tmp_label = 'ECBS'
        # plt.plot(tmp_x+1, answer_list, linewidth=self.lw, color=self.colors[0], 
        #     marker=self.marks[0], ms=self.ms, label=tmp_label)

        for _, m_tp in enumerate(result[self.focal_w[0]].keys()):
            if m_tp[0] < 0:
                tmp_label = m_tp[1]
            else:
                tmp_label = m_tp[1] + '(b=' + str(m_tp[0]) + ')'
            remain_ins: List[int] = [item for item in range(1, 25+1)]
            reverse_dict: Dict[int, float] = dict()
            for k in result[self.focal_w[0]][m_tp].keys():
                for ins in result[self.focal_w[0]][m_tp][k]:
                    tmp_str = ins.split('/')[-1]
                    tmp_str = tmp_str.split('-')[-1]
                    tmp_str = tmp_str.split('.')[0]
                    reverse_dict[int(tmp_str)] = k
                    remain_ins.remove(int(tmp_str))

            answer_list = list()
            for ins in ins_list:
                if ins in reverse_dict.keys():
                    answer_list.append(np.log(reverse_dict[ins]))
                else:
                    answer_list.append(np.inf)
            
            plt.plot(tmp_x+1, answer_list, linewidth=self.lw, color=self.colors[self.tmp_tp[m_tp]], 
                marker=self.marks[self.tmp_tp[m_tp]], ms=self.ms, label=tmp_label)

        plt.xticks(tmp_x+1, ins_list)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='best', fontsize=self.legend_size)
        ax.yaxis.grid(True)
        plt.xlabel('Instances', fontsize=self.label_size)
        plt.ylabel('log Runtime (sec)', fontsize=self.label_size)
        plt.show()
        return

    def plot_time_success(self):
        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                        result[fw][(-1, tp)] = {'num': list(), 'success': list(), 'runtime': list()}
                        for na in range(10, 110, 10):
                            ins_runtime = 0
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, -1, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)

                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                        ins_runtime += tmp_df['runtime'].sum()
                                        ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                        success_num += tmp_df.shape[0]
                                        total_num += 25

                                    else:
                                        ins_runtime += self.time_limit * 25
                                        total_num += 25
                            if total_num == 0:
                                mean_runtime = 0
                                success_rate = 0
                            else:
                                mean_runtime =  ins_runtime / total_num
                                success_rate = success_num / total_num

                            result[fw][(-1, tp)]['num'].append(na)
                            result[fw][(-1, tp)]['success'].append(success_rate)
                            result[fw][(-1, tp)]['runtime'].append(mean_runtime)
                    
                    else:  # for CBS
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], List[float]] = dict()
                        result[fw][(-1, tp)] = {'num': list(), 'success': list(), 'runtime': list()}
                        for na in range(10, 110, 10):
                            ins_runtime = 0
                            success_num = 0
                            total_num = 0
                            for scen in self.scen_list:
                                for sid in self.sid_dict[scen]:
                                    tmp_dir = self.getFileDir(tp, -1, na)
                                    tmp_file = self.getFileName(scen, fw, tp, sid, -1, na)
                                    
                                    if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                        tmp_df = self.getCSVIns(scen, fw, tp, sid, -1, na)
                                        ins_runtime += tmp_df['runtime'].sum()
                                        ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                        success_num += tmp_df.shape[0]
                                        total_num += 25

                                    else:
                                        ins_runtime += self.time_limit * 25
                                        total_num += 25

                            if total_num == 0:
                                mean_runtime = 0
                                success_rate = 0
                            else:
                                mean_runtime =  ins_runtime / total_num
                                success_rate = success_num / total_num

                            result[fw][(-1, tp)]['num'].append(na)
                            result[fw][(-1, tp)]['success'].append(success_rate)
                            result[fw][(-1, tp)]['runtime'].append(mean_runtime)
                        
            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        if fw not in result.keys():
                            result[fw]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                        for mth in self.merge_th:
                            result[fw][(mth, tp)] = {'num': list(), 'success': list(), 'runtime': list()}
                            for na in range(10, 110, 10):
                                ins_runtime = 0
                                success_num = 0
                                total_num = 0
                                for scen in self.scen_list:
                                    for sid in self.sid_dict[scen]:
                                        tmp_dir = self.getFileDir(tp, mth, na)
                                        tmp_file = self.getFileName(scen, fw, tp, sid, mth, na)
                                    
                                        if os.path.exists(os.path.join(tmp_dir, tmp_file)):
                                            tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, na)
                                            ins_runtime += tmp_df['runtime'].sum()
                                            ins_runtime += self.time_limit * (25 - tmp_df.shape[0])
                                            success_num += tmp_df.shape[0]
                                            total_num += 25
                                        else:
                                            ins_runtime += self.time_limit * 25
                                            total_num += 25

                                if total_num == 0:
                                    mean_runtime = 0
                                    success_rate = 0
                                else:
                                    mean_runtime =  ins_runtime / total_num
                                    success_rate = success_num / total_num

                                result[fw][(mth, tp)]['num'].append(na)
                                result[fw][(mth, tp)]['success'].append(success_rate)
                                result[fw][(mth, tp)]['runtime'].append(mean_runtime)

        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Runtime-Success rate on ' + self.map_name
        # plt.title(fig_title, fontsize=self.title_size)
        idx = 0
        for tp in self.cbs_types:
            if tp == 'ECBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        tmp_label = tp + '(w=' + str(fw) + ')'
                        plt.plot(result[fw][(-1, tp)]['runtime'], result[fw][(-1, tp)]['success'], linewidth=self.lw, 
                            color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1
                    else:
                        tmp_label = 'CBS'
                        plt.plot(result[fw][(-1, tp)]['runtime'], result[fw][(-1, tp)]['success'], linewidth=self.lw, 
                            color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                        idx += 1

            elif tp == 'MACBS':
                for fw in self.focal_w:
                    if fw > 1.00:
                        for mth in self.merge_th:
                            tmp_label = tp + '(w=' + str(fw) + ', b=' + str(mth) + ')'
                            plt.plot(result[fw][(mth, tp)]['runtime'], result[fw][(mth, tp)]['success'], linewidth=self.lw, 
                                color=self.colors[idx], marker=self.marks[idx], ms=self.ms, label=tmp_label, zorder=idx)
                            idx += 1

        # plt.grid(True)
        ax.yaxis.grid(True)

        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
        }

        plt.rcParams.update(params)
        plt.xlabel('Runtime (sec)', fontsize=self.label_size)

        min_success = np.inf
        for r_fw in result.values():
            for r_tp in r_fw.values():
                if min(r_tp['success']) < min_success:
                    min_success = min(r_tp['success'])

        plt.yticks(np.arange(0.0, 1.05, 0.1))
        plt.ylabel('Success Rate', fontsize=self.label_size)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='lower left')

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_time_succ.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()
        return

    def plot_runtime_accu_ins(self):
        # plot figure
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        
        # fig_title: str = 'Runtime under ' + r'$w_{focal}=$' + str(self.focal_w[0]) + \
        #     ' for '+ str(self.num_of_agent) + ' agents on ' + self.map_name
        # plt.title(fig_title, fontsize=self.title_size)

        result: Dict[float, Dict[Tuple[int, str], Dict[str, List[float]]]] = dict()
        for scen_idx in [0, 1]:
            for tp in self.cbs_types:
                if tp == 'ECBS' or tp == 'CBS':
                    mth = -1

                    __df = self.getCSVIns(scen_name=self.scen_list[scen_idx], f_weight=self.focal_w[0], cbs_type=tp, 
                        sid=self.sid_dict[self.scen_list[scen_idx]][0], merge_th=mth, num_of_ag=self.num_of_agent)
                    if self.focal_w[0] not in result.keys():
                        result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                    for _, row in __df.iterrows():
                        if (mth, tp) not in result[self.focal_w[0]].keys():
                            result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                        tmp_ratio = row['runtime']
                        if tmp_ratio == 0:
                            tmp_ratio = np.inf
                        if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                            result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                        result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])
                else:
                    for mth in self.merge_th:
                        __df = self.getCSVIns(self.scen_list[scen_idx], self.focal_w[0], tp, 
                            self.sid_dict[self.scen_list[scen_idx]][0], mth, self.num_of_agent)
                        if self.focal_w[0] not in result.keys():
                            result[self.focal_w[0]]: Dict[Tuple[int, str], Dict[str, List[float]]] = dict()
                        for _, row in __df.iterrows():
                            if (mth, tp) not in result[self.focal_w[0]].keys():
                                result[self.focal_w[0]][(mth, tp)]: Dict[float, List[str]] = dict()
                            tmp_ratio = row['runtime']
                            if tmp_ratio == 0:
                                tmp_ratio = np.inf
                            if tmp_ratio not in result[float(self.focal_w[0])][(mth, tp)].keys():
                                result[self.focal_w[0]][(mth, tp)][tmp_ratio] = list()
                            result[self.focal_w[0]][(mth, tp)][tmp_ratio].append(row['instance name'])

        for plot_id, m_tp in enumerate(result[self.focal_w[0]].keys()):
            if m_tp[0] < 0:
                tmp_label = m_tp[1]
                plot_id += 10
            else:
                tmp_label = m_tp[1] + '(b=' + str(m_tp[0]) + ')'
            # ans_list: List[float] = sorted(result[self.focal_w[0]][m_tp].keys())
            ans_list = list()
            for r in sorted(result[self.focal_w[0]][m_tp].keys()):
                ans_list.append(np.log(r))
            plt.plot(ans_list, np.arange(len(ans_list)) + 1, linewidth=self.lw, color=self.colors[self.tmp_tp[m_tp]],
                marker=self.marks[self.tmp_tp[m_tp]], ms=self.ms, label=tmp_label, zorder=plot_id)

        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend(loc='best', fontsize=self.legend_size)
        ax.yaxis.grid(True)
        plt.xlabel('log Runtime (sec)', fontsize=self.label_size)
        plt.ylabel('# Instances', fontsize=self.label_size)
        plt.show()
        return

    def plot_weight_subopt(self):
        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        ax.yaxis.grid(True)

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
            'axes.labelsize': self.label_size,
        }

        plt.rcParams.update(params)
        plt.ylabel('Avg. Soc/' + r'$f_{min}$', fontsize=self.label_size)
        plt.xlabel(r'$w_{focal}$', fontsize=self.label_size)
        plt.xticks(self.focal_w)
        ax.tick_params(labelsize=self.num_size, width=3)

        common_ins: Dict[Tuple[str, int], List[str]] = dict()
        in_map = None
        for scen in self.scen_list:
            for sid in self.sid_dict[scen]:
                df_list: List[pd.DataFrame] = list()
                for fw in self.focal_w:
                    for tp in self.cbs_types:
                        if tp == 'ECBS':
                            tmp_df = self.getCSVIns(scen, fw, tp, sid, in_map)
                            df_list.append(tmp_df['instance name'])
                        elif tp == 'MACBS' or tp == 'MAECBS':
                            for mth in self.merge_th:
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, mth, in_map)
                                df_list.append(tmp_df['instance name'])

                in_common = reduce(np.intersect1d, df_list)
                in_common = in_common.tolist()
                common_ins[(scen, sid)] = in_common

        result = dict()
        for tp in self.cbs_types:            
            if tp == 'ECBS':
                r_idx = (-1, tp)
                if r_idx not in result.keys():
                    result[r_idx] = dict()
                for fw in self.focal_w:                    
                    _df = pd.DataFrame()
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_ins = self.getCSVIns(scen, fw, tp, sid)
                            cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                            tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                            _df = _df.append(tmp_ins, ignore_index=True)

                    print(_df.shape)

                    tmp_ratio = 0.0
                    for _, row in _df.iterrows():
                        tmp_ratio += row['solution cost'] / row['min f value']
                    tmp_ratio /= _df.shape[0]
                    result[r_idx][fw] = tmp_ratio

            elif tp == 'MACBS':
                for mth in self.merge_th:
                    r_idx = (mth, tp)
                    if r_idx not in result.keys():
                        result[r_idx] = dict()
                    for fw in self.focal_w:                    
                        _df = pd.DataFrame()
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_ins = self.getCSVIns(scen, fw, tp, sid, mth)
                                cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                                tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                                _df = _df.append(tmp_ins, ignore_index=True)

                        print(_df.shape)

                        tmp_ratio = 0.0
                        for _, row in _df.iterrows():
                            tmp_ratio += row['solution cost'] / row['min f value']
                        tmp_ratio /= _df.shape[0]
                        result[r_idx][fw] = tmp_ratio


            elif tp == 'MAECBS':
                for mth in self.merge_th:
                    r_idx = (mth, tp)
                    if r_idx not in result.keys():
                        result[r_idx] = dict()
                    for fw in self.focal_w:                    
                        _df = pd.DataFrame()
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_ins = self.getCSVIns(scen, fw, tp, sid, mth)
                                cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                                tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                                _df = _df.append(tmp_ins, ignore_index=True)

                        print(_df.shape)

                        tmp_ratio = 0.0
                        for _, row in _df.iterrows():
                            tmp_ratio += row['solution cost'] / row['min f value']
                        tmp_ratio /= _df.shape[0]
                        result[r_idx][fw] = tmp_ratio

        idx = 0
        for tp in self.cbs_types:
            if tp == 'ECBS':
                plt.plot(list(result[(-1, tp)].keys()), list(result[(-1, tp)].values()), linewidth=self.lw, 
                    color=self.colors[self.tmp_tp[(-1, tp)]], marker=self.marks[self.tmp_tp[(-1, tp)]], ms=self.ms, label=tp, zorder=idx+10)
                idx += 1
            elif tp == 'MACBS' or tp == 'MAECBS':
                for mth in self.merge_th:
                    tmp_la = tp + '(b=' + str(mth) + ')'
                    plt.plot(list(result[(mth, tp)].keys()), list(result[(mth, tp)].values()), linewidth=self.lw, 
                        color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_la, zorder=idx)
                    idx += 1

        ax.legend()
        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_weight_subopt.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()

    def plot_weight_runtime(self):
        common_ins: Dict[Tuple[str, int], List[str]] = dict()
        for scen in self.scen_list:
            for sid in self.sid_dict[scen]:
                df_list: List[pd.DataFrame] = list()
                for fw in self.focal_w:
                    for tp in self.cbs_types:
                        if tp == 'ECBS':
                            tmp_df = self.getCSVIns(scen, fw, tp, sid)
                            df_list.append(tmp_df['instance name'])
                        elif tp == 'MACBS' or tp == 'MAECBS':
                            for mth in self.merge_th:
                                tmp_df = self.getCSVIns(scen, fw, tp, sid, mth)
                                df_list.append(tmp_df['instance name'])

                in_common = reduce(np.intersect1d, df_list)
                in_common = in_common.tolist()
                common_ins[(scen, sid)] = in_common

        result = dict()
        for tp in self.cbs_types:            
            if tp == 'ECBS':
                r_idx = (-1, tp)
                if r_idx not in result.keys():
                    result[r_idx] = dict()
                for fw in self.focal_w:                    
                    _df = pd.DataFrame()
                    for scen in self.scen_list:
                        for sid in self.sid_dict[scen]:
                            tmp_ins = self.getCSVIns(scen, fw, tp, sid)
                            cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                            tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                            _df = _df.append(tmp_ins, ignore_index=True)

                    print(_df.shape)

                    tmp_ratio = 0.0
                    for _, row in _df.iterrows():
                        tmp_ratio += row['runtime']
                    tmp_ratio /= _df.shape[0]
                    result[r_idx][fw] = tmp_ratio

            elif tp == 'MACBS':
                for mth in self.merge_th:
                    r_idx = (mth, tp)
                    if r_idx not in result.keys():
                        result[r_idx] = dict()
                    for fw in self.focal_w:                    
                        _df = pd.DataFrame()
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_ins = self.getCSVIns(scen, fw, tp, sid, mth)
                                cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                                tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                                _df = _df.append(tmp_ins, ignore_index=True)

                        print(_df.shape)

                        tmp_ratio = 0.0
                        for _, row in _df.iterrows():
                            tmp_ratio += row['runtime']
                        tmp_ratio /= _df.shape[0]
                        result[r_idx][fw] = tmp_ratio


            elif tp == 'MAECBS':
                for mth in self.merge_th:
                    r_idx = (mth, tp)
                    if r_idx not in result.keys():
                        result[r_idx] = dict()
                    for fw in self.focal_w:                    
                        _df = pd.DataFrame()
                        for scen in self.scen_list:
                            for sid in self.sid_dict[scen]:
                                tmp_ins = self.getCSVIns(scen, fw, tp, sid, mth)
                                cond = tmp_ins['instance name'].isin(common_ins[(scen, sid)]) == False
                                tmp_ins = tmp_ins.drop(tmp_ins[cond].index)
                                _df = _df.append(tmp_ins, ignore_index=True)

                        print(_df.shape)

                        tmp_ratio = 0.0
                        for _, row in _df.iterrows():
                            tmp_ratio += row['runtime']
                        tmp_ratio /= _df.shape[0]
                        result[r_idx][fw] = tmp_ratio

        f = plt.figure(num=None, figsize=(self.fig_h, self.fig_w), dpi=80, facecolor='w', edgecolor='k')
        ax = f.add_subplot(111)
        ax.tick_params(labelright=False)
        ax.yaxis.grid(True)

        idx = 0
        for tp in self.cbs_types:
            if tp == 'ECBS':
                plt.plot(list(result[(-1, tp)].keys()), list(result[(-1, tp)].values()), linewidth=self.lw, 
                    color=self.colors[self.tmp_tp[(-1, tp)]], marker=self.marks[self.tmp_tp[(-1, tp)]], ms=self.ms, label=tp, zorder=idx+10)
                idx += 1
            elif tp == 'MACBS' or tp == 'MAECBS':
                for mth in self.merge_th:
                    tmp_la = tp + '(b=' + str(mth) + ')'
                    plt.plot(list(result[(mth, tp)].keys()), list(result[(mth, tp)].values()), linewidth=self.lw, 
                        color=self.colors[self.tmp_tp[(mth, tp)]], marker=self.marks[self.tmp_tp[(mth, tp)]], ms=self.ms, label=tmp_la, zorder=idx)
                    idx += 1

        params = {
            'legend.fontsize': self.legend_size,
            'legend.handlelength': 2,
            'axes.labelsize': self.label_size,
        }

        plt.rcParams.update(params)
        plt.ylabel('Avg. Runtime (sec)', fontsize=self.label_size)
        plt.xlabel(r'$w_{focal}$', fontsize=self.label_size)
        plt.xticks(self.focal_w)
        ax.tick_params(labelsize=self.num_size, width=3)
        ax.legend()

        out_file: str = self.map_name + '_' + str(self.num_of_agent) + '_weight_subopt.png'
        plt.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), out_file))
        plt.show()


    def plot_fig(self):
        if self.todo_function == 'plot_time_soc':
            dp.plot_time_soc()
        elif self.todo_function == 'plot_num_success':
            dp.plot_num_success()
        elif self.todo_function == 'plot_num_runtime':
            dp.plot_num_runtime()
        elif self.todo_function == 'plot_time_success':
            dp.plot_time_success()
        elif self.todo_function == 'plot_ins_ratio':
            __ins = dp.plot_ins_ratio()
            dp.plot_ins_runtime(__ins)
        elif self.todo_function == 'plot_ins_runtime':
            dp.plot_ins_runtime()
        elif self.todo_function == 'plot_runtime_accu_ins':
            dp.plot_runtime_accu_ins()
        elif self.todo_function == 'plot_weight_subopt':
            dp.plot_weight_subopt()
        elif self.todo_function == 'plot_weight_runtime':
            dp.plot_weight_runtime()

                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Take config.yaml as input!')
    parser.add_argument('--config', type=str, default='config.yaml')

    args = parser.parse_args()

    # Create data processor
    dp = DataProcessor(args.config)
    dp.plot_fig()
    # dp.plot_time_soc()
    # dp.plot_num_success()
    # dp.plot_num_runtime()
    # dp.plot_time_success()
