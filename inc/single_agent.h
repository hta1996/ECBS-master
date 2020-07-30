#pragma once
#include "node.h"
#include "grid2D.h"

class SingleAgentPlanner 
{
private:
	// define typedefs (will also be used in ecbs)
	// note -- handle typedefs is defined inside the class (hence, include node.h is not enough).
	typedef pairing_heap< Node*, compare<Node::compare_node> > heap_open_t;
	typedef pairing_heap< Node*, compare<Node::secondary_compare_node> > heap_focal_t;
	typedef unordered_set<Node*, Node::NodeHasher, Node::eqnode> hashtable_t;
	heap_open_t open_list;
	heap_focal_t focal_list;
	hashtable_t allNodes_table;

	void clear();
	int extractLastGoalTimestep(int goal_location, const vector< list< tuple<int, int, bool> > >* cons);
	void releaseClosedListNodes(hashtable_t& allNodes_table);
	bool isConstrained(int curr_id, int next_id, int next_timestep,
		const vector< list< tuple<int, int, bool> > >* cons) const;
	void updatePath(Node* goal);
	int numOfConflictsForStep(int curr_id, int next_id, int next_timestep, const CAT& res_table, size_t map_size);
	void updateFocalList(double old_lower_bound, double new_lower_bound, double f_weight);

public:
	bool runFocalSearch(const Grid2D& G, int agent_id, double f_weight, const vector < list< tuple<int, int, bool> > >* constraints,
		const CAT& res_table); // the original ECBS low-level search


	SingleAgentPlanner(size_t map_size, int max_makespan): map_size(map_size), max_makespan(max_makespan) {}

	vector<pathEntry> path;  // a path that takes the agent from initial to goal location satisying all constraints
	int path_cost;  
	double lower_bound;  // lower bound of FOCAL list ( = e_weight * min_f_val)
	int min_f_val;  // min f-val seen so far
	int num_of_conf;

	const size_t map_size;
    const int max_makespan;

	uint64_t num_expanded;
	uint64_t num_generated;
};