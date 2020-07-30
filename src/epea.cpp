#include "epea.h"

EPEA::EPEA(const Grid2D& in_G, int k_robust, int screen, double time_limit, bool in_is_solver):
	BasicSolver(in_G, k_robust, screen, time_limit, in_is_solver) 
{
	// initialize allNodes_table (hash table)
	empty_node = new EPEANode();
	empty_node->locs.push_back(-2);
	deleted_node = new EPEANode();
	deleted_node->locs.push_back(-3);
	allNodes_table.set_empty_key(empty_node);
	allNodes_table.set_deleted_key(deleted_node);
}

EPEA::~EPEA() {}

string EPEA::get_name(void) const
{
	string name = "EPEA";
	return name;
}

// print results
void EPEA::printResults(void) const
{
    if (runtime > time_limit)  // timeout
		cout << "Timeout  ; ";
	else if (open_list.empty() && solution_cost < 0)
		cout << "No solutions  ; ";
	else
		cout << ":) Succeed ; ";

	double out_runtime = (double) runtime / CLOCKS_PER_SEC;
	cout << "cost:" << solution_cost << "; runtime:" << out_runtime <<
        "; HL_nodes generates:" << HL_num_generated << "; HL_nodes expand:" << HL_num_expanded << endl;
}

void EPEA::saveResults(const string& file_name, const string& instance_name) const
{
	std::ifstream infile(file_name);
	bool exist = infile.good();
	infile.close();
	if (!exist)
	{
		ofstream addHeads(file_name);
		addHeads << "runtime,#high-level expanded,#high-level generated,#solver calls," << 
			"solution cost,runtime of detecting conflicts,runtime of building CATs," <<
			"runtime of path finding,runtime of generating child nodes,runtime of preprocessing,solver name,instance name" << endl;
		addHeads.close();
	}

	double out_runtime = (double) runtime / CLOCKS_PER_SEC;
    double out_runtime_generate_child = (double) runtime_generate_child / CLOCKS_PER_SEC;
	double out_runtime_build_CAT = (double) runtime_build_CAT / CLOCKS_PER_SEC;
	double out_runtime_path_finding = (double) runtime_path_finding / CLOCKS_PER_SEC;
	double out_runtime_detect_conflicts = (double) runtime_detect_conflicts / CLOCKS_PER_SEC;

	ofstream stats(file_name, std::ios::app);
	stats << out_runtime << "," << HL_num_expanded << "," << HL_num_generated << "," << solver_counter << "," <<
		solution_cost << "," << out_runtime_detect_conflicts << "," << out_runtime_build_CAT << "," <<
		out_runtime_path_finding << "," << out_runtime_generate_child << "," << G.pre_time << "," << get_name() << "," << instance_name << endl;
	stats.close();
}

list<Constraint> EPEA::getMAConstraints(vector<list<tuple<int, int, bool>>>* ma_cons)
{
	list<Constraint> out_cons;
	if (ma_cons != nullptr)
	{
		for (int t = 0; t < (int)ma_cons->size(); t++)
		{
			for (const auto& con_it: ma_cons->at(t))
			{
				// Check the constraint is already in the out_cons
				bool in_output = false;
				for (auto& out_it : out_cons)
				{
					if (get<0>(out_it) == get<0>(con_it) && get<1>(out_it) == get<1>(con_it))
					{
						in_output = true;
						if (t < get<2>(out_it))
							get<2>(out_it) = t;

						if ((t+1) > get<3>(out_it))
							get<3>(out_it) = t+1;
					}
				}
				if (!in_output)
				{
					Constraint tmp_cons = make_tuple(get<0>(con_it), get<1>(con_it), t, t+1, get<2>(con_it));
					out_cons.push_back(tmp_cons);
				}
			}
		}
	}
	return out_cons;
}

