#include "cbs.h"

CBS::CBS(const Grid2D& in_G, int k_robust, int screen, double in_time_limit, int in_merge_th, bool in_is_solver,
	SingleAgentPlanner single_planner, BasicSolver* solver_ptr, bool in_mr_active, int in_conf_mode, 
	bool in_rs_only, int in_restart_times):
    BasicSolver(in_G, k_robust, screen, in_time_limit, in_is_solver), 
	merge_th(in_merge_th), single_planner(single_planner), solver(solver_ptr), 
	mr_active(in_mr_active), confs_mode(in_conf_mode), restart_only(in_rs_only), restart_times(in_restart_times)
{
	if (solver == nullptr && merge_th < INT_MAX)
	{
		cerr << "Need to declair solver for MA-CBS!" << endl;
		exit(-1);
	}

	else if (mr_active && restart_only)
	{
		cerr << "Can only activate either MR or Restart only!" << endl;
		exit(-1);
	}

	else
	{
		if (restart_times > 0)
		{
			restart_duration = (clock_t) floor(time_limit * CLOCKS_PER_SEC / (restart_times + 1));
			restart_counter = 1;
		}
		else
		{
			restart_duration = (clock_t) INT_MAX;
		}
	}
}

CBS::~CBS(){}

string CBS::get_name(void) const
{
	string name;
	if (solver == nullptr)
	{
		name += "CBS";
	}
	else
	{
		name += "MACBS_";
		name += std::to_string(merge_th);
		if (mr_active && !restart_only)
			name += "_mr";
		else if (restart_only && !mr_active)
			name += "_ro";
		if (restart_times > 0)
			name += ("_rt" + std::to_string(restart_times));
		name += "-";
		name += solver->get_name();
	}
	return name;
}

// print results
void CBS::printResults() const
{
    if (runtime > time_limit)  // timeout
		cout << "Timeout; ";
	else if (open_list.empty() && solution_cost < 0)
		cout << "No solutions; ";
	else
		cout << ":) Succeed; ";

	double out_runtime = (double) runtime / CLOCKS_PER_SEC;
	cout << "cost:" << solution_cost << "; lb:" << min_sum_f_vals << "; runtime:" << out_runtime << "; HL_node:" << 
        HL_num_generated << "; LL_node:" << LL_num_generated << "; merge_node:" << HL_num_merged << "; max_MA:" << 
		getMaxMANum() << endl;
}

void CBS::saveResults(const string& file_name, const string& instance_name)
{
	std::ifstream infile(file_name);
	bool exist = infile.good();
	infile.close();
	if (!exist)
	{
		ofstream addHeads(file_name);
		addHeads << "runtime,#high-level expanded,#high-level generated,#high-level merged," << 
			"#low-level expanded,#low-level generated,#solver calls,max MA," <<
			"solution cost,min f value,root g value,root f value,merge_th," <<
			"runtime of detecting conflicts,runtime of building CATs,runtime of path finding," <<
			"runtime of generating root,runtime of generating child nodes,runtime of sub-solver,runtime of merge,runtime of preprocessing," <<
			"solver name,instance name, max conflict num, max conf a1, max conf a2" << endl;
		addHeads.close();
	}

	double out_runtime = (double) runtime / CLOCKS_PER_SEC;
	double out_runtime_generate_root = (double) runtime_generate_root / CLOCKS_PER_SEC;
    double out_runtime_generate_child = (double) runtime_generate_child / CLOCKS_PER_SEC;
	double out_runtime_build_CAT = (double) runtime_build_CAT / CLOCKS_PER_SEC;
	double out_runtime_path_finding = (double) runtime_path_finding / CLOCKS_PER_SEC;
	double out_runtime_detect_conflicts = (double) runtime_detect_conflicts / CLOCKS_PER_SEC;
    double out_runtime_merge = (double) runtime_merge / CLOCKS_PER_SEC;
    double out_runtime_solver = (double) runtime_solver / CLOCKS_PER_SEC;

	int max_conf_val, max_conf_a1, max_conf_a2;
	tie(max_conf_val, max_conf_a1, max_conf_a2) = getMaxConflictMatrix();

	ofstream stats(file_name, std::ios::app);
	stats << out_runtime << "," << HL_num_expanded << "," << HL_num_generated << "," << HL_num_merged << "," << 
		LL_num_expanded << "," << LL_num_generated << "," << solver_counter << "," <<  getMaxMANum() << "," <<
		solution_cost << "," << min_sum_f_vals << "," << dummy_start->g_val << "," << dummy_start->sum_min_f_vals << "," << merge_th << "," <<
		out_runtime_detect_conflicts << "," << out_runtime_build_CAT << "," << out_runtime_path_finding << "," << 
		out_runtime_generate_root << "," << out_runtime_generate_child << "," << out_runtime_solver << "," << out_runtime_merge << "," << G.pre_time << "," <<
		get_name() << "," << instance_name << "," << max_conf_val << "," << max_conf_a1 << "," << max_conf_a2 << endl;
	stats.close();
}

