#!/bin/bash
#SBATCH --constraint="IB&avx2&xeon&E5-2640v4&xl190r"
#SBATCH --ntasks=8
#SBATCH --time=23:59:00
#SBATCH --mem-per-cpu=2Gb
sh ./run_cbs.sh &
sh ./run_macbs_epea.sh &
sh ./run_macbs_epea_mr.sh &
sh ./run_ecbs.sh &
sh ./run_maecbs_epea.sh &
sh ./run_maecbs_epea_mr.sh &
sh ./run_maecbs.sh &
sh ./run_maecbs_mr.sh &
wait