/// <summary>
/// Expands a single agent in the nodes.
/// This includes:
/// - Generating the children
/// - Inserting them into OPEN
/// - Insert node into CLOSED
/// Returns the child nodes
/// </summary>
list<EPEANode*> EPEA::expandOneAgent(list<EPEANode*>& intermediateNodes, int in_agent_id, int start_agent_id)
{
	time_pt tstart = std::chrono::steady_clock::now();
	list<EPEANode*> generatedNodes;
	for (list<EPEANode*>::iterator it = intermediateNodes.begin(); it != intermediateNodes.end(); ++it) 
	{
		for (list<pair<int16_t, int16_t>>::iterator it2 = (*it)->singleAgentDeltaFs->at(in_agent_id).begin(); 
            it2 != (*it)->singleAgentDeltaFs->at(in_agent_id).end(); ++it2)
		{
			int next_loc = (*it)->locs[in_agent_id] + G.moves_offset[it2->first];
			if(!(*it)->isMoveValid(G, in_agent_id, (*it)->locs[in_agent_id], next_loc, ma_vec))
				continue;

			// validate initial constraints
			bool constrained = false;
			for (Constraint c : initial_constraints[in_agent_id])
			{
				if (get<2>(c) == (*it)->makespan &&
					((get<0>(c) == (*it)->locs[in_agent_id] && get<1>(c) == next_loc) || 
					(get<0>(c) == next_loc && get<1>(c) < 0)))
				{
					constrained = true;
					break;
				}
			}

			if (constrained)  // go to next legal
				continue;
			
			// Using the data that describes its delta F potential before the move.
            // last move was good
			if (it2->second <= (*it)->remainingDeltaF)
			{
				EPEANode *childNode = new EPEANode();
				childNode->deep_copy(**it);  // Copy all except lookUp table
				childNode->moveTo(G, in_agent_id, next_loc, cat, ma_vec);
				childNode->remainingDeltaF -= it2->second;  // Update target F
				generatedNodes.push_back(childNode);
			}
			else
				break;
		}
		
		if(in_agent_id > start_agent_id)
		{
			delete *it;	
		}
	}
	intermediateNodes.clear();
	runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
	return generatedNodes;
}

