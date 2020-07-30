# include "basic_solver.h"
# include <iostream>

BasicSolver::BasicSolver(const Grid2D& in_G, int k_robust, int screen, double in_time_limit, bool in_is_solver):
    G(in_G), k_robust(k_robust), screen(screen), is_solver(in_is_solver)
{
	time_limit = (clock_t)(in_time_limit * CLOCKS_PER_SEC);
	num_of_agents = (int)G.start_locations.size();
	map_size = G.map_size();
	ll_min_f_vals = vector <int>(num_of_agents, 0);
	paths_costs = vector <int>(num_of_agents, 0);
	ma_vec = vector<bool>(num_of_agents, false);
	ll_min_f_vals_found_initially = vector <int>(num_of_agents, 0);
	paths_costs_found_initially = vector <int>(num_of_agents, 0);
	vector<vector<int>> temp_m(num_of_agents, vector<int>(num_of_agents, 0));
	conflict_matrix = temp_m;
}

BasicSolver::~BasicSolver(){}


//////////////////// TOOLS ///////////////////////////

// Return agent_id's location for the given timestep
// Note -- if timestep is longer than its plan length,
// then the location remains the same as its last location
inline int BasicSolver::getAgentLocation(int agent_id, int timestep) const
{
	//debug
	// if (agent_id == 9)
	// {
	// 	cout << "getAgentLocation\n";
	// 	cout << "agent: " << agent_id << endl;
	// 	printSinglePath(paths[agent_id]);
	// }

	// if last timestep > plan length, agent remains in its last location
	if (timestep >= (int) paths[agent_id]->size())
		return G.get_location(paths[agent_id]->back().id);
	else if (timestep < 0)
		return G.get_location(paths[agent_id]->front().id);
	else  // otherwise, return its location for that timestep
		return G.get_location(paths[agent_id]->at(timestep).id);
}

// Return true iff agent1 and agent2 switched locations at timestep [t,t+1] 
inline bool BasicSolver::switchedLocations(int agent1_id, int agent2_id, size_t timestep) 
{
	// if both agents at their goal, they are done moving (cannot switch places)
	if ( timestep >= paths[agent1_id]->size() && timestep >= paths[agent2_id]->size() )
		return false;
	else
	{
		return getAgentLocation(agent1_id, (int) timestep) == getAgentLocation(agent2_id, (int) timestep + 1) && 
		getAgentLocation(agent1_id, (int) timestep + 1) == getAgentLocation(agent2_id, (int) timestep);
	}
}

// Get the maximum value in the conflict_matrix
tuple<int, int, int>  BasicSolver::getMaxConflictMatrix(void)
{
	if ((int)conflict_matrix.size() != num_of_agents || (int)conflict_matrix[0].size() != num_of_agents)
	{
		cerr << "Size of the conflict_matrix should be the same as num_of_agents!" << endl;
		exit(-1);
	}

	// Flatten to 1D
	vector<int> oneDimVector;
	for (int i = 0; i < num_of_agents; i++)
	{
		for (int j = 0; j < num_of_agents; j++)
		{
			oneDimVector.push_back(conflict_matrix[i][j]);
		}
	}

	vector<int>::iterator maxElement;
	maxElement = max_element(oneDimVector.begin(), oneDimVector.end());
	int dist = distance(oneDimVector.begin(), maxElement);
	int col = dist % num_of_agents;
	int row = dist / num_of_agents;

	if (screen == 2)
		cout << "\nMax val:" << *maxElement << ", a1:" << row << ", a2:" << col << endl;

	return make_tuple(*maxElement, row, col);
}

// Returns the maximal path length (among all agent)
size_t BasicSolver::getPathsMaxLength()
{
	size_t retVal = 0;
	for (int ag = 0; ag < num_of_agents; ag++)
		if (paths[ag] != nullptr && paths[ag]->size() > retVal)
			retVal = (int)paths[ag]->size();
	return retVal;
}

size_t BasicSolver::getPathsMaxLength(const list<Path*>& in_paths)
{
	size_t retVal = 0;
	for (const auto& it : in_paths)
	{
		if (it != nullptr && it->size() > retVal)
			retVal = it->size();
	}
	return retVal;
}