inline int CBS::getMaxMANum(void) const
{
	int max_ma_size = 0;
	for (const auto& ag: meta_agents)
		if (max_ma_size < (int) ag.size())
			max_ma_size = ag.size();
	return max_ma_size;
}

//////////////////// CONFLICTS ///////////////////////////
// Find all conflicts in the current solution
bool CBS::findConflicts(CBSNode& node)
{
	time_pt tstart = std::chrono::steady_clock::now();
	if (screen == 1)
		cout << "findConflicts" << endl;
	
	if(node.parent == nullptr)  // Root node
	{
		if (screen == 1)
		{
			cout << "root" << endl;
			cout << "meta_agent size: " << meta_agents.size() << endl;
		}

		if (mr_active && (int) meta_agents.size() < num_of_agents)  // For merge-restart in outer CBS
		{
			// Detect new conflicts		
			vector<bool> detected(num_of_agents, false);
			for (int a1 = 0; a1 < num_of_agents; a1 ++)
			{
				detected[a1] = true;
				for (int a2 = 0; a2 < num_of_agents; a2++)
				{
					if (detected[a2] || !ma_vec[a2])
						continue;
					else if (findMetaAgent(a1) == findMetaAgent(a2))  // For efficiency
						continue;
					else
						findAgentConflicts(node.conflicts, a1, a2);
				}
			}
		}

		else  // Merge-restart is off
		{
			list<list<int>>::iterator a1_it;
			list<list<int>>::iterator a2_it;
			for (a1_it = meta_agents.begin(); a1_it != meta_agents.end(); a1_it++) 
				for (a2_it = std::next(a1_it, 1); a2_it != meta_agents.end(); a2_it++) 
					findAgentConflicts(node.conflicts, a1_it->front(), a2_it->front());
		}
	}
	else
	{		
		// Copy from parent
		vector<bool> copy(num_of_agents, true);
		// Do not copy conflicts of agents that already updated paths
		for (list<tuple<int, vector<pathEntry>, int, int>>::const_iterator it = node.paths_updated.begin(); 
			it != node.paths_updated.end(); it++)
		{
			copy[get<0>(*it)] = false;
		}

		// Copy conflicts from parent, not from meta-agent
		for (list<std::shared_ptr<Conflict>>::const_iterator it = node.parent->conflicts.begin(); 
			it != node.parent->conflicts.end(); ++it)
		{
			if (copy[get<0>(**it)] && copy[get<1>(**it)])  // **it returns a list of meta agents (int).
				node.conflicts.push_back(*it);
		}

		// Detect new conflicts		
		vector<bool> detected(num_of_agents, false);
		for (list<tuple<int, vector<pathEntry>, int, int>>::const_iterator it = node.paths_updated.begin(); 
			it != node.paths_updated.end(); it++)
		{
			int a1 = get<0>(*it);
			detected[a1] = true;
			for (int a2 = 0; a2 < num_of_agents; a2++)
			{
				if (detected[a2] || !ma_vec[a2])
					continue;
				else if (findMetaAgent(a1) == findMetaAgent(a2))  // for efficiency
					continue;
				else
					findAgentConflicts(node.conflicts, a1, a2);
			}
		}
	}
	runtime_detect_conflicts += getDuration(tstart, std::chrono::steady_clock::now());
    return !node.conflicts.empty();
}

bool CBS::findConflictsMA(CBSNode& node)
{
	if (screen == 1)
	{
		cout << "findConflictsMA" << endl;
		for (const auto& ma_it : node.meta_agents)
			printMetaAgent(ma_it);
	}

	time_pt tstart = std::chrono::steady_clock::now();
	if (solver != nullptr)  // This is for outter CBS
	{
		// Copy from parent
		vector<bool> copy(num_of_agents, true);
		// Do not copy conflicts of agents that already updated paths
		for (list<tuple<int, vector<pathEntry>, int, int>>::const_iterator it = node.paths_updated.begin(); 
			it != node.paths_updated.end(); it++)
		{
			copy[get<0>(*it)] = false;
		}

		// Copy conflicts from parent, not from meta-agent
		if (node.parent != nullptr)
		{
			for (list<std::shared_ptr<Conflict>>::const_iterator it = node.parent->conflicts.begin(); 
				it != node.parent->conflicts.end(); ++it)
			{
				if (copy[get<0>(**it)] && copy[get<1>(**it)])  // **it returns a list of meta agents (int).
					node.conflicts.push_back(*it);
			}
		}

		// Erase previous conflicts that related to meta-agents
		for (list<std::shared_ptr<Conflict>>::const_iterator it = node.conflicts.begin(); it != node.conflicts.end();)
		{
			if (solver->ma_vec[get<0>(**it)] || solver->ma_vec[get<1>(**it)])
				it = node.conflicts.erase(it++);
			else
				++it;
		}
	}

	if (node.paths_updated.empty())
	{
		cerr << "Failed, no updated paths!!" << endl;
		exit(-1);
	}

	vector<bool> detected(num_of_agents, false);
	for (list<tuple<int, vector<pathEntry>, int, int>>::const_iterator it = node.paths_updated.begin(); 
		it != node.paths_updated.end(); it++)
	{
		int a1 = get<0>(*it);
		if (solver->ma_vec[a1])
		{
			detected[a1] = true;
			for (int a2 = 0; a2 < num_of_agents; a2++)
			{
				if (detected[a2])
					continue;
				else if (findMetaAgent(a1) == findMetaAgent(a2))  // for efficiency
					continue;
				else
					findAgentConflicts(node.conflicts, a1, a2);
			}
		}
	}

	runtime_detect_conflicts += getDuration(tstart, std::chrono::steady_clock::now());
    return !node.conflicts.empty();
}

