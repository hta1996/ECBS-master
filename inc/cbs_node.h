#pragma once
#include "node.h"

class CBSNode 
{
public:
	list<int> agent_id;
	Constraint constraint; 
	list<std::shared_ptr<Conflict>> conflicts;

	// MA-CBS
	list<list<int>> meta_agents;
    vector<bool> ma_vec;

	CBSNode* parent = nullptr;
	list<tuple<int, vector<pathEntry>, int, int>> paths_updated; // Agent id + new path + cost + lower bound
	int g_val;  // Sum of individual cost (total cost)
	int num_of_collisions;
	int sum_min_f_vals;  // Saves the overall sum of min f-vals.

	uint64_t time_expanded;
	uint64_t time_generated;


	// The following is used to comapre nodes in the OPEN list
	struct compare_node 
	{
		bool operator()(const CBSNode* n1, const CBSNode* n2) const
		{
			if (n1->g_val == n2->g_val)
				return n1->num_of_collisions >= n2->num_of_collisions;
			return n1->g_val >= n2->g_val;		
		}
	};  // Used by OPEN to compare nodes by sum_min_f_vals (top of the heap has min sum_min_f_vals)

	typedef boost::heap::pairing_heap< CBSNode* , boost::heap::compare<compare_node> >
		::handle_type open_handle_t;
	open_handle_t open_handle;

	// The following is used by googledensehash for generating the hash value of a nodes
	// This is needed because otherwise we'll have to define the specialized template inside std namespace
	struct CBSNodeHasher
	{
		std::size_t operator()(const CBSNode* n) const
		{
			size_t agent_id_hash = 17;
			for (auto it = n->agent_id.begin(); it != n->agent_id.end(); ++it)
            {
                std::cout << "it: " << *it << endl;
                agent_id_hash = agent_id_hash * 31 + *it;
            }
			size_t time_generated_hash = std::hash<uint64_t>()(n->time_generated);
			return ( agent_id_hash ^ (time_generated_hash << 1) );
		}
	};

	CBSNode():
		agent_id(list<int>{-1}), parent(nullptr), g_val(0), num_of_collisions(0), sum_min_f_vals(0), time_expanded(0), time_generated(0) {}

	void printNode()
	{
		cout << "--------------------Start--------------------" << endl;
		cout << "agent_id: ";
		for (const auto& ag: agent_id)
		{
			cout << ag << ", ";
		}
		cout << "| size: " << agent_id.size() << endl;

		if (agent_id.front() == -1)
		{
			cout << "Root node!!!" << endl;
		}

		bool all_true = std::all_of(ma_vec.begin(), ma_vec.end(), [](bool v){return v;});
		if (!all_true)  // Solver nodes
		{
			cout << "Agents: ";
			for (const auto& ag_list: meta_agents)
			{
				cout << "[";
				for (const auto& ag: ag_list)
					cout << ag << " ";
				cout << "], ";
			}
			cout << endl;
		}

		cout << "g_val:" << g_val << ", fmin: " << sum_min_f_vals << ", num_of_collisions:" << num_of_collisions << endl;
		cout << "constraints: ";
		cout << get<0>(constraint) << ", " << get<1>(constraint) << ", " << get<2>(constraint) << ", " << get<3>(constraint) << endl;
		cout << "conflicts size: " << conflicts.size() << endl;
		cout << "time_generates: " << time_generated << ", time_expanded: " << time_expanded << endl;
		if (parent != nullptr)  // Print parents index
			cout << "parent time_generates: " << parent->time_generated << endl;
		cout << "---------------------END---------------------" << endl;
	}
};


