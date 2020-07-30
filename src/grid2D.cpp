#include "grid2D.h"

Grid2D::Grid2D(int num_of_agents):
	num_of_agents(num_of_agents){}

bool Grid2D::load_map(string fname)
{	
	using namespace boost;
	using namespace std;

	ifstream myfile(fname.c_str());
	if (!myfile.is_open())
		return false;

	string line;
	tokenizer< char_separator<char> >::iterator beg;
	getline(myfile, line);
	if (line[0] == 't') // Nathan's benchmark
	{
		char_separator<char> sep(" ");
		getline(myfile, line);
		tokenizer< char_separator<char> > tok(line, sep);
		beg = tok.begin();
		beg++;
		rows = atoi((*beg).c_str()); // read number of rows
		getline(myfile, line);
		tokenizer< char_separator<char> > tok2(line, sep);
		beg = tok2.begin();
		beg++;
		cols = atoi((*beg).c_str()); // read number of cols
		getline(myfile, line); // skip "map"
	}
	else // my benchmark
	{
		char_separator<char> sep(",");
		tokenizer< char_separator<char> > tok(line, sep);
		beg = tok.begin();
		rows = atoi((*beg).c_str()); // read number of rows
		beg++;
		cols = atoi((*beg).c_str()); // read number of cols
	}

	my_map.resize(cols * rows, false);  // true: is obstacle

	// read map (and start/goal locations)
	for (int i = 0; i < rows; i++) {
		getline(myfile, line);
		for (int j = 0; j < cols; j++) {
			my_map[linearize_coordinate(i, j)] = (line[j] != '.');
		}
	}
	myfile.close();

	// initialize moves_offset array
	moves_offset[Grid2D::valid_moves_t::WAIT_MOVE] = 0;
    moves_offset[Grid2D::valid_moves_t::NORTH] = -cols;
    moves_offset[Grid2D::valid_moves_t::EAST] = 1;
    moves_offset[Grid2D::valid_moves_t::SOUTH] = cols;
    moves_offset[Grid2D::valid_moves_t::WEST] = -1;
	return true;
}