// Takes the paths_found_initially and UPDATE all (constrained) paths found for agents from curr to start
// also, do the same for ll_min_f_vals and paths_costs (since its already "on the way").
void CBS::updatePaths(CBSNode* curr)
{
	paths = paths_found_initially;
	ll_min_f_vals = ll_min_f_vals_found_initially;
	paths_costs = paths_costs_found_initially;
	vector<bool> updated(num_of_agents, false);  // initialized for false

	do  // Fix for merge_th is 0
	{
		for (auto it = curr->paths_updated.begin(); it != curr->paths_updated.end(); it++)
		{
			if (!updated[get<0>(*it)])  // get<0> is agent_id
			{
				paths[get<0>(*it)] = &(get<1>(*it));  // get<1> is the pathEntry
				paths_costs[get<0>(*it)] = get<2>(*it);
				ll_min_f_vals[get<0>(*it)] = get<3>(*it);
				updated[get<0>(*it)] = true;
			}
		}
		if (curr->parent != nullptr)
			curr = curr->parent;
	} while (curr->parent != nullptr);	
}

vector<list<tuple<int, int, bool>>>* CBS::collectConstraints(CBSNode* curr, int ag, const list<agent_info>& ma_info)
{
	if (screen == 2)
		cout << "collectCOnstraints for agent: " << ag << endl;

	// Extract all constraints on leaf_node->agent_id
	list <Constraint> constraints_negative;

	int max_timestep = -1;
	while (curr != dummy_start)
	{		
		// if agent_id is found in the node
		if (std::find(curr->agent_id.begin(), curr->agent_id.end(), ag) != curr->agent_id.end())
		{
			constraints_negative.push_back(curr->constraint);
			if (get<3>(curr->constraint) > max_timestep)  // calc constraints' max_timestep
				max_timestep = get<3>(curr->constraint);
		}
		curr = curr->parent;
	}
	
	vector<list<tuple<int, int, bool>>>* init_cons_ptr = nullptr;
	if (!ma_info.empty())
	{
		for (const auto& ma_it : ma_info)
		{
			if (ma_it.agent_id == ag && ma_it.constraints != nullptr)
			{
				max_timestep = std::max(max_timestep, (int) ma_it.constraints->size());
				init_cons_ptr = ma_it.constraints;
				break;
			}
		}
	}

	// Initialize a constraint vector of length max_timestep+1. 
	// Each entry is an empty list< tuple<int,int, bool> > (loc1,loc2, positive)
	auto cons_vec = new vector<list<tuple<int, int, bool>>>(max_timestep + k_robust + 1, list<tuple<int, int, bool>>());

	if (init_cons_ptr != nullptr)
	{
		for (int t = 0; t < (int)init_cons_ptr->size(); t++)
			cons_vec->at(t) = init_cons_ptr->at(t);
	}

	for (const auto & it : constraints_negative)
	{
		for (int t = get<2>(it); t < get<3>(it); t++)
		{
			cons_vec->at(t).push_back(make_tuple(get<0>(it), get<1>(it), false));
			if (screen == 2)
			{
				cout << "constraint t:" << t << ", ag:" << ag << ", loc1:" << get<0>(it) << ", loc2:" << get<1>(it) << endl;
			}
		}
	}

	return cons_vec;
}

