#!/bin/bash
echo "Running Experiments: MAECBS_ro"

name="warehouse-20-40-10-2-1"
map="../../../mapf_benchmark/mapf-map/$name.map"
scen1="even"
scen="../../../mapf_benchmark/scen-$scen1/$name-$scen1"
output="/scratch/shaohung/my_exp2/$name/$name-$scen1"
time=300

for sid in 0
do
    for b in 10
    do
        for n in $(seq 10 10 100)
        do
            for w in $(seq 1.01 0.1 1.01)
            do
                for i in $(seq 1 1 25)
                do
                    echo "$n agents on instance $name-$scen1-$i  w=$w  b=$b sid=$sid"
                    ../../build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_mr.csv -t $time -w $w -b $b -s 5 -i $sid --debug 0 --ro true
                done
            done
        done
    done
done