size_t BasicSolver::getCATLength(const list<Path*>& in_paths)
{
	return std::max(getPathsMaxLength(), getPathsMaxLength(in_paths));
}

int BasicSolver::getPathLocation(Path* p, int time_step)
{
	if(time_step >= (int)p->size())
		return p->back().id;
	else if (time_step < 0)
		return p->front().id;
	else
		return p->at(time_step).id;
}

bool BasicSolver::evaluateSolution() const
{
	if (solution_cost == -1)  // Timeout
		return false;
    for (int i = 0; i < num_of_agents; i++)
    {
        for (size_t timestep = 0; timestep < paths[i]->size() - 1; timestep++)
        {
            int id = paths[i]->at(timestep).id;
            int next_id = paths[i]->at(timestep + 1).id;
            bool connected = false;
            for (auto children : G.children_vertices(id))
            {
                if (children == next_id)
                {
                    connected = true;
                    break;
                }
            }
            if (!connected)
			{
				cout << "not connected" << endl;
                return false;
			}
        }
    }
    list<std::shared_ptr<Conflict>> conflicts;
    for (int i = 0; i < num_of_agents; i++)
    {
        for (int j = i + 1; j < num_of_agents; j++)
        {
            findAgentConflictsEval(conflicts, i, j);
            if (!conflicts.empty())
			{
				if (screen == 1)
				{
					cout << "Conflicts during evaluation:" << endl;
					list<std::shared_ptr<Conflict>>::const_iterator it;
					for (it = conflicts.begin(); it != conflicts.end(); ++it)
						cout << get<0>(**it) << " " << get<1>(**it) << " " << get<2>(**it) << " "
							<< get<3>(**it) << " " << get<4>(**it) << endl;
				}
                return false;
			}
        }
    }
    return true;
}

list<int> BasicSolver::findMetaAgent(int a_id) const
{
	list<int> out_list;
	if (ma_vec[a_id])
	{
		for (const auto& ma_iter: meta_agents)
		{
			if (std::find(ma_iter.begin(), ma_iter.end(), a_id) != ma_iter.end())
			{
				out_list = ma_iter;
				break;
			}
		}
		
		if (out_list.size() == 0)
		{
			cout << "No such meta_agent!!!" << endl;
			exit(1);
		}
	}
	return out_list;
}

void BasicSolver::printMetaAgent(const list<int>& in_ma) const
{
	cout << "[";
	for (const auto& ag: in_ma)
		cout << ag << " ";
	cout << "], " << endl;
}

void BasicSolver::printAllAgents() const
{
	for (const auto& ma_it : meta_agents)
		printMetaAgent(ma_it);
}

void BasicSolver::printPaths(const list<Path*>& in_paths) const
{
	cout << "paths size: " << in_paths.size() << endl;
	for (const auto& p_it : in_paths)
	{
		for (const auto& loc_it: *p_it)
		{
			cout << loc_it.id << " ";
		}
		cout << endl;
	}
}
void BasicSolver::printPaths(const vector<Path*>& in_paths) const
{
    cout << "paths size: " << in_paths.size() << endl;
    for (const auto& p_it : in_paths)
    {
        for (const auto& loc_it: *p_it)
        {
            cout << loc_it.id << " ";
        }
        cout << endl;
    }
}

void BasicSolver::printSinglePath(const Path* path_ptr) const
{
	cout << "path length: " << path_ptr->size() << endl;
	for (const auto& loc_it: *path_ptr)
		cout << loc_it.id << " ";
	cout << endl;
}

void BasicSolver::printCAT(const CAT& in_cat) const
{
	cout << "cat length:" << in_cat.size() << endl;
	for (const auto& cat_it: in_cat)
	{
		cout << "size: " << cat_it.size() << endl;
		std::copy(cat_it.begin(), cat_it.end(), std::ostream_iterator<int>(cout, ", "));
		cout << "\n---------------------------------------------------------------------------" << endl;
	}
	cout << endl;
}

void BasicSolver::printConflicts(const list<std::shared_ptr<Conflict>>& in_confs) const
{
	for (const auto it: in_confs)
	{
		cout << "a1:" << get<0>(*it) << ", a2:" << get<1>(*it) << ", v1:" << get<2>(*it) << ", v2:" << 
			get<3>(*it) << ", t:" << get<4>(*it) << endl; 
	}
}