void CBS::generateRoot(const list<agent_info>& ma_info, const list<Path*>& in_other_paths)
{
	time_pt tstart = std::chrono::steady_clock::now();

    // Initialize paths_found_initially
    paths_found_initially.resize(num_of_agents, nullptr);
	paths = paths_found_initially;

	// Update cat for other paths initially
	initCAT(in_other_paths);
	
	if (ma_info.empty())
	{
		for (const auto& ag : meta_agents)
		{
			if (ag.size() == 1)  // Initialize root for single agent
			{
				paths = paths_found_initially;
				updateCAT(ag.front(), in_other_paths);
				if (single_planner.runFocalSearch(G, ag.front(), 1.0, nullptr, cat) == false)
				{
					if (getDuration(run_start, std::chrono::steady_clock::now()) > time_limit)
					{
						solution_cost = -1;
						solution_found = false;
						dummy_start = new CBSNode();  // For saveResults to work well
						runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
						return;
					}
					else
					{
						if (screen == 2)
							cout << "NO SOLUTION EXISTS FOR AGENT " << ag.front() << endl;
						solution_cost = -2;
						solution_found = false;
						dummy_start = new CBSNode();  // For saveResults to work well
						runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
						return;
					}
				}
				paths_found_initially[ag.front()] = new vector<pathEntry>(single_planner.path);
				ll_min_f_vals_found_initially[ag.front()] = single_planner.min_f_val;
				paths_costs_found_initially[ag.front()] = single_planner.path_cost;
				LL_num_expanded += single_planner.num_expanded;
				LL_num_generated += single_planner.num_generated;
			}

			else if (ag.size() > 1 && mr_active)  // Initialize root for meta-agent in merge and restart
			{
				// Find a path w.r.t cons_vec (and prioretize by res_table).
				solver_counter ++;
					
				list<agent_info> root_ma_info;
				vector<bool> root_ma_vec(num_of_agents, false);
				for (auto single_ag : ag)
				{
					agent_info temp_agent;
					temp_agent.agent_id = single_ag;
					temp_agent.constraints = nullptr;  // empty constraint
					root_ma_info.push_back(temp_agent);
					root_ma_vec[single_ag] = true;
				}

				list<Path*> dummy_other_paths;

				// Modify time_limit for the MA-solver
				solver->time_limit = time_limit - getDuration(run_start, std::chrono::steady_clock::now());

				// Run the solver for meta-agent
				bool rootFoundSol = solver->run(root_ma_info, dummy_other_paths);
				LL_num_expanded += solver->LL_num_expanded;
				LL_num_generated += solver->LL_num_generated;
				runtime_solver += solver->runtime;

				if (rootFoundSol)  // Found paths for meta-agent
				{
					for (const auto& it : root_ma_info)
					{	
						paths = paths_found_initially;
						paths_found_initially[it.agent_id] = new Path(*solver->paths[it.agent_id]);
						ll_min_f_vals_found_initially[it.agent_id] = solver->ll_min_f_vals[it.agent_id];
						paths_costs_found_initially[it.agent_id] = solver->paths_costs[it.agent_id];
					}

					// Debug: Show paths of meta-agent
					if (screen == 1)
					{
						for (const auto& it: root_ma_info)
						{
							cout << "------------------------------------------------------\n";
							cout << "[" << it.agent_id << "] paths_found_initially: \n";
							printSinglePath(paths_found_initially[it.agent_id]);
							cout << "------------------------------------------------------\n";
						}
						cout << "MR Root Path done" << endl;
					}
				}

				else if (solver->runtime > solver->time_limit)  // Timeout in solver!!!
				{
					solution_cost = -1;
					solution_found = false;
					dummy_start = new CBSNode();  // For saveResults to work well
					runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
					return;
				}

				else
				{
					solution_cost = -2;
					solution_found = false;
					dummy_start = new CBSNode();  // For saveResults to work well
					runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
					return;
				}
			}
		}
	}

	else
	{
		// Construct initial constraints ptr
		for (const auto& info_it : ma_info)
		{
			paths = paths_found_initially;
			updateCAT(info_it.agent_id, in_other_paths);
			if (single_planner.runFocalSearch(G, info_it.agent_id, 1.0, info_it.constraints, cat) == false)
			{
				if (getDuration(run_start, std::chrono::steady_clock::now()) > time_limit)
				{
					solution_cost = -1;
					solution_found = false;
					dummy_start = new CBSNode();  // For saveResults to work well
					runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
					return;
				}
				else
				{
					if (screen == 2)
						cout << "NO SOLUTION EXISTS FOR AGENT " << info_it.agent_id << endl;
					solution_cost = -2;
					solution_found = false;
					dummy_start = new CBSNode();  // For saveResults to work well
					runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
					return;
				}
			}
			paths_found_initially[info_it.agent_id] = new vector<pathEntry>(single_planner.path);
			ll_min_f_vals_found_initially[info_it.agent_id] = single_planner.min_f_val;
			paths_costs_found_initially[info_it.agent_id] = single_planner.path_cost;
			LL_num_expanded += single_planner.num_expanded;
			LL_num_generated += single_planner.num_generated;
		}
	}
	
    paths = paths_found_initially;
    ll_min_f_vals = ll_min_f_vals_found_initially;
    paths_costs = paths_costs_found_initially;

    // generate dummy start and update data structures
	dummy_start = new CBSNode();
	dummy_start->meta_agents = meta_agents;
	dummy_start->ma_vec = ma_vec;

    for (int i = 0; i < num_of_agents; i++)
    {
        dummy_start->g_val += paths_costs[i];
        dummy_start->sum_min_f_vals += ll_min_f_vals[i];
    }
    findConflicts(*dummy_start);
    dummy_start->num_of_collisions = (int)dummy_start->conflicts.size();
    dummy_start->open_handle = open_list.push(dummy_start);
    HL_num_generated++;
    dummy_start->time_generated = HL_num_generated;
    
	allNodes_table.push_back(dummy_start);
	min_sum_f_vals = dummy_start->sum_min_f_vals;

	runtime_generate_root += getDuration(tstart, std::chrono::steady_clock::now());
	return;
}

