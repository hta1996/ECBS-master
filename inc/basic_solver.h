#pragma once
#include "common.h"
#include "grid2D.h"
#include "single_agent.h"

class BasicSolver
{
public:
    const Grid2D& G;
    int k_robust;
    int screen;
    clock_t time_limit;  // unit: micro second

    // MA-CBS
    int num_of_agents;
    list<list<int>> meta_agents;
    vector<bool> ma_vec;
    bool is_solver;  // Whether it is a MA-solver

    // statistics of efficiency
    time_pt run_start = std::chrono::steady_clock::now();
    clock_t runtime = 0;
    clock_t runtime_generate_root = 0;  // runtime of generating root nodes
    clock_t runtime_generate_child = 0;  // runtime of generating child nodes
	clock_t runtime_build_CAT = 0;  // runtime of building conflict avoidance table
	clock_t runtime_path_finding = 0;  // runtime of finding paths for single agents
	clock_t runtime_detect_conflicts = 0;
    clock_t runtime_merge = 0;
    clock_t runtime_solver = 0;

    uint64_t solver_counter = 0;
    uint64_t HL_num_expanded = 0;
    uint64_t HL_num_generated = 0;
    uint64_t LL_num_expanded = 0;
    uint64_t LL_num_generated = 0;
    uint16_t HL_num_merged = 0;
    long long average_delta_collisions=0;

    // statistics of solution quality
    vector < Path* > paths;  // agents paths
    vector <int> paths_costs;
    vector <int> ll_min_f_vals;  // each entry [i] represent the lower bound found for agent[i]
    size_t max_path_len;
    
    bool solution_found = false;
    double solution_cost = 0;

    // Constructor and Distructor
    BasicSolver(const Grid2D& in_G, int k_robust, int screen, double in_time_limit, bool in_is_solver);
	~BasicSolver();

    virtual bool run(list<agent_info> ma_info, list<Path*> in_other_paths) = 0;
    const vector<Path*>& get_solution() const {return paths; };
    
    // print
    // void saveResults(const string& outputFile, const string& agentFile) const;
    bool evaluateSolution() const;
    virtual string get_name(void) const = 0;

protected:
    CAT cat,cat_optimal;  // conflict-avoidance table
    CAT init_cat;  // initial cat storing other paths
    bool is_init_cat;  // check CAT is initialized by other paths

    vector <int> paths_costs_found_initially;
    vector<int> paths_costs_optimal;
    vector <int> ll_min_f_vals_found_initially;  // contains initial ll_min_f_vals found
    vector < Path* > paths_found_initially;  // contain initial paths found
    vector<Path*> path_optimal;
    int sum_of_optiaml_path_cost=0;
    int sum_of_cost_initial=0;

    // vector < Path* > other_paths;  // other agents paths

    // input
    size_t map_size;

    // Hash table of pairs of (meta)agents and number of conflicts
    // key: sorted list of meta_agent (a{1,2}, a3 --> {1, 2, 3}), value: conflict number
    struct list_hash_fn
    {
        std::size_t operator() (const list<int> &in_list) const
        {
            std::size_t temp = 17;
            for (auto it = in_list.begin(); it != in_list.end(); ++it)
            {
                std::cout << "it: " << *it << endl;
                temp = temp * 31 + *it;
            }
            std::cout << temp << endl;
            return temp;
        }
    };
    
    // key: pairs of (meat) agents and flattening to ordered lists
    // eg. {a1, a3}, a2 --> {a1, a2, a3}
    // val: number of conflicts
    // std::unordered_map<list<int>, int, list_hash_fn> num_of_conflicts;

    vector<vector<int>> conflict_matrix;
    vector<vector<int>> conflict_agent;
    int CA_timestamp=0;
    vector<int> indiv_shortest_path_length;

    // Tool functions
    virtual void initialClear() = 0;
    inline int getAgentLocation(int agent_id, int timestep) const;
    inline bool switchedLocations(int agent1_id, int agent2_id, size_t timestep);
    
    tuple<int, int, int> getMaxConflictMatrix(void);  // returns max_val, row, col
    size_t getPathsMaxLength();
    size_t getPathsMaxLength(const list<Path*>& in_paths);
    size_t getCATLength(const list<Path*>& in_paths);
    int getPathLocation(Path* p, int time_step);
    list<int> findMetaAgent(int a_id) const;
    void printMetaAgent(const list<int>& in_ma) const;
    void printAllAgents(void) const;
    void printPaths(const list<Path*>& in_paths) const;
    void printPaths(const vector<Path*>& in_paths) const;
    void printSinglePath(const Path* path_ptr) const;
    void printCAT(const CAT& in_cat) const;
    void printConflicts(const list<std::shared_ptr<Conflict>>& in_confs) const;

    // functions for running High-level search
    void findAgentConflicts(list<std::shared_ptr<Conflict>>& set, int a1, int a2) const;
    void findAgentConflictsEval(list<std::shared_ptr<Conflict>>& set, int a1_, int a2_) const;
    std::shared_ptr<Conflict> chooseConflict(const list<std::shared_ptr<Conflict>>& confs, int8_t mode=0);
    int countConflicts(list<int> in_ma1, list<int> in_ma2);
    
    void initCAT(const list<Path*>& in_other_paths);
    void updateCAT(const int in_ag, const list<Path*>& in_other_paths);
    void updateCATOtherPaths(const list<Path*>& in_other_paths);
};