void EPEA::expandNode(EPEANode& node)
{
	time_pt tstart = std::chrono::steady_clock::now();

	if (getDuration(run_start, tstart) > time_limit)
	{
		HL_num_expanded --;  // Ignore this node expansion if timeout
		runtime = getDuration(run_start, tstart);
		solution_cost = -1;
		solution_found = false;
		return;
	}

	if (!node.alreadyExpanded)
	{
		node.calcSingleAgentDeltaFs(G, initial_constraints, ma_vec);
		node.alreadyExpanded = true;
		node.targetDeltaF = 0;  // Assuming a consistent heuristic (as done in the paper), the min delta F is zero.
		node.remainingDeltaF = 0;  // Just for the following hasChildrenForCurrentDeltaF call.
		if (node.targetDeltaF > node.maxDeltaF)  // Node has no possible children at all
		{
			node.clear();
			runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
			return;
		}
	}

	// If this node was already expanded, notice its h was updated, so the deltaF refers to its original H
	list<EPEANode*> intermediateNodes;
	intermediateNodes.push_back(&node);

	for (int a_id = 0; a_id < G.get_num_of_agents(); a_id++)
	{
		if (ma_vec[a_id])
			intermediateNodes = expandOneAgent(intermediateNodes, a_id, meta_agents.front().front());
	}
	
	list<EPEANode*> finalGeneratedNodes = intermediateNodes;
	for (list<EPEANode*>::iterator it = finalGeneratedNodes.begin(); it != finalGeneratedNodes.end(); ++it)
	{
		(*it)->makespan++;
		(*it)->clearConstraintTable();
		(*it)->targetDeltaF = 0;
		(*it)->parent = &node;
	}

	// Insert the generated nodes into the open list
	for (list< EPEANode* >::iterator child = finalGeneratedNodes.begin(); child != finalGeneratedNodes.end(); ++child)
	{
		// Assuming h is an admissable heuristic, no need to generate nodes that won't get us to the goal
		// within the budget
		if ((*child)->h_val + (*child)->g_val <= this->maxCost)
		{
			hashtable_t::iterator it = allNodes_table.find(*child);

			// If in closed list - only reopen if F is lower or node is otherwise preferred
			// Notice the agents may have gotten to their location from a different direction in this node.
			if (it != allNodes_table.end())
			{
				EPEANode* existing = (*it).second;
				if (screen == 2)
					existing->printNode();

				bool compare;  
				if((*child)->g_val + (*child)->h_val == existing->g_val + existing->h_val)
					compare = (*child)->h_val < existing->h_val;
				else
					compare = (*child)->g_val + (*child)->h_val < existing->g_val + existing->h_val;


				if (compare)// This node has smaller f, or preferred due to other consideration.
				{
					existing->update(**child);
					if (!existing->in_openlist) // reopen 
					{
						existing->open_handle = this->open_list.push(existing);
						existing->in_openlist = true;
					}
				}
				delete (*child);
			}

			else  // add the newly generated node to open_list and hash table
			{
				// allNodes_table.push_back(*child);
				allNodes_table[(*child)] = *child;

				HL_num_generated++;
				(*child)->index = HL_num_generated;
				(*child)->open_handle = open_list.push(*child);
				(*child)->in_openlist = true;
			}
		}
	}

	// Node was cleared during expansion.
	// It's unnecessary and unsafe to continue to prepare it for the next partial expansion.
	if (node.alreadyExpanded == false)
	{
		runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
		return;
	}

	node.targetDeltaF++; // This delta F was exhausted
	node.remainingDeltaF = node.targetDeltaF;

	if (node.targetDeltaF <= node.maxDeltaF && node.h_val + node.g_val + node.targetDeltaF <= this->maxCost)
	{
		// Re-insert node into open list
		node.in_openlist = true;
		node.open_handle = open_list.push(&node);
	}
	else
		node.clear();
	runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
	return;
}

void EPEA::initialClear(void)
{
    // statistics of efficiency
	runtime = 0;
    HL_num_expanded = 0;
    HL_num_generated = 0;
	HL_num_merged = 0;
    LL_num_expanded = 0;
    LL_num_generated = 0;
	
	// statistics of solution quality
    solution_found = false;
    solution_cost = 0.0;

	// other parameters
	cat.clear();
	init_cat.clear();
	vector<vector<int>> temp_m(G.get_num_of_agents(), vector<int>(G.get_num_of_agents(), 0));
	conflict_matrix = temp_m;
	is_init_cat = false;
	open_list.clear();
	meta_agents.clear();
	ma_vec = vector<bool>(num_of_agents, false);

	list<Constraint> tmp_cons;
	initial_constraints = vector<list<Constraint>>(G.get_num_of_agents(), tmp_cons);

	paths_costs_found_initially = vector<int>(G.get_num_of_agents(), 0);
	paths_costs = vector<int>(G.get_num_of_agents(), 0);

	ll_min_f_vals_found_initially = vector<int>(G.get_num_of_agents(), 0);
	ll_min_f_vals = vector<int>(G.get_num_of_agents(), 0);

	paths_found_initially = vector<Path*>(G.get_num_of_agents(), nullptr);
    paths = vector<Path*>(G.get_num_of_agents(), nullptr);

	max_path_len = -1;
}

void EPEA::transformPath(void)
{
	for (int i = 0; i < G.get_num_of_agents(); i++)
	{
		if (ma_vec[i])
		{
			paths_costs[i] = (int) epea_paths[i].size() - 1;
			ll_min_f_vals[i] = (int) epea_paths[i].size() - 1;
		}
		else
		{
			paths_costs[i] = 0;
			ll_min_f_vals[i] = 0;
		}
		
		paths[i] = new vector<pathEntry>(epea_paths[i].size());
		for (int t = 0; t < (int)epea_paths[i].size(); t++)
		{
			paths[i]->at(t).id = epea_paths[i][t];
		}
	}

	// Debug
	if (screen == 1)
	{
		cout << "+++++++++++++++++ paths +++++++++++++++++" << endl;
		for (int i = 0; i < (int)paths.size(); i++)
		{
			cout << "[" << i << "]: ";
			printSinglePath(paths[i]);
		}
	}
}