//////////////////// GENERATE A NODE ///////////////////////////
// Plan a path for an agent in a child node
// Collect constraints in the function. 
bool CBS::findPathForSingleAgent(CBSNode* node, int ag, 
	const list<agent_info>& ma_info, const list<Path*>& in_other_paths)
{
	time_pt tstart = std::chrono::steady_clock::now();

	// Extract all constraints on agent ag
	vector < list< tuple<int, int, bool> > >* cons_vec = collectConstraints(node, ag, ma_info);

	// Build reservation table
	updateCAT(ag, in_other_paths);

	// Find a path w.r.t cons_vec (and prioretize by res_table).
	bool foundSol = single_planner.runFocalSearch(G, ag, 1.0, cons_vec, cat);
	LL_num_expanded += single_planner.num_expanded;
	LL_num_generated += single_planner.num_generated;
	delete (cons_vec);
	if (foundSol)
	{
		for (list<tuple<int, Path, int, int>>::const_iterator p_it = node->paths_updated.begin(); 
			p_it != node->paths_updated.end();)
		{
			if (get<0>(*p_it) == ag)
				p_it = node->paths_updated.erase(p_it++);
			else
				++p_it;
		}

		node->paths_updated.emplace_back(ag, vector<pathEntry>(single_planner.path),
			single_planner.path_cost, single_planner.min_f_val);

		node->g_val = node->g_val - (int)paths[ag]->size() + (int)single_planner.path.size();
		node->sum_min_f_vals = node->sum_min_f_vals - ll_min_f_vals[ag] + single_planner.min_f_val;
		paths[ag] = &get<1>(node->paths_updated.back());
		ll_min_f_vals[ag] = single_planner.min_f_val;

		runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
		return true;
	}
	else
	{
		delete node;
		runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
		return false;
	}
}

// Plan a path for the meta agent in a child node
// Collect constraints outside the function. 
bool CBS::findPathForMetaAgent(CBSNode* node, const list<int>& meta_ag, 
	const list<agent_info>& ma_info, const list<Path*>& in_other_paths)
{
	time_pt tstart = std::chrono::steady_clock::now();

	if (solver == nullptr)
	{
		cerr << "Failed: No solver for MetaAgent!" << endl;
		exit(-1);
	}

	// Find a path w.r.t cons_vec (and prioretize by res_table).
	solver_counter ++;

	if (screen == 1 && in_other_paths.size() > 0)
	{
		printPaths(in_other_paths);
		cout << endl;
	}

	// Modify time_limit for the MA-solver
	solver->time_limit = time_limit - getDuration(run_start, std::chrono::steady_clock::now());  
	
	// Run solver for meta-agent
	bool foundSol = solver->run(ma_info, in_other_paths);
	LL_num_expanded += solver->LL_num_expanded;
	LL_num_generated += solver->LL_num_generated;
	runtime_solver += solver->runtime;

	if (solver->runtime > solver->time_limit)  // Timeout in solver!!!
	{
		runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
		return false;
	}

	if (foundSol)
	{
		// Delete repeated paths_updated
		for (const auto& it : ma_info)
		{
			for (list<tuple<int, Path, int, int>>::const_iterator p_it = node->paths_updated.begin(); 
				p_it != node->paths_updated.end();)
			{
				if (get<0>(*p_it) == it.agent_id)
				{
					paths[it.agent_id] = nullptr;
					p_it = node->paths_updated.erase(p_it++);
				}
				else
					++p_it;
			}
		}

		for (const auto& it : ma_info)
		{	
			// Agents order in node and solver are the same
			node->paths_updated.emplace_back(it.agent_id, vector<pathEntry>(*solver->paths[it.agent_id]),
				solver->paths_costs[it.agent_id], solver->ll_min_f_vals[it.agent_id]);

			node->g_val = node->g_val - paths_costs[it.agent_id] + solver->paths_costs[it.agent_id];

			node->sum_min_f_vals = node->sum_min_f_vals - ll_min_f_vals[it.agent_id] + solver->ll_min_f_vals[it.agent_id];

			paths[it.agent_id] = &get<1>(node->paths_updated.back());
			paths_costs[it.agent_id] = solver->paths_costs[it.agent_id];
			ll_min_f_vals[it.agent_id] = solver->ll_min_f_vals[it.agent_id];
		}

		if (screen == 1)
		{
			cout << "================= Solver paths =================" << endl;
			for (const auto& it: ma_info)
			{
				cout << "agent: " << it.agent_id << endl;
				printSinglePath(solver->paths[it.agent_id]);
			}
			cout << "paths_updated size: " << node->paths_updated.size() << endl;
			cout << "=============== Solver paths END ===============" << endl;
		}

		runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
		return true;
	}
	else
	{
		delete node;
		runtime_path_finding += getDuration(tstart, std::chrono::steady_clock::now());
		return false;
	}
}

