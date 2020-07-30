#! /usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import yaml
import numpy as np

# ins_dict = {
#     'num_of_agent': 20,
#     'map_name': 'random-32-32-20',
#     'focal_w': [1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09, 
#         1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00],
#     'merge_th': [1, 2, 3, 4, 5],
#     'cbs_types': ['ECBS', 'MACBS'],
#     'scen_dict': {'even': [0, 5, 20]}
# }

# ins_dict = {
#     'num_of_agent': 50,
#     'map_name': 'random-32-32-20',
#     'focal_w': [1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00],
#     'merge_th': [1, 10],
#     'cbs_types': ['ECBS', 'MACBS'],
#     'scen_dict': {'even': [0, 50]}
# }

ins_dict = {
    'num_of_agent': 20,
    'map_name': 'empty-32-32',
    'focal_w': [1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00],
    'merge_th': [1, 10],
    'cbs_types': ['ECBS', 'MACBS'],
    'scen_dict': {'even': [0]}
}

file_name = ins_dict['map_name'] + '_' + str(ins_dict['num_of_agent']) + '_config.yaml'
with open(file_name, 'w') as fout:
    yaml.dump(ins_dict, fout)