// find conflicts between paths of agents a1 and a2
void BasicSolver::findAgentConflicts(list<std::shared_ptr<Conflict>>& set, int a1_, int a2_) const
{
    int a1 = paths[a1_]->size() > paths[a2_]->size() ? a1_ : a2_;
    int last_timestep = (int)paths[a1]->size() - 1;
    int a2 = paths[a1_]->size() > paths[a2_]->size() ? a2_ : a1_;

	list<int> ma1 = findMetaAgent(a1);
	list<int> ma2 = findMetaAgent(a2);

	for (int t1  = 0; t1 <= last_timestep; t1++)
	{
		int loc1 = getAgentLocation(a1, t1);
		if (k_robust == 0)
        {
            int loc2 = getAgentLocation(a2, t1);
            int next_loc1 = getAgentLocation(a1, t1 + 1);
            int next_loc2 = getAgentLocation(a2, t1 + 1);

            if (loc1 == loc2)  // vertex conflict
            {
                for (const auto& a1_iter: ma1)
				{
					for (const auto& a2_iter: ma2)
					{
						// if (screen == 1)
						// 	cout << "a1:" << a1_iter << " a2:" << a2_iter << " loc:" << loc1 << endl;
						set.push_back(std::make_shared<Conflict>(a1_iter, a2_iter, loc1, -1, t1));
					}
				}
            }
			
            else if (loc1 != next_loc1 && loc1 == next_loc2 && loc2 == next_loc1)  // edge conflict
            {
				for (const auto& a1_iter: ma1)
				{
					for (const auto& a2_iter: ma2)
					{
						if (screen == 1)
							cout << "a1:" << a1_iter << " a2:" << a2_iter << " loc1:" << loc1 <<  " loc2: "<< loc2 << endl;
						set.push_back(std::make_shared<Conflict>(a1_iter, a2_iter, loc1, loc2, t1+1));
					}
				}
            }			
        } 
		else  // This is for k-robust MAPF
		{
		    for (int t2 = max(0, t1 - k_robust); t2 <= min(last_timestep, t1 + k_robust); t2++)
            {
		        int loc2 = getAgentLocation(a2, t2);
                if (loc1 == loc2)  // vertex conflict
				{
					for (const auto& a1_iter: findMetaAgent(a1))
					{
						for (const auto& a2_iter: findMetaAgent(a2))
							set.push_back(std::make_shared<Conflict>(a1_iter, a2_iter, loc1, -1, min(t1, t2)));
					}
				}
            }
		}
	}
}

void BasicSolver::findAgentConflictsEval(list<std::shared_ptr<Conflict>>& set, int a1_, int a2_) const
{
    int a1 = paths[a1_]->size() > paths[a2_]->size() ? a1_ : a2_;
    int last_timestep = (int)paths[a1]->size() - 1;
    int a2 = paths[a1_]->size() > paths[a2_]->size() ? a2_ : a1_;
	for (int t1  = 0; t1 <= last_timestep; t1++)
	{
		int loc1 = getAgentLocation(a1, t1);
		if (k_robust == 0)
        {
            int loc2 = getAgentLocation(a2, t1);
            int next_loc1 = getAgentLocation(a1, t1 + 1);
            int next_loc2 = getAgentLocation(a2, t1 + 1);
            if (loc1 == loc2)// vertex conflict
            {
                set.push_back(std::make_shared<Conflict>(a1, a2, loc1, -1, t1));
            }
            else if (loc1 != next_loc1 && loc1 == next_loc2 && loc2 == next_loc1)// edge conflict
            {
                set.push_back(std::make_shared<Conflict>(a1, a2, loc1, loc2, t1 + 1));
            }
        } 
		else
		{
		    for (int t2 = max(0, t1 - k_robust); t2 <= min(last_timestep, t1 + k_robust); t2++)
            {
		        int loc2 = getAgentLocation(a2, t2);
                if (loc1 == loc2)// vertex conflict
                    set.push_back(std::make_shared<Conflict>(a1, a2, loc1, -1, min(t1, t2)));
            }
		}
	}
}

