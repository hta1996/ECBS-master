#pragma once
#include "common.h"
#include "grid2D.h"
#include "node.h"

#include <google/dense_hash_map>

#include <boost/heap/fibonacci_heap.hpp>
using boost::heap::fibonacci_heap;

class EPEANode
{
public:
    list<int> agent_id;
	int index;

	uint64_t time_expanded;
	uint64_t time_generated;

	// Parameters for EPEA
	EPEANode* parent = nullptr;
	int makespan;
	vector<int> locs;
	vector<int16_t> arrival_time;
	int g_val;  // Sum of individual cost (total cost)
    int h_val;  
	
	int num_of_collisions;  // For tie breaking

    bool alreadyExpanded = false;
	int targetDeltaF = 0;  // Starts at zero, incremented after a node is expanded once. Set on Expand.
	int remainingDeltaF = 0;  // Remaining delta F towards targetDeltaF. Reset on Expand.
	int maxDeltaF = 0;  // Only computed on demand

	list<pair<int, int>> vertex_cons;
	list<pair<int, int>> edge_cons;

    // For each agent and each direction it can go, the effect of that move on F
    // INT16_MAX means this is an illegal move. Only computed on demand.
	typedef vector<list<pair<int16_t, int16_t>>> SingleAgentDeltaFs;
	std::shared_ptr<SingleAgentDeltaFs> singleAgentDeltaFs;

	// Per each agent and delta F, has 1 if that delta F is achievable by moving the agents starting from this one on,
	// 2 if it isn't, and 0 if we don't know yet.
	vector<vector<int16_t>> fLookup; 

    // The following is used to comapre nodes in the OPEN list
	struct compare_node 
	{
		bool operator()(const EPEANode* n1, const EPEANode* n2) const
		{
			if (n1->g_val + n1->h_val + n1->targetDeltaF == n2->g_val + n2->h_val + n2->targetDeltaF)
				if (n1->num_of_collisions == n2->num_of_collisions)
					return n1->h_val + n1->targetDeltaF > n2->h_val + n2->targetDeltaF;
				else
					return n1->num_of_collisions > n2->num_of_collisions;
			else
				return n1->g_val + n1->h_val + n1->targetDeltaF > n2->g_val + n2->h_val + n2->targetDeltaF;
		}
	};

	// The following is used by googledensehash for checking whether two nodes are equal
	// we say that two nodes, s1 and s2, are equal if
	// both are non-NULL and have the same time_expanded (unique)
	struct epea_eqnode 
	{
		bool operator()(const EPEANode* s1, const EPEANode* s2) const 
		{
			if (s1 == s2)
				return true;
			else if (!s1 || !s2 || s1->makespan != s2->makespan)
				return false;
			else
			{
				for (int i = 0; i < (int)s1->locs.size(); i++)
					if (s1->locs[i] != s2->locs[i])
						return false;
				return true;
			}
		}
	};

	// The following is used by googledensehash for generating the hash value of a nodes
	// this is needed because otherwise we'll have to define the specialized template inside std namespace
	// this hasher is different than that in ECBS
	// change hash to boost::hash
	struct EPEANodeHasher 
	{
		size_t operator()(const EPEANode* n) const 
		{
			size_t timestep_hash = boost::hash<int>()(n->makespan);
			size_t sum_of_locs = 0;
			for (int i = 0; i < (int)n->locs.size(); i++)
			{
				sum_of_locs += n->locs[i];
			}
			size_t loc_hash = boost::hash<int>()(sum_of_locs);
			return (loc_hash ^ (timestep_hash << 1));
		}
	};

	// The following is used by googledensehash for generating the hash value of a nodes
    typedef fibonacci_heap< EPEANode*, boost::heap::compare<compare_node>>::handle_type open_handle_t;
	open_handle_t open_handle;
	bool in_openlist;

    EPEANode();
	EPEANode(const Grid2D& in_G, const vector<bool>& in_ma_vec);  // this is for root node
	~EPEANode();

	bool operator==(const EPEANode& rhs) const;

	void deep_copy(const EPEANode &cpy);  // copy
	void update(const EPEANode &cpy);  // Update stats, used in duplicate detection.
	void clear();
	void clearConstraintTable();
	void calcSingleAgentDeltaFs(const Grid2D& in_G, const vector<list<Constraint>>& init_cons, const vector<bool>& in_ma_vec);

	bool isMoveValid(const Grid2D& in_G, int in_agent_id, int curr_loc, int next_loc, const vector<bool>& in_ma_vec) const;
	void moveTo(const Grid2D& in_G, int agent_id, int next_loc, const CAT& in_cat, const vector<bool>&);
	vector<vector<int>> getPlan(const Grid2D& in_G, const vector<bool>& in_ma_vec);

    void printNode()
	{
		cout << "--------------------Start--------------------" << endl;
		cout << "idx:" << index << ", alreadyExpanded?" << alreadyExpanded << endl;
		cout << "makespan:" << makespan << ", g:" << g_val << ", h:" << h_val << ", targetDeltaF:" << targetDeltaF << ", num_of_collisions:" << num_of_collisions << endl;
		if (parent != nullptr)
			cout << "[parent] idx:" << parent->index << ", makespan:" << parent->makespan << ", g:" << parent->g_val << ", h:" << parent->h_val << endl;
		cout << "locs: ";
		for (size_t i = 0; i < locs.size(); i++)
		{
			cout << locs[i] << ", ";
		}
		cout << endl;
		cout << "time_generates: " << time_generated << ", time_expanded: " << time_expanded << endl;
		cout << "---------------------END---------------------" << endl;
	}
};