// Plan paths for a child node
bool CBS::generateChild(CBSNode* node, const list<agent_info>& ma_info, const list<Path*>& in_other_paths)
{
	time_pt tstart = std::chrono::steady_clock::now();

	if (get<4>(node->constraint))  // Positive constraint
	{
		cout << "positive constraint should not exists!";
		return false;
	}
	else  // Negative constraint
	{
		if (node->agent_id.size() == 1 || solver == nullptr)
		{
			if (!findPathForSingleAgent(node, node->agent_id.front(), ma_info, in_other_paths))
			{
				runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
				return false;  // No path is found for agent_id
			}
			else  // Find a path for single agent, find the conflict!
			{
				findConflicts(*node);
			}
		}
		else
		{
			list<agent_info> joint_ma_info;
			vector<bool> temp_ma_vec(num_of_agents, false);
			for (auto ag : node->agent_id)
			{
				// Add constraints,...
				agent_info temp_agent;
				vector < list< tuple<int, int, bool> > >* ag_cons = collectConstraints(node, ag, ma_info);
				temp_agent.agent_id = ag;
				temp_agent.constraints = ag_cons;
				joint_ma_info.push_back(temp_agent);
				temp_ma_vec[ag] = true;
			}

			// Update other paths from agent not in the meta-agent
			list<Path*> joint_other_paths;
			for (int ag = 0; ag < num_of_agents; ag++)
			{
				if (!temp_ma_vec[ag])
					joint_other_paths.push_back(paths[ag]);
			}

			if (!findPathForMetaAgent(node, node->agent_id, joint_ma_info, joint_other_paths))
			{
				runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
				return false;  // No path is found for agent_id
			}
			else  // Find paths for meta-agent, find conflicts
			{
				joint_ma_info.clear();
				joint_other_paths.clear();
				findConflictsMA(*node);
			}
			
		}
	}

	node->num_of_collisions = (int)node->conflicts.size();  // Compute number of colliding agents
	node->meta_agents = meta_agents;
	node->ma_vec = ma_vec;

	// Update handles
	node->open_handle = open_list.push(node);  // Add child node to open list
	HL_num_generated++;
	node->time_generated = HL_num_generated;
	allNodes_table.push_back(node);
	
	if (screen == 1)  // Debug
	{
		cout << "Generate child!!!" << endl;
		node->printNode();
		cout << "Generate child done !!!" << endl;
	}
	runtime_generate_child += getDuration(tstart, std::chrono::steady_clock::now());
	return true;
}

void CBS::initialClear()
{
	// Only intialized when merge_restart is off!
	if (!mr_active && !restart_only)
	{
		runtime = 0;
		meta_agents.clear();
		ma_vec = vector<bool>(num_of_agents, false);
		
		// statistics of efficiency
		HL_num_expanded = 0;
		HL_num_generated = 0;
		HL_num_merged = 0;
		LL_num_expanded = 0;
		LL_num_generated = 0;
	}
	
	// Statistics of solution quality
    min_sum_f_vals = 0;
    solution_found = false;
    solution_cost = 0.0;

	// Other parameters
	cat.clear();
	init_cat.clear();
	vector<vector<int>> temp_m(num_of_agents, vector<int>(num_of_agents, 0));
	conflict_matrix = temp_m;
	is_init_cat = false;
	dummy_start = nullptr;
	open_list.clear();
	allNodes_table.clear();
	
	paths_costs_found_initially = vector<int>(num_of_agents, 0);
	paths_costs = vector<int>(num_of_agents, 0);

	ll_min_f_vals_found_initially = vector<int>(num_of_agents, 0);
	ll_min_f_vals = vector<int>(num_of_agents, 0);

	paths_found_initially = vector<Path*>(num_of_agents, nullptr);
    paths = vector<Path*>(num_of_agents, nullptr);

	max_path_len = -1;
}

