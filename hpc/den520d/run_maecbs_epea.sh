#!/bin/bash
echo "Running Experiments: MAECBS_EPEA"

name="den520d"
map="../../../mapf_benchmark/mapf-map/$name.map"
scen1="even"
scen="../../../mapf_benchmark/scen-$scen1/$name-$scen1"
output="/staging/sc3/shaohung/my_exp/$name/$name-$scen1"
time=300

for sid in 0
do
    for b in 1
    do
        for n in $(seq 50 50 250)
        do
            for w in $(seq 1.01 0.1 1.01)
            do
                for i in $(seq 1 1 25)
                do
                    echo "$n agents on instance $name-$scen1-$i  w=$w  b=$b sid=$sid"
                    ../../build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_EPEA.csv -t $time -w $w -b $b -s 6 -i $sid --debug 0
                done
            done
        done
    done
done