void EPEA::clearAllNodesTable(void)
{
	if (!allNodes_table.empty())
	{
		hashtable_t::iterator it;
		for (it = allNodes_table.begin(); it != allNodes_table.end(); it++) {
			delete ((*it).second);
		}
		allNodes_table.clear();
		delete (empty_node);
		delete (deleted_node);
	}
}

/// <summary>
/// Runs the algorithm until the problem is solved or memory/time is exhausted
/// </summary>
/// <returns>True if solved</returns>
bool EPEA::run(list<agent_info> ma_info, list<Path*> in_other_paths)
{
	if (screen == 1)
		cout << get_name() << endl;

	// set timer
	run_start = std::chrono::steady_clock::now();  // set timer	

	if (getDuration(run_start, std::chrono::steady_clock::now()) > time_limit)  // Timeout!
	{
		solution_cost = -1;
		solution_found = false;
		runtime = getDuration(run_start, std::chrono::steady_clock::now());
		return solution_found;
	}

	// initial clear parameters
	initialClear();

	// initialize meta-agent table --> every agent in meta-agent
	if (ma_info.empty() && meta_agents.empty())  // Initialized for outter CBS
	{
		for (int i = 0; i < num_of_agents; i++)
		{
			meta_agents.push_back(list<int>({i}));
			ma_vec[i] = true;
		}
	}

	else if (is_solver)  // Initialized for meta-agent solver
	{
		for (const auto& it: ma_info)
		{
			meta_agents.push_back(list<int>({it.agent_id}));
			ma_vec[it.agent_id] = true;
			initial_constraints[it.agent_id] = getMAConstraints(it.constraints);  // Generate constraints
		}
	}

	// Create cat from other_path
	initCAT(in_other_paths);

	// generate root node
	HL_num_generated++;
	EPEANode* root_node = new EPEANode(G, ma_vec);
	root_node->index = HL_num_generated;
	root_node->open_handle = open_list.push(root_node);
	root_node->in_openlist = true;
	allNodes_table[root_node] = root_node;

	int init_h = open_list.top()->h_val;  // g = targetDeltaF = 0 initially
	int lastF = -1;

	while (!open_list.empty())
	{
		// Check if max time has been exceeded
		runtime = getDuration(run_start, std::chrono::steady_clock::now());
		if (runtime > time_limit)
		{
			solution_cost = -1;
			solution_found = false;
			// A minimum estimate of solution_depth
			solution_depth = open_list.top()->g_val + open_list.top()->h_val + open_list.top()->targetDeltaF - init_h;
			if (screen == 1)
				printResults();
			allNodes_table.clear();
			return solution_found;
		}

		EPEANode* curr = open_list.top();
		open_list.pop();
		
		lastF = curr->g_val + curr->h_val + curr->targetDeltaF;

		// Check if node is the goal
		if (curr->h_val == 0)
		{
			runtime = getDuration(run_start, std::chrono::steady_clock::now());
			solution_cost = curr->g_val;
			solution_found = true;
			epea_paths = curr->getPlan(G, ma_vec);
			solution_depth = curr->g_val - init_h;
			transformPath();
			if (screen == 1)
				printResults();

			allNodes_table.clear();
			return solution_found;
		}

		// Expand
		expandNode(*curr);
		HL_num_expanded++;
	}

	// No solution
	solution_cost = -2;
	solution_found = false;
	this->solution_depth = lastF - init_h;
	runtime = getDuration(run_start, std::chrono::steady_clock::now());
	if (screen == 1)
		printResults();
	allNodes_table.clear();
	return solution_found;
}


