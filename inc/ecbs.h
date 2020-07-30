#pragma once
#include "basic_solver.h"
#include "ecbs_node.h"

class ECBS:
    public BasicSolver
{
public:
    // Settings for ecbs only
	double focal_w;
    int merge_th;
    std::string featFile;
    std::string weightFile;
    int focal_mode=0;
    vector<double> feature_weight;
    int testing=0;

    // Constructor and destructor
    ECBS(const Grid2D& G, int k_robust, int screen, double in_time_limit, int in_merge_th, bool in_is_solver, 
        SingleAgentPlanner single_planner, BasicSolver* solver, double in_focal_w, bool in_mr_active, int in_confs_mode, 
        bool in_rs_only, int in_restart_times);
    ~ECBS();

    string get_name(void) const;
    void printResults() const;
    void saveResults(const string& file_name, const string& instance_name);
    inline int getMaxMANum(void) const;
    bool run(list<agent_info> ma_info, list<Path*> in_other_paths);
    void updateFmin();

private:
    ECBSNode* dummy_start;

    SingleAgentPlanner single_planner;  // Not in basic solver
    SingleAgentPlanner optimal_planner;
    BasicSolver* solver;

    bool mr_active;
    int confs_mode = 0;
    bool restart_only;

    int restart_times;
    clock_t restart_duration;
    int restart_counter;

    typedef boost::heap::pairing_heap< ECBSNode*, boost::heap::compare<ECBSNode::compare_node> > heap_open_t;
    heap_open_t open_list;
    list<ECBSNode*> allNodes_table;
    typedef boost::heap::pairing_heap< ECBSNode*, boost::heap::compare<ECBSNode::secondary_compare_node> > heap_focal_t;
    heap_focal_t focal_list;
    double focal_list_threshold;
    int min_sum_f_vals = 0;

    void initialClear();
    void updatePaths(ECBSNode* curr);
    bool findConflictsMA (ECBSNode& node);
    bool findConflicts(ECBSNode& node);
    vector<list<tuple<int, int, bool>>>* collectConstraints(ECBSNode* curr, int ag, const list<agent_info>& ma_info);
    void generateRoot(const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool generateChild(ECBSNode* node, const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    void collectFeature(ECBSNode* node);
    bool findPathForSingleAgent(ECBSNode* node, int ag, 
        const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool findPathForMetaAgent(ECBSNode* node, const list<int>& meta_ag, 
        const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool mergeAgents(list<int> ag1, list<int> ag2);
    void updateFocalList(double old_lower_bound, double new_lower_bound);
    void printFeature();

};