bool Grid2D::load_agents(string fname, int start_id)
{
	using namespace std;
	using namespace boost;

	string line;
	ifstream myfile (fname.c_str());
	if (!myfile.is_open()) 
		return false;

	getline(myfile, line);
	if (line[0] == 'v') // Nathan's benchmark
	{
		if (num_of_agents == 0)
		{
			cerr << "The number of agents should be larger than 0" << endl;
			exit(-1);
		}
        if (testing==0)
        {
            cerr<<"random agent!!"<<endl;
            vector<int> tmp_start,tmp_goal;
            tmp_start.clear();
            tmp_goal.clear();
            start_locations.resize(num_of_agents);
            goal_locations.resize(num_of_agents);
            char_separator<char> sep("\t");

            // Discard line before start_id
            for (int i = 0; i < start_id; i++)
            {
                getline(myfile, line);
            }
            vector<int> idx;
            idx.clear();
            for (int i = 0; i < 400; i++)
            {
                idx.push_back(i);
                getline(myfile, line);
                tokenizer< char_separator<char> > tok(line, sep);
                tokenizer< char_separator<char> >::iterator beg = tok.begin();
                beg++; // skip the first number
                beg++; // skip the map name
                beg++; // skip the columns
                beg++; // skip the rows
                
                // read start [row,col] for agent i
                int col = atoi((*beg).c_str());
                beg++;
                int row = atoi((*beg).c_str());
                tmp_start.push_back(linearize_coordinate(row, col));

                // read goal [row,col] for agent i
                beg++;
                col = atoi((*beg).c_str());
                beg++;
                row = atoi((*beg).c_str());
                tmp_goal.push_back(linearize_coordinate(row, col));
            }
            random_shuffle(idx.begin(),idx.end());
            for(int i=0;i<num_of_agents;i++)
            {
                start_locations[i]=tmp_start[idx[i]],
                goal_locations[i]=tmp_goal[idx[i]];
            }
        }else
        {
            start_locations.resize(num_of_agents);
            goal_locations.resize(num_of_agents);
            char_separator<char> sep("\t");

            // Discard line before start_id
            for (int i = 0; i < start_id; i++)
            {
                getline(myfile, line);
            }

            for (int i = 0; i < num_of_agents; i++)
            {
                getline(myfile, line);
                tokenizer< char_separator<char> > tok(line, sep);
                tokenizer< char_separator<char> >::iterator beg = tok.begin();
                beg++; // skip the first number
                beg++; // skip the map name
                beg++; // skip the columns
                beg++; // skip the rows
                
                // read start [row,col] for agent i
                int col = atoi((*beg).c_str());
                beg++;
                int row = atoi((*beg).c_str());
                start_locations[i] = linearize_coordinate(row, col);

                // read goal [row,col] for agent i
                beg++;
                col = atoi((*beg).c_str());
                beg++;
                row = atoi((*beg).c_str());
                goal_locations[i] = linearize_coordinate(row, col);
            }
        }

		// debug
		// printAgentsInfo();
	}
	else // My benchmark
	{
		char_separator<char> sep(",");
		tokenizer< char_separator<char> > tok(line, sep);
		tokenizer< char_separator<char> >::iterator beg = tok.begin();
		num_of_agents = atoi((*beg).c_str());
		start_locations.resize(num_of_agents);
		goal_locations.resize(num_of_agents);
		for (int i = 0; i<num_of_agents; i++)
		{
			getline(myfile, line);
			tokenizer<char_separator<char>> col_tok(line, sep);
			tokenizer<char_separator<char>>::iterator c_beg = col_tok.begin();
			pair<int, int> curr_pair;
			
			// read start [row,col] for agent i
			int row = atoi((*c_beg).c_str());
			c_beg++;
			int col = atoi((*c_beg).c_str());
			start_locations[i] = linearize_coordinate(row, col);
			
			// read goal [row,col] for agent i
			c_beg++;
			row = atoi((*c_beg).c_str());
			c_beg++;
			col = atoi((*c_beg).c_str());
			goal_locations[i] = linearize_coordinate(row, col);
		}
		cout << "num_of_agents " << num_of_agents << endl;
	}
	myfile.close();
	return true;
}

vector<int> Grid2D::load_path(string fname, int in_agent_id)
{
	using namespace boost;
	using namespace std;

	string line;
	ifstream myfile (fname.c_str());
	if (!myfile.is_open()) 
		exit(1);

	vector<int> output_path;
	char_separator<char> sep(",");
	for (int i = 0; i < num_of_agents; i++)
	{
		getline(myfile, line);
		if (i == in_agent_id)
		{
			tokenizer<char_separator<char>> tok(line, sep);
			for (tokenizer< char_separator<char> >::iterator beg = tok.begin(); beg != tok.end(); beg++)
				output_path.push_back(atoi((*beg).c_str()));
			break;
		}
	}
	return output_path;
}

list<int> Grid2D::children_vertices(int vertex_id) const
{
	list<int> vertices;
	for (int direction = 0; direction < 5; direction++)
	{
		int next_id = vertex_id + moves_offset[direction];
		if (0 <= next_id && next_id < cols * rows && !my_map[next_id] && abs(next_id % cols - vertex_id % cols) < 2)
			vertices.push_back(next_id);
	}
	return vertices;
}


void Grid2D::preprocessing_heuristics()
{
	time_pt tstart = std::chrono::steady_clock::now();
	
	size_t num_of_agents = start_locations.size();
	heuristics.resize(num_of_agents);
	for (size_t i = 0; i < num_of_agents; i++)
	{
		compute_heuristics(goal_locations[i], heuristics[i]);
	}

	clock_t tmp_time = getDuration(tstart, std::chrono::steady_clock::now());
	pre_time = (double) tmp_time / CLOCKS_PER_SEC;
}

