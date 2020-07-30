# Bounded Sub-optimal Nested CBS
This work combines both MACBS and ECBS to come up with a novel searching algorithm called Nested (E)CBS for solving MAPF problem.

## Installation 
The code requires the external library: BOOST (https://www.boost.org/).

One also needs to fit your own cmake version, current version in CMakeList.txt is 3.16.5 (2.8.12 is also suitable).

### To compile the code:
```
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

### To run the code:
```
# for running a single instance
./build/ECBS -m [PATH_TO_MAP] -a [PATH_TO_SCEN] -n [NumberOfAgents] -o [OutputFIle] -t [TimeLimit] -w [FocalWeight] -b [MergeThreshold] -s [MODE] -i [StartAgentIDForScenFile] --debug [true/false] --maecbs [true/false]
# for running the whole experiment
nohup sh ./run_benchmark.sh &
```


### To run the code on USC-HPC:
Check https://hackmd.io/@shaohungchan/Hkfg1XuGI for details.


## Required Inputs:

  -m [ --map ]        : Input file for map (*string*)
  
  -a [ --agents ]     : Input file for agents (*string*)

  -n [ --agentNum ]   : Number of agents (*int*)
  
  -o [ --output ]     : Output file for schedule (*string*)

  -s [ --solver ]     : Solver to use (*int*, 0: EPEA\*, 1: CBS, 2: ECBS, 3: MA-CBS(EPEA\*), 4: MA-CBS(CBS), 5: MA-ECBS, 6: MA-ECBS(EPEA\*), 7: MA-ECBS(CBS), 8: Evaluate path.txt)
 
 ## Optional Inputs:

  -w [ --weight ]     : Suboptimal bound for ECBS (*float*, default: 1.00)
  
  -b [ --mergeTh ]    : Merge Threshold for MACBS and MAECBS (*int*, default: 1)

  -t [ --cutoffTime ] : Cutoff time (seconds) (*int*, default: 300)

  -i [ --startID ]    : Start id for the benchmark files (*int*, default: 0)

  --mr                : Whether to use merge and restart technique (*bool*, default: false)

  --ro                : Whether to restart, only for NECBS. This is triggered by merging process. (*bool*, default: false)

  --rt                : Times to restart randomly under cutoff time. This is triggered by time. (*int*, default: 0)

  -c [--conf]         : Methods to choose a conflict during CBS(ECBS) branching (*int*, 0: Random, 1: Smallest sum of agent size, default: 0)

  --sConf             : Methods to choose a conflict for CBS(ECBS) as MA-solver (*int*, 0: Random, 1: Smallest sum of agent size, default: 0)

  --makespan          : Maximum makespan for single agent solver (*int*, default: INT_MAX)

  --seed              : Random seed (*int*, default: 0)

  --debug             : Debug mode (*int*, 0: Nothing, 1: Print all output, 2: Print HL and LL nodes, default: 0)
  
  --help              : Produce help message