std::shared_ptr<Conflict> BasicSolver::chooseConflict(const list<std::shared_ptr<Conflict>>& confs, int8_t mode)
{
	std::shared_ptr<Conflict> out_confs = nullptr;

	switch (mode)
	{
	case 0:  // Random choose a conflict
	{
		int id = rand() % confs.size();
		int i = 0;
		for (const auto it: confs)
		{
			if (i == id)
				out_confs = it;
			else
				i++;
		}
		break;
	}

	case 1:  // Choose the conflict with minimal size of meta-agent
	{
		size_t min_size = INT_MAX;
		vector<std::shared_ptr<Conflict>> tar_confs;
		for (const auto it: confs)
		{
			size_t ma_size = findMetaAgent(get<0>(*it)).size() + findMetaAgent(get<1>(*it)).size();
			if (ma_size < min_size)
			{
				min_size = ma_size;
			}
		}

		for (const auto it: confs)  // Random choose among min-size conflicts
		{
			if (findMetaAgent(get<0>(*it)).size() + findMetaAgent(get<1>(*it)).size() == min_size)
				tar_confs.push_back(it);
		}

		int rand_id = rand() % tar_confs.size();
		out_confs = tar_confs[rand_id];
		break;
	}
	
	case 2:  // Choose the conflict with minimal timestep
	{
		int min_timestep = INT_MAX;
		for (const auto it: confs)
		{
			int cur_timestep = get<4>(*it);
			if (cur_timestep < min_timestep)
			{
				out_confs = it;
				min_timestep = cur_timestep;
			}
		}
		break;
	}

	case 3:  // Choose conflict with most common agent
	{
		// Count agents inside conflicts
		vector<int> ag_count(num_of_agents, 0);
		for (const auto it : confs)
		{
			ag_count[get<0>(*it)] ++;
			ag_count[get<1>(*it)] ++;
		}

		// Choose agent involving maximum number of conflicts
		vector<int>::iterator max_it = std::max_element(ag_count.begin(), ag_count.end());
		int target_ag = std::distance(ag_count.begin(), max_it);

		for (const auto it : confs)
		{
			if (get<0>(*it) == target_ag || get<1>(*it) == target_ag)
			{
				out_confs = it;
				break;
			}
		}
		break;
	}

	default:
		break;
	}

	if (screen == 1)  // debug
	{
		if (mode == 1)
		{
			printAllAgents();
			cout << "------------------------------------------------------------" << endl;
		}

		for (const auto it: confs)
		{
			cout << "conflict: a1:" << get<0>(*it) << ", a2:" << get<1>(*it) << ", v1:" << get<2>(*it) <<  
				", v2:" << get<3>(*it) << ", t:" << get<4>(*it) << endl;
		}
		cout << "------------------------------------------------------------" << endl;
		cout << "Choose conflict:" << endl;
		cout << "a1:" << get<0>(*out_confs) << ", a2:" << get<1>(*out_confs) << ", v1:" << get<2>(*out_confs) << 
			", v2:" << get<3>(*out_confs) << ", t:" << get<4>(*out_confs) << endl;
	}

	return out_confs;
}

int BasicSolver::countConflicts(list<int> in_ma1, list<int> in_ma2)
{
	int counter = 0;
	for (const auto& a1 : in_ma1)
	{
		for (const auto& a2 : in_ma2)
		{
			counter += conflict_matrix[a1][a2];
		}
	}

	// if (screen == 1)  // debug
	// {
	// 	cout << "conflict_matrix" << endl;
	// 	for (int i = 0; i < num_of_agents; i++)
	// 	{
	// 		for (int j = 0; j < num_of_agents; j++)
	// 		{
	// 			cout << conflict_matrix[i][j] << "  ";
	// 		}
	// 		cout << endl;
	// 	}
	// 	cout << endl;
	// }

	return counter;
}

void BasicSolver::initCAT(const list<Path*>& in_other_paths)
{
	if (!is_init_cat)
	{
		if (in_other_paths.size() > 0)
		{
			max_path_len = getCATLength(in_other_paths) + k_robust;
			cat.clear();
			cat.resize(max_path_len);
			init_cat.clear();
			init_cat.resize(max_path_len);
			updateCATOtherPaths(in_other_paths);  // update cat, not init_cat
			std::copy(cat.begin(), cat.end(), init_cat.begin());  // deep copy to init_cat
		}
		else
		{
			max_path_len = getPathsMaxLength() + k_robust;
			cat.clear();
			cat.resize(max_path_len);
			init_cat.clear();
			init_cat.resize(max_path_len);
		}
		is_init_cat = true;

		if (screen == 1 && is_solver)  // debug
		{
			printCAT(init_cat);
		}
	}
	return;
}

// Generates a boolean reservation table (i.e., conflict avoidance table) for paths (cube of map_size*max_timestep).
// This is used by the low-level ECBS to count possible collisions efficiently
// Note -- we do not include the agent for which we are about to plan for
void BasicSolver::updateCATOtherPaths(const list<Path*>& in_other_paths)
{
    for (const auto& path_it : in_other_paths)
	{
		if (k_robust > 0)
		{
			int prev = 0;
			int curr = 1;
			while (curr <= (int)path_it->size())
			{
				if (curr == (int)path_it->size() || path_it->at(prev).id != path_it->at(curr).id)
				{
					int loc = getPathLocation(path_it, prev);
					for (int t = max(0, prev - k_robust); t < curr + k_robust; t++)
						cat[t].insert(loc);
					prev = curr;
				}
				++curr;
			}
		} 
		else
		{
			for (size_t timestep = 0; timestep < max_path_len; timestep++)
			{
				int loc = getPathLocation(path_it, timestep);
				cat[timestep].insert(loc);
				int prev_loc = getPathLocation(path_it, timestep - 1);
				// if (timestep == 1 && is_solver)  // debug
				// {
				// 	cout << loc << endl;
				// 	cout << loc + (1 + prev_loc) * (int)map_size << endl;
				// }
				if (prev_loc != loc)
				{
					cat[timestep].insert(loc + (1 + prev_loc) * (int)map_size);
				}
			}
		}
	}
	return;
}

void BasicSolver::updateCAT(int in_ag, const list<Path*>& in_other_paths)
{
	// clock_t t1 = clock();
	time_pt tstart = std::chrono::steady_clock::now();
	max_path_len = getCATLength(in_other_paths);
	cat.clear();
	cat.resize(max_path_len);

	// initialize cat
	if (is_init_cat)
		std::copy(init_cat.begin(), init_cat.end(), cat.begin());
	else
		initCAT(in_other_paths);

	if (screen == 1 && init_cat.size() > 0)
	{
		cout << "max_path_len: " << max_path_len << endl;
		printPaths(in_other_paths);
		printCAT(init_cat);
		cout << "-------------------------------------------------" << endl;
		printCAT(cat);
		cout << endl;
	}

	for (int i = 0; i < num_of_agents; i++)
	{
		// check whether the agent is in meta-agent or not
		if (i != in_ag && ma_vec[i] == true && paths[i] != nullptr)  // agent i is in meta_agent and has path
		{
		    if (k_robust > 0)
            {
                auto prev = 0;
                auto curr = 1;
                while (curr <= (int)paths[i]->size())
                {
                    if (curr == (int)paths[i]->size() || paths[i]->at(prev).id != paths[i]->at(curr).id)
                    {
                        int loc = getAgentLocation(i, prev);
                        for (int t = max(0, prev - k_robust); t < curr + k_robust; t++)
                            cat[t].insert(loc);
                        prev = curr;
                    }
                    ++curr;
                }
            }
			else
			{
                for (int timestep = 0; timestep < (int) max_path_len; timestep++)
                {
                    int loc = getAgentLocation(i, timestep);
                    cat[timestep].insert(loc);
                    int prev_loc = getAgentLocation(i, timestep - 1);

					// if (loc + (1 + prev_loc) * (int)map_size == 214992 && is_solver)  // debug
					// {
					// 	cout << "other agent: " << i << endl;
					// 	cout << "loc:" << loc << " prev_loc:" << prev_loc << endl;
					// 	cout << "time step: " << timestep << endl;
					// 	cout << "Weird" << endl;
					// }

                    if (prev_loc != loc)
                    {
                        cat[timestep].insert(loc + (1 + prev_loc) * (int)map_size);
                    }
                }
		    }
		}
	}

	runtime_build_CAT += getDuration(tstart, std::chrono::steady_clock::now());
	return;
}
