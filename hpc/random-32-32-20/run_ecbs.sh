#!/bin/bash
echo "Running Experiments: ECBS"

name="random-32-32-20"
map="../../../mapf_benchmark/mapf-map/$name.map"
scen1="even"
scen="../../../mapf_benchmark/scen-$scen1/$name-$scen1"
output="/scratch/shaohung/my_exp/$name/$name-$scen1"
time=300

for sid in 0
do
    for n in $(seq 10 10 100)
    do
        for w in $(seq 1.05 0.01 1.05)
        do
            for i in $(seq 1 1 25)
            do
                echo "$n agents on instance $name-$scen1-$i  w=$w  sid=$sid"
                ../../build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-ECBS.csv -t $time -w $w -s 2 -i $sid --debug 0
            done
        done
    done
done