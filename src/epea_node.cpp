#include "epea_node.h"

// Constructor
EPEANode::EPEANode():
    agent_id(list<int>{-1}), index(0), time_expanded(0), time_generated(0), parent(nullptr), makespan(0), 
    g_val(0), h_val(0), num_of_collisions(0), singleAgentDeltaFs(NULL)
{}

// This is for Root
EPEANode::EPEANode(const Grid2D& in_G, const vector<bool>& in_ma_vec):  // This is for Root node
    agent_id(list<int>{-1}), index(0), time_expanded(0), time_generated(0), parent(nullptr), makespan(0),
	g_val(0), num_of_collisions(0), singleAgentDeltaFs(NULL)
{
    locs.resize(in_G.get_num_of_agents(), -1);
	h_val = 0;
    for (int i = 0; i < (int)locs.size(); i++)
    {
		if (in_ma_vec[i])
		{
	        locs[i] = in_G.start_locations[i];
        	h_val += in_G.heuristics[i][locs[i]];
		}
    }
    arrival_time.resize(in_G.get_num_of_agents(), -1);
}

EPEANode::~EPEANode()
{
	clear();
}

void EPEANode::deep_copy(const EPEANode &cpy)
{
	//Constants
    num_of_collisions = cpy.num_of_collisions;

	//Stats
	makespan = cpy.makespan;
	g_val = cpy.g_val;
	h_val = cpy.h_val;
	parent = cpy.parent;

	// Deep copy
	locs.resize(cpy.locs.size());
	locs.assign(cpy.locs.begin(), cpy.locs.end());
	arrival_time.resize(cpy.arrival_time.size());
	arrival_time.assign(cpy.arrival_time.begin(), cpy.arrival_time.end());
	vertex_cons.resize(cpy.vertex_cons.size());
	vertex_cons.assign(cpy.vertex_cons.begin(), cpy.vertex_cons.end());
	edge_cons.resize(cpy.edge_cons.size());
	edge_cons.assign(cpy.edge_cons.begin(), cpy.edge_cons.end());
	singleAgentDeltaFs = std::shared_ptr<SingleAgentDeltaFs>(new SingleAgentDeltaFs(cpy.singleAgentDeltaFs->size()));
	for (int i = 0; i < (int)singleAgentDeltaFs->size(); i++)
	{
		singleAgentDeltaFs->at(i).resize(cpy.singleAgentDeltaFs->at(i).size());
		singleAgentDeltaFs->at(i).assign(cpy.singleAgentDeltaFs->at(i).begin(), cpy.singleAgentDeltaFs->at(i).end());
	}
	
    // resize(num_of_agents);// For the hasChildrenForCurrentDeltaF call on temporary nodes.
    // Notice that after an agent is moved, all rows up to and including the one of the agent that moved
    // won't be up-to-date.
    fLookup.clear();

	alreadyExpanded = false;  // Creating a new unexpanded node from cpy

	// For intermediate nodes created during expansion 
    // (fully expanded nodes have these fields recalculated when they're expanded)
	targetDeltaF = cpy.targetDeltaF;
	remainingDeltaF = cpy.remainingDeltaF;
						   
	// Not necessarily achievable after some of the agents moved.
    // The above is OK because we won't be using data for agents that already moved.
    maxDeltaF = cpy.maxDeltaF;
}

void EPEANode::update(const EPEANode &cpy)
{
	g_val = cpy.g_val;
	h_val = cpy.h_val;
	maxDeltaF = cpy.maxDeltaF;
	remainingDeltaF = cpy.remainingDeltaF;
	targetDeltaF = cpy.targetDeltaF;
	parent = cpy.parent;
	alreadyExpanded = cpy.alreadyExpanded;
	num_of_collisions = cpy.num_of_collisions;

	// Deep copy
	arrival_time.resize(cpy.arrival_time.size());
	arrival_time.assign(cpy.arrival_time.begin(), cpy.arrival_time.end());

	vertex_cons.resize(cpy.vertex_cons.size());
	vertex_cons.assign(cpy.vertex_cons.begin(), cpy.vertex_cons.end());
	edge_cons.resize(cpy.edge_cons.size());
	edge_cons.assign(cpy.edge_cons.begin(), cpy.edge_cons.end());
}

void EPEANode::clear()
{
	//Save some memory
	arrival_time.clear();
	vertex_cons.clear();
	edge_cons.clear();
	fLookup.clear();
	if (singleAgentDeltaFs != NULL)
		singleAgentDeltaFs->clear();
	alreadyExpanded = false;  // Enables reopening
	targetDeltaF = 0;
	remainingDeltaF = 0;
}

void EPEANode::clearConstraintTable()  // Clear constraint table
{
	vertex_cons.clear();
	edge_cons.clear();
}

