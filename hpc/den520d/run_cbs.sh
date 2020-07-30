#!/bin/bash
echo "Running Experiments: CBS"

name="den520d"
map="../../../mapf_benchmark/mapf-map/$name.map"
scen1="even"
scen="../../../mapf_benchmark/scen-$scen1/$name-$scen1"
output="/staging/sc3/shaohung/my_exp/$name/$name-$scen1"
time=300
w=1.00

for sid in 0
do
    for n in $(seq 50 50 250)
    do
        for i in $(seq 1 1 25)
        do
            echo "$n agents on instance $name-$scen1-$i  w=$w  sid=$sid"
            ../../build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-CBS.csv -t $time -w $w -s 1 -i $sid --debug 0
        done
    done
done