// compute low-level heuristics
void Grid2D::compute_heuristics(int goal_location, vector<int>& heuristics)
{
	struct MyNode
	{
		int loc;
		int g_val;
		bool in_openlist;

		// the following is used to comapre nodes in the OPEN list
		struct compare_node
		{
			// returns true if n1 > n2 (note -- this gives us *min*-heap).
			bool operator()(const MyNode* n1, const MyNode* n2) const
			{
				return n1->g_val >= n2->g_val;
			}
		};  // used by OPEN (heap) to compare nodes (top of the heap has min g-val)

		// define a typedefs for handles to the heaps (allow up to quickly update a node in the heap)
		typedef pairing_heap< MyNode*, boost::heap::compare<MyNode::compare_node> >
			::handle_type open_handle_t;

		open_handle_t open_handle;

		MyNode() {}
		MyNode(int loc, int g_val, bool in_openlist = false) : loc(loc), g_val(g_val), in_openlist(in_openlist) {}

		// The following is used for checking whether two nodes are equal
		// we say that two nodes, s1 and s2, are equal if
		// both agree on the location and timestep
		struct eqnode
		{
			bool operator()(const MyNode* s1, const MyNode* s2) const
			{
				return (s1 == s2) || (s1 && s2 &&
					s1->loc == s2->loc);
			}
		};

		// The following is used for generating the hash value of a nodes
		struct NodeHasher
		{
			std::size_t operator()(const MyNode* n) const
			{
				return std::hash<int>()(n->loc);
			}
		};
	};

	int root_location = goal_location;

	// generate a heap that can save nodes (and a open_handle)
	pairing_heap< MyNode*, compare<MyNode::compare_node> > heap;
	pairing_heap< MyNode*, compare<MyNode::compare_node> >::handle_type open_handle;

	// generate hash_map (key is a node pointer, data is a node handler,
	//                    NodeHasher is the hash function to be used,
	//                    eqnode is used to break ties when hash values are equal)
	unordered_set<MyNode*, MyNode::NodeHasher, MyNode::eqnode> nodes;

	MyNode* root = new MyNode(root_location, 0);
	root->open_handle = heap.push(root); // add root to heap
	nodes.insert(root); // add root to hash_table (nodes)
	while (!heap.empty())
	{
		MyNode* curr = heap.top();
		heap.pop();
		auto neighbours = children_vertices(curr->loc);
		for (auto next_loc : neighbours)
		{
			int next_g_val = (int)curr->g_val + 1;
			MyNode* next = new MyNode(next_loc, next_g_val);
			auto it = nodes.find(next);
			if (it == nodes.end()) 
			{  
				// add the newly generated node to heap and hash table
				next->open_handle = heap.push(next);
				nodes.insert(next);
			}
			else 
			{  
				// update existing node's g_val if needed (only in the heap)
				delete(next);  // not needed anymore -- we already generated it before
				MyNode* existing_next = *it;
				if (existing_next->g_val > next_g_val) 
				{
					existing_next->g_val = next_g_val;
					heap.update((*it)->open_handle);
				}
			}
		}
	}
	// iterate over all nodes
	heuristics.resize(rows * cols, INT_MAX);
	for (auto it = nodes.begin(); it != nodes.end(); it++)
	{
		MyNode* s = *it;
		heuristics[s->loc] = (int)s->g_val;
		delete (s);
	}
	nodes.clear();
	heap.clear();
}

void Grid2D::printAgentsInfo(void)
{
	cout << "==================== Agents ====================" << endl;
	cout << format("%-5s | %-5s | %-5s") % "agent" % "start" % "goal" << endl;
	for (int i = 0; i < num_of_agents; i++)
	{
		cout << format("%-5d | %-5d | %-5d") % i % start_locations[i] % goal_locations[i] << endl;
	}
	cout << "================== Agents END ==================" << endl;
}
