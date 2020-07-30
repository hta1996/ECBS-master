#pragma once

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_traits.hpp>
#include <boost/heap/pairing_heap.hpp>
#include <boost/tokenizer.hpp>
#include <boost/unordered_set.hpp>
#include <boost/unordered_map.hpp>
#include <boost/format.hpp>

#include <cassert>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <vector>
#include <iostream>
#include <iomanip>
#include <list>
#include <vector>
#include <string>
#include <functional>  // for std::hash (c++11 and above)
#include <time.h>
#include <memory> // for std::shared_ptr
#include <map>
#include <cstring>
#include <cassert>
#include <fstream>
#include <algorithm>
#include <ctime>
#include <chrono>
#include <tuple>
#include <typeinfo>

using boost::heap::pairing_heap;
using boost::heap::compare;
using boost::unordered_map;
using boost::unordered_set;
using boost::format;

using std::string;
using std::vector;
using std::list;
using std::max;
using std::min;
using std::cout;
using std::endl;
using std::cerr;
using std::setw;
using std::ifstream;
using std::ofstream;
using std::pair;
using std::make_pair;
using std::tuple;
using std::make_tuple;
using std::tie;
using std::clock;
using std::clock_t;
typedef std::chrono::steady_clock::time_point time_pt;

// Default: use the true distance to the goal location of the agent
// DH: Differential Heuristics where all goal locations are used as pivots 
enum lowlevel_hval { DEFAULT, DH, LLH_COUNT };

enum conflict_type { CARDINAL, SEMICARDINAL, NONCARDINAL, CONFLICT_COUNT };

// <int loc1, int loc2, int t_min, int t_max, bool positive_constraint>
// NOTE loc2 = -1 for vertex constraints; loc2 = location2 for edge constraints
// [t_min, t_max) is the prohibited time range
typedef std::tuple<int, int, int, int, bool> Constraint;
std::ostream& operator<<(std::ostream& os, const Constraint& constraint);

// <int agent1, int agent2, int loc1, int loc2, int timestep>
// NOTE loc2 = -1 for vertex conflicts; loc2 = location2 for edge conflicts
typedef std::tuple<int, int, int, int, int> Conflict;
std::ostream& operator<<(std::ostream& os, const Conflict& conflict);


struct ConstraintState
{
	bool vertex = false;
	bool edge[5] = { false, false, false, false, false };
};

typedef vector< unordered_set< int > > CAT;  // vector[time] -> a set of locations

struct pathEntry
{
    int id;
};

// For meta agent
struct agent_info
{
    int agent_id;
    vector < list< tuple<int, int, bool> > >* constraints;
};

typedef vector<pathEntry> Path;
std::ostream& operator<<(std::ostream& os, const Path& path);

inline clock_t getDuration(time_pt start, time_pt end) 
{
    return std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
};