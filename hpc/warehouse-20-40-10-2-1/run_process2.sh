#!/bin/bash
#SBATCH --constraint="IB&avx2&xeon&E5-2640v4&xl190r"
#SBATCH --ntasks=8
#SBATCH --time=23:59:00
#SBATCH --mem-per-cpu=2Gb
sh ./run_maecbs_mr.sh &
sh ./run_maecbs_mr2.sh &
sh ./run_maecbs_mr3.sh &
sh ./run_maecbs_mr4.sh &
sh ./run_maecbs_ro.sh &
sh ./run_maecbs_ro2.sh &
sh ./run_maecbs_ro3.sh &
sh ./run_maecbs_ro4.sh &
wait