void EPEANode::calcSingleAgentDeltaFs(const Grid2D& in_G, const vector<list<Constraint>>& init_cons, const vector<bool>& in_ma_vec)
{
	// Initialization
	singleAgentDeltaFs = std::shared_ptr<SingleAgentDeltaFs>(new SingleAgentDeltaFs(in_G.get_num_of_agents()));
	int hBefore, hAfter;
	maxDeltaF = 0;

	// Set values
	for (int i = 0; i < in_G.get_num_of_agents(); i++)
	{
		if (in_ma_vec[i])
		{
			hBefore = (int)round(in_G.heuristics[i][locs[i]]);
			int singleAgentMaxLegalDeltaF = -1;

			for(int16_t j = 0; j < Grid2D::valid_moves_t::MOVE_COUNT; j++)
			{
				if (isMoveValid(in_G, i, locs[i], locs[i]+in_G.moves_offset[j], in_ma_vec))
				{
					// validate initial constraints
					if (!init_cons[i].empty())
					{
						bool constrained = false;
						for (Constraint c : init_cons[i])
						{
							if (get<2>(c) == makespan &&
								((get<0>(c) == locs[i] && get<1>(c) == locs[i] + in_G.moves_offset[j]) ||
								(get<0>(c) == locs[i] + in_G.moves_offset[j] && get<1>(c) < 0)))
							{
								constrained = true;
								break;
							}
						}
						if (constrained)
							continue;
					}

					hAfter = (int)round(in_G.heuristics[i][locs[i] + in_G.moves_offset[j]]);
					int16_t deltaF  = 0;
					if (hBefore != 0)  // h difference + g difference in this specific domain
						deltaF = (int16_t)(hAfter - hBefore + 1);
					
					// If agent moved from its goal we must count and add all the steps it was stationed at the goal, 
					// since they're now part of its g difference
					else if (hAfter != 0)
						deltaF = (int16_t)(hAfter - hBefore + makespan - arrival_time[i] + 1);
					
					list<pair<int16_t, int16_t>>::iterator it = singleAgentDeltaFs->at(i).begin();
					for(; it != singleAgentDeltaFs->at(i).end() && it->second < deltaF; ++it)
						continue;
					singleAgentDeltaFs->at(i).insert(it, make_pair(j, deltaF));

					singleAgentMaxLegalDeltaF = singleAgentMaxLegalDeltaF > deltaF ? singleAgentMaxLegalDeltaF: deltaF;
				}
			}

			if (singleAgentMaxLegalDeltaF == -1)
			{
				// No legal action for this agent, so no legal children exist for this node
				maxDeltaF = 0; // Can't make it negative without widening the field.
				break;
			}
			maxDeltaF += singleAgentMaxLegalDeltaF;
		}
	}
}

// Check if the move is valid, i.e. not colliding into walls or other agents
bool EPEANode::isMoveValid(const Grid2D& in_G, int agent_id, int curr_loc, int next_loc, const vector<bool>& in_ma_vec) const
{
	if (!in_ma_vec[agent_id])
		return false;
		
	if (0 > next_loc || next_loc >= in_G.get_cols() * in_G.get_rows()
		|| in_G.heuristics[agent_id][next_loc] >= in_G.get_cols() * in_G.get_rows())
		return false;

	int curr_x = (int) floor(curr_loc / in_G.get_cols());
	int curr_y = curr_loc % in_G.get_cols();
	int next_x = (int) floor(next_loc / in_G.get_cols());
	int next_y = next_loc % in_G.get_cols();
	if (abs(curr_x - next_x) + abs(curr_y - next_y) > 1)
		return false;

	for (list<pair<int, int>>::const_iterator it = edge_cons.begin(); it != edge_cons.end(); ++it)
		if (it->first == next_loc  && it->second == curr_loc)
			return false;

	for (list<pair<int, int>>::const_iterator it = vertex_cons.begin(); it != vertex_cons.end(); ++it)
		if (it->first == next_loc)
			return false; 

	return true;
}

void EPEANode::moveTo(const Grid2D& in_G, int in_agent_id, int next_loc, const CAT& in_cat, const vector<bool>& in_ma_vec)
{
	if (in_ma_vec[in_agent_id])
	{
		// Update constraint table
		vertex_cons.push_back(make_pair(next_loc, next_loc));
		edge_cons.push_back(make_pair(locs[in_agent_id], next_loc));

		// Update stats
		int hBefore = in_G.heuristics[in_agent_id][locs[in_agent_id]];
		int hAfter = in_G.heuristics[in_agent_id][next_loc];
		
		if(makespan == 0 && hBefore == 0)
			arrival_time[in_agent_id] = 0;
		
		// arriving at the goal
		else if(hBefore > 0 && hAfter == 0)
			arrival_time[in_agent_id] = makespan + 1;
		
		if (hBefore > 0)
			g_val++;

		// If agent moved from its goal we must count and 
		// add all the steps it was stationed at the goal, 
		// since they're now part of its g difference
		else if (hAfter > 0)
			g_val += makespan + 1 - arrival_time[in_agent_id];
		h_val += hAfter - hBefore;

		// Update location
		locs[in_agent_id] = next_loc;

		// Update number of collision with other paths
		if (!in_cat.empty() && makespan < (int) in_cat.size() && 
			in_cat[makespan].find(next_loc) != in_cat[makespan].end())
			num_of_collisions ++;
	}
}

vector<vector<int>> EPEANode::getPlan(const Grid2D& in_G, const vector<bool>& in_ma_vec)
{
	vector<vector<int>> paths(in_G.get_num_of_agents());
	for(int i = 0; i < in_G.get_num_of_agents(); i++)
		paths[i].resize(arrival_time[i] + 1);
	EPEANode *node = this;
	for (int t = makespan; t >= 0; t--)
	{
		for (int i = 0; i < in_G.get_num_of_agents(); i++)
		{
			if(in_ma_vec[i] && t <= arrival_time[i])
				paths[i][t] = node->locs[i];
		}
		node = node->parent;
	}
	return paths;
}