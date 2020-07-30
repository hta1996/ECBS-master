#!/bin/bash
echo "Running Experiments: Benchmark"

name="random-32-32-20"
scen1="even"
map="../mapf_benchmark/mapf-map/$name.map"
scen="../mapf_benchmark/scen-$scen1/$name-$scen1"
output="../my_exp/$name/$name-$scen1"
time=60
sid=0
w=1.05
b=10

for n in $(seq 50 10 50)
do
    for i in $(seq 1 1 22)
    do
        echo "$n agents on instance $name-even-$i  w=$w  sid=$sid"
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-1.00-$sid-CBS.csv -t $time -w 1.00 -s 1 -i $sid --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-ECBS.csv -t $time -w $w -s 2 -i $sid --debug 0  --rt 5
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-1.00-$sid-$b-MACBS_EPEA.csv -t $time -w 1.00 -b $b -s 3 -i $sid --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-1.00-$sid-$b-MACBS_EPEA_mr.csv -t $time -w 1.00 -b $b -s 3 -i $sid --mr true --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS.csv -t $time -w $w -b $b -s 5 -i $sid --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_mr.csv -t $time -w $w -b $b -s 5 -i $sid --mr true --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_mr1.csv -t $time -w $w -b $b -s 5 -i $sid --mr true --debug 0 -c 1 --sConf 1
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_EPEA.csv -t $time -w $w -b $b -s 6 -i $sid --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MAECBS_EPEA_mr.csv -t $time -w $w -b $b -s 6 -i $sid --mr true --debug 0
        ./build/ECBS -m $map -a $scen-$i.scen -n $n -o $output-$n-$w-$sid-$b-MACBS_ro.csv -t $time -w 1.00 -b $b -s 4 -i $sid --ro true --debug 0
    done
done