bool CBS::run(list<agent_info> ma_info, list<Path*> in_other_paths)
{
	run_start = std::chrono::steady_clock::now();  // Set timer

	initialClear();  // Clearing parameters in basic solver

	// Initialize meta-agent table --> every agent in meta-agent
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
		}
	}

    generateRoot(ma_info, in_other_paths);

	// Root node is already in the open_list
	while (!open_list.empty())
	{
		// Check whether time out
		clock_t loop_runtime = getDuration(run_start, std::chrono::steady_clock::now());

		if (loop_runtime > time_limit)  // Timeout
		{
			if (is_solver)
				cout << "Timeout in solver!!!!" << endl;

			solution_found = false;
			solution_cost = -1;
			break;
		}

		if (open_list.size() == 0)  // No solution for the agent configuration
		{
			solution_found = false;
			solution_cost = -2;
			break;
		}

		CBSNode* open_head = open_list.top();
		if (open_head->sum_min_f_vals > min_sum_f_vals)
			min_sum_f_vals = open_head->sum_min_f_vals;

		CBSNode* curr = open_list.top();
		open_list.pop();

		if (screen > 0)  // Debug
		{
			cout << "\nCurrent node!!!!!" << endl;
			curr->printNode();
			cout << "Current node end!!!!!\n" << endl;
		}

		// Take the paths_found_initially and 
		// Update all constrained paths found for agents from curr to dummy_start (and lower-bounds)		
		updatePaths(curr);
		if (curr->conflicts.empty())
		{  
			// Found a solution (and finish the while loop)
			solution_found = true;
			solution_cost = curr->g_val;
			break;
		}

		// Liron restart
		if (restart_times > 0 && (int) floor(loop_runtime / restart_duration) == restart_counter)
		{
			// Random shuffle meta_agents
			vector<int> tmp_ma_vec;
			for (int i=0; i<num_of_agents; ++i) tmp_ma_vec.push_back(i);
			std::random_shuffle(tmp_ma_vec.begin(), tmp_ma_vec.end() );

			// Reassign to meta_agents
			meta_agents.clear();
			for (int i = 0; i < num_of_agents; i++)
				meta_agents.push_back(list<int>({tmp_ma_vec[i]}));

			restart_counter ++;
			HL_num_merged ++;

			if (screen == 2)
				printAllAgents();
			break;
		}

		// Copy Meta_agent status from node to solver
		if (curr->agent_id.front() != -1)  // It is not a root
		{
			meta_agents = curr->meta_agents;
			ma_vec = curr->ma_vec;
		}
		
		// Choose a conflict
		int agent1_id, agent2_id, location1, location2, timestep;
		list<int> ma1;
		list<int> ma2;

		while (true)  // Choose a conflict that is not inside the meta-agent (external conflicts)
		{
			tie(agent1_id, agent2_id, location1, location2, timestep) = *chooseConflict(curr->conflicts, confs_mode);
			ma1 = findMetaAgent(agent1_id);
			ma2 = findMetaAgent(agent2_id);
			
			if (ma1 != ma2)  // Make sure that the conflicts are from two meta-agents
			{
				if (screen == 2)
				{
					cout << "\nPick Conflicts: " << agent1_id << " " << agent2_id <<
						" " << location1 << " " << location2 << " " << timestep << " " << endl;
				}
				break;
			}
			
			else
			{
				ma1.clear();
				ma2.clear();
			}
		}

		// Get the index of num_of_conflict table
		list<int> joint_ma = findMetaAgent(agent1_id);
		joint_ma.merge(findMetaAgent(agent2_id));

		for (const auto& a1 : ma1)
		{
			for (const auto& a2 : ma2)
			{
				conflict_matrix[a1][a2] += 1;
				conflict_matrix[a2][a1] += 1;
			}
		}
		
		if (countConflicts(ma1, ma2) > merge_th)  // Should merge
		{
			time_pt tstart_merge = std::chrono::steady_clock::now();
			HL_num_merged ++;  // Add 1 to the counter

			if (restart_only)  // Restart only
			{
				// Random shuffle meta_agents
				if ((int) meta_agents.size() == num_of_agents)
				{
					// Random shuffle can only be applied on a vector
					vector<int> tmp_ma_vec;
					for (int i=0; i<num_of_agents; ++i) tmp_ma_vec.push_back(i);
					std::random_shuffle(tmp_ma_vec.begin(), tmp_ma_vec.end() );

					// Reassign to meta_agents
					meta_agents.clear();
					for (int i = 0; i < num_of_agents; i++)
						meta_agents.push_back(list<int>({tmp_ma_vec[i]}));

					if (screen == 1)
						printAllAgents();

					runtime_merge += getDuration(tstart_merge, std::chrono::steady_clock::now());
					break;
				}
				else
				{
					cerr << "Size of meta_agent should equal num_of_agent!" << endl;
					exit(-1);
				}
				
			}

			// Merge agents into a meta-agent
			if (screen == 1)
			{
				cout << "joint MA: ";
				printMetaAgent(joint_ma);
			}
			meta_agents.remove(ma1);
			meta_agents.remove(ma2);
			meta_agents.push_back(joint_ma);

			// Randomly shuffle meta_agents
			vector<std::reference_wrapper<list<int>>> vec(meta_agents.begin(), meta_agents.end());
			std::random_shuffle(vec.begin(), vec.end());
			list<list<int>> shuffled_list {vec.begin(), vec.end()};
			meta_agents.swap(shuffled_list);

			if (mr_active)
			{
				runtime_merge += getDuration(tstart_merge, std::chrono::steady_clock::now());
				break;
			}

			// Collect constraints for meta-agents
			list<agent_info> joint_ma_info;
			vector<bool> temp_ma_vec(num_of_agents, false);
			for (auto ag : joint_ma)
			{
				// Add constraints
				agent_info temp_agent;
				vector <list< tuple<int, int, bool>>>* ag_cons = collectConstraints(curr, ag, ma_info);
				temp_agent.agent_id = ag;
				temp_agent.constraints = ag_cons;
				joint_ma_info.push_back(temp_agent);
				temp_ma_vec[ag] = true;
			}

			// Update other paths from agent not in the meta-agent
			list<Path*> joint_other_paths;
			for (int ag = 0; ag < num_of_agents; ag++)
			{
				if (!temp_ma_vec[ag])
					joint_other_paths.push_back(paths[ag]);
			}

			bool foundMetaPath = findPathForMetaAgent(curr, joint_ma, joint_ma_info, joint_other_paths);
			
			joint_ma_info.clear();
			joint_ma.clear();
			joint_other_paths.clear();

			if (foundMetaPath)
			{
				// Copy new meta_agents to current node
				curr->meta_agents = meta_agents;
				curr->ma_vec = ma_vec;
	
				findConflictsMA(*curr);
	
				curr->num_of_collisions = (int)curr->conflicts.size();

				// Add current node to open list
				curr->open_handle = open_list.push(curr);
				
				if (screen == 1)
				{
					cout << "================= MA Node =================" << endl;
					curr->printNode();
					cout << "open_list size: " << open_list.size() << endl;
					cout << "Merge Complete, insert to OpenList!" << endl;
					cout << "=============== MA Node END ===============" << endl;
				}
				runtime_merge += getDuration(tstart_merge, std::chrono::steady_clock::now());
				continue;
			}

			else
			{
				runtime_merge += getDuration(tstart_merge, std::chrono::steady_clock::now());
				cout << "Failed: No path for Meta-Agent!!!" << endl;
				continue;
			}
		}  // Should merge end

		// Braching: generate the two successors that resolve one of the conflicts
		HL_num_expanded++;
		curr->time_expanded = HL_num_expanded;
		auto n1 = new CBSNode();
		auto n2 = new CBSNode();
		n1->parent = curr;
		n2->parent = curr;
		n1->g_val = curr->g_val;
		n2->g_val = curr->g_val;
		n1->sum_min_f_vals = curr->sum_min_f_vals;
		n2->sum_min_f_vals = curr->sum_min_f_vals;
		n1->meta_agents = curr->meta_agents;
		n2->meta_agents = curr->meta_agents;
		n1->ma_vec = curr->ma_vec;
		n2->ma_vec = curr->ma_vec;

		n1->agent_id = ma1;
		n2->agent_id = ma2;
		n1->constraint = make_tuple(location1, location2, timestep, timestep + k_robust + 1, false);
		
		if (location2 < 0)  // Generate n2 constraint for vertex conflict
			n2->constraint = make_tuple(location1, location2, timestep, timestep + k_robust + 1, false);
		else  // Generate n2 constraint for edge conflict
			n2->constraint = make_tuple(location2, location1, timestep, timestep + 1, false);
		
		vector<vector<pathEntry>*> copy(paths);
		generateChild(n1, ma_info, in_other_paths);
		paths = copy;
		generateChild(n2, ma_info, in_other_paths);
		curr->conflicts.clear();  // conflict of current node is no longer useful since path has been replanned.

	}  // End of while loop

	// Update total runtime (using adding for merge-restart)
	runtime += getDuration(run_start, std::chrono::steady_clock::now());
	if (runtime > time_limit && !solution_found && solution_cost != -2)  // Timeout
	{
		solution_cost = -1;
		solution_found = false;
	}
	// Activate merge-restart and under time-limit
	else if ((mr_active || restart_only || restart_times > 0) && runtime < time_limit && !solution_found && solution_cost == 0)
	{
		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		if (solver != nullptr)
		{
			// Modify time_limit for the MA-solver
			solver->time_limit = time_limit - getDuration(run_start, std::chrono::steady_clock::now());
		}
		solution_found = run(dummy_info, dummy_other_paths);
	}

	if (!is_solver && screen == 1)  // Debug
		printResults();

	return solution_found;
}