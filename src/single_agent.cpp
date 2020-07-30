#include "single_agent.h"


void SingleAgentPlanner::clear()
{
	this->num_expanded = 0;
	this->num_generated = 0;
	this->path_cost = 0;
	this->lower_bound = 0;
	this->min_f_val = 0;
	open_list.clear();
	focal_list.clear();
	allNodes_table.clear();
}


// Updates the path.
void SingleAgentPlanner::updatePath(Node* goal)
{
	path.clear();
	Node* curr = goal;
	while (curr->timestep != 0) 
	{
		path.resize(path.size() + 1);
		path.back().id = curr->id;
		curr = curr->parent;
	}
	path.resize(path.size() + 1);
	path.back().id = curr->id;
	reverse(path.begin(), path.end());
	path_cost = goal->g_val;
	num_of_conf = goal->num_internal_conf;
}

void SingleAgentPlanner::releaseClosedListNodes(hashtable_t& allNodes_table)
{
	hashtable_t::iterator it;
	for (it=allNodes_table.begin(); it != allNodes_table.end(); it++) 
	{
		delete *it; 
	}
}


// iterate over the constraints ( cons[t] is a list of all constraints for timestep t) and return the latest
// timestep which has a constraint involving the goal location
// which is the minimal plan length for the agent
int SingleAgentPlanner::extractLastGoalTimestep(int goal_location, const vector< list< tuple<int, int, bool> > >* cons)
{
	if (cons == NULL)
		return -1;
	for (int t = (int)cons->size() - 1; t > 0; t--)
	{
		for (auto it = cons->at(t).begin(); it != cons->at(t).end(); ++it)
		{
			if (get<0>(*it) == goal_location && get<1>(*it) < 0 && !get<2>(*it)) 
			{
				return (t);
			}
		}
	}
	return -1;
}

// Checks if a valid path found (wrt my_map and constraints)
// input: curr_id (location at time next_timestep-1) ; next_id (location at time next_timestep); next_timestep
// cons[timestep] is a list of <loc1,loc2, bool> of (vertex/edge) constraints for that timestep. (loc2=-1 for vertex constraint).
bool SingleAgentPlanner::isConstrained(int curr_id, int next_id, int next_timestep,
	const vector< list< tuple<int, int, bool> > >* cons)  const
{
	if (cons == NULL)
		return false;
	// check vertex constraints (being in next_id at next_timestep is disallowed)
	if ( next_timestep < static_cast<int>(cons->size()) ) 
	{
		for (const auto & it : cons->at(next_timestep))
		{
			if (get<2>(it))  // positive constraint
			{
				if(get<0>(it) != next_id)  // can only stay at constrained location
					return true;
			}
			else  // negative constraint
			{
				if ( (get<0>(it) == next_id && get<1>(it) < 0)  // vertex constraint
					|| (get<0>(it) == curr_id && get<1>(it) == next_id))  // edge constraint
					return true;
			}
		}
	}
	return false;
}

// Return the number of conflicts between the known_paths' (by looking at the reservation table) for the move [curr_id,next_id].
// Returns 0 if no conflict, 1 for vertex or edge conflict, 2 for both.
int SingleAgentPlanner::numOfConflictsForStep(int curr_loc, int next_loc, int next_timestep, const CAT& res_table, size_t map_size)
{
	if (res_table.empty())
	{
		return 0;
	}
	int retVal = 0;
  	if (next_timestep >= (int)res_table.size()) {
    	// check vertex constraints (being at an agent's goal when he stays there because he is done planning)
    	if ( res_table.back().find(next_loc) != res_table.back().end())
      		retVal++;
    // Note -- there cannot be edge conflicts when other agents are done moving
  	} else {
		// check vertex constraints (being in next_id at next_timestep is disallowed)
		if ( res_table[next_timestep].find(next_loc) != res_table[next_timestep].end())
			retVal++;
		// check edge constraints (the move from curr_id to next_id at next_timestep-1 is disallowed)
		// which means that res_table is occupied with another agent for [curr_id,next_timestep] and [next_id,next_timestep-1]
		if ( res_table[next_timestep].find(curr_loc + (1 + next_loc) *(int)map_size) != res_table[next_timestep].end())
			retVal++;
  	}
  	return retVal;
}

// Iterate over OPEN and adds to FOCAL all nodes with: 
// 1) f-val > old_min_f_val ; and 
// 2) f-val * f_weight < new_lower_bound.
void SingleAgentPlanner::updateFocalList(double old_lower_bound, double new_lower_bound, double f_weight)
{
	for (Node* n : open_list)
	{
		if ( n->getFVal() > old_lower_bound && n->getFVal() <= new_lower_bound )
		{
			n->focal_handle = focal_list.push(n);
		}
	}
}

// Returns true if a collision free path found (with cost up to f_weight * f-min) while
// minimizing the number of internal conflicts (that is conflicts with known_paths for other agents found so far).
// res_table is the same as cat
bool SingleAgentPlanner::runFocalSearch(const Grid2D& G, int agent_id, double f_weight,
                                        const vector < list< tuple<int, int, bool> > >* constraints,
                                        const CAT& res_table)
{
    clear();
    hashtable_t::iterator it;  // will be used for find()

    // generate start and add it to the OPEN list
    int start_id = G.start_locations[agent_id];
    Node* start = new Node(start_id, 0, G.heuristics[agent_id][start_id], NULL, 0);
    num_generated++;

    start->open_handle = open_list.push(start);
    start->focal_handle = focal_list.push(start);
    start->in_openlist = true;
    allNodes_table.insert(start);
    min_f_val = start->getFVal();
    lower_bound = f_weight * min_f_val; // max(lowerbound, f_weight * min_f_val);

    int lastGoalConsTime = extractLastGoalTimestep(G.get_location(G.goal_locations[agent_id]), constraints);

    while ( !focal_list.empty() )
    {
        Node* curr = focal_list.top(); 

        focal_list.pop();
        open_list.erase(curr->open_handle);
        curr->in_openlist = false;
        num_expanded++;

        // check if the popped node is a goal
        if (curr->id == G.goal_locations[agent_id] && curr->timestep > lastGoalConsTime)
        {
            updatePath(curr);
            releaseClosedListNodes(allNodes_table);
            return true;
        }

        // iterator over all possible actions
        auto neighbours = G.children_vertices(curr->id);
        for (auto next_id : neighbours)
        {
            int next_timestep = curr->timestep + 1;

            if (!isConstrained(G.get_location(curr->id), G.get_location(next_id), next_timestep, constraints))
            {
                // compute cost to next_id via curr node
                int next_g_val = curr->g_val + 1;
                int next_h_val = G.heuristics[agent_id][next_id];
                int next_internal_conflicts = 0;
                next_internal_conflicts = curr->num_internal_conf + numOfConflictsForStep(G.get_location(curr->id),
                    G.get_location(next_id), next_timestep, res_table, G.map_size());

                // generate (maybe temporary) node
                Node* next = new Node(next_id, next_g_val, next_h_val, curr, next_timestep, next_internal_conflicts);

                // try to retrieve it from the hash table
                it = allNodes_table.find(next);

                if (it == allNodes_table.end())
                {
                    next->open_handle = open_list.push(next);
                    next->in_openlist = true;
                    num_generated++;

                    if (next->getFVal() <= lower_bound)
                        next->focal_handle = focal_list.push(next);
                    allNodes_table.insert(next);
                }
                else
                {  
                    // update existing node's if needed (only in the open_list)
                    delete(next);  // not needed anymore -- we already generated it before
                    Node* existing_next = *it;

                    if (existing_next->in_openlist)  // if its in the open list
                    {   
                        if (existing_next->getFVal() > next_g_val + next_h_val ||
                        (existing_next->getFVal() == next_g_val + next_h_val &&
                        existing_next->num_internal_conf > next_internal_conflicts))
                        {
                            // if f-val decreased through this new path (or it remains the same and there's less internal conflicts)
                            bool add_to_focal = false;  // check if it was above the focal bound before and now below (thus need to be inserted)
                            bool update_in_focal = false;  // check if it was inside the focal and needs to be updated (because f-val changed)
                            bool update_open = false;
                            if ((next_g_val + next_h_val) <= lower_bound)
                            {   // if the new f-val qualify to be in FOCAL
                                if (existing_next->getFVal() > lower_bound)
                                    add_to_focal = true;  // and the previous f-val did not qualify to be in FOCAL then add
                                else
                                    update_in_focal = true;  // and the previous f-val did qualify to be in FOCAL then update
                            }
                            if (existing_next->getFVal() > next_g_val + next_h_val)
                                update_open = true;
                            // update existing node
                            existing_next->g_val = next_g_val;
                            existing_next->h_val = next_h_val;
                            existing_next->parent = curr;
                            existing_next->num_internal_conf = next_internal_conflicts;

                            if (update_open)
                            {
                                open_list.increase(existing_next->open_handle);  // increase because f-val improved
                            }
                            if (add_to_focal)
                            {
                                existing_next->focal_handle = focal_list.push(existing_next);
                            }
                            if (update_in_focal)
                            {
                                focal_list.update(existing_next->focal_handle);
                            }
                        }
                    }
                    else
                    {  
                        // if its in the closed list (reopen)
                        if (existing_next->getFVal() > next_g_val + next_h_val ||
                        (existing_next->getFVal() == next_g_val + next_h_val 	&&
                        existing_next->num_internal_conf > next_internal_conflicts))
                        {
                            // if f-val decreased through this new path (or it remains the same and there's less internal conflicts)
                            existing_next->g_val = next_g_val;
                            existing_next->h_val = next_h_val;
                            existing_next->parent = curr;
                            existing_next->num_internal_conf = next_internal_conflicts;
                            existing_next->open_handle = open_list.push(existing_next);
                            existing_next->in_openlist = true;
                            if (existing_next->getFVal() <= lower_bound)
                            {
                                existing_next->focal_handle = focal_list.push(existing_next);
                            }
                        }
                    }  // end update a node in closed list
                }  // end update an existing node
            }
        }  // end for loop that generates successors

        if (open_list.empty())  // in case OPEN is empty, no path found...
            break;

        // update FOCAL if min f-val increased
        auto open_head = open_list.top();
        if ( open_head->getFVal() > min_f_val )
        {
            int new_min_f_val = open_head->getFVal();
            double new_lower_bound = f_weight * new_min_f_val; // max(lowerbound, f_weight * new_min_f_val);
            updateFocalList(lower_bound, new_lower_bound, f_weight);
            min_f_val = new_min_f_val;
            lower_bound = new_lower_bound;
        }
    }  // end while loop
    // no path found
    path.clear();
    releaseClosedListNodes(allNodes_table);
    return false;
}
