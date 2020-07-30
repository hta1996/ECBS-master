#pragma once
#include "basic_solver.h"
#include "epea_node.h"

using google::dense_hash_map;

class EPEA:
	public BasicSolver
{
public:
	double solution_depth = 0;
	vector<vector<int>> epea_paths;  // Agents paths, need to change to vector<Path*> and return to MACBS

	EPEA(const Grid2D& in_G, int k_robust, int screen, double time_limit, bool in_is_solver);
	~EPEA();
	string get_name(void) const;
	void printResults(void) const;
    void saveResults(const string& file_name, const string& instance_name) const;
	bool run(list<agent_info> ma_info, list<Path*> in_other_paths);

private:

	const int maxCost = INT_MAX;
	typedef fibonacci_heap< EPEANode*, compare<EPEANode::compare_node> > heap_open_t;
	heap_open_t open_list;

	typedef dense_hash_map<EPEANode*, EPEANode*, EPEANode::EPEANodeHasher, EPEANode::epea_eqnode> hashtable_t;
	hashtable_t allNodes_table;

	int initialEstimate;

	vector<list<Constraint>> initial_constraints;  // Input: agent_id -> Output: list<Constraint>
	vector<int> minLengths;

	// Used in hash table and would be deleted from the destructor
	EPEANode* empty_node;
	EPEANode* deleted_node;

	list<Constraint> getMAConstraints(vector<list<tuple<int, int, bool>>>* ma_cons);
	list<EPEANode*> expandOneAgent(list<EPEANode*>& intermediateNodes, int in_agent_id, int start_agent_id);
	void expandNode(EPEANode& node);
	void initialClear(void);
	void transformPath(void);
	void clearAllNodesTable(void);
};
