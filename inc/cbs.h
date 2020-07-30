#pragma once
#include "basic_solver.h"
#include "cbs_node.h"

class CBS:
    public BasicSolver
{
public:
    //Settings for ecbs only
    int merge_th;

    // Constructor and destructor
    CBS(const Grid2D& in_G, int k_robust, int screen, double in_time_limit, int in_merge_th, 
        bool in_is_solver, SingleAgentPlanner single_planner, BasicSolver* solver, bool in_mr_active, int in_conf_mode,
        bool in_rs_only, int in_restart_times);
    ~CBS();

    string get_name(void) const;
    void printResults() const;
    void saveResults(const string& file_name, const string& instance_name);
    inline int getMaxMANum(void) const;
    bool run(list<agent_info> ma_info, list<Path*> in_other_paths);

private:
    CBSNode* dummy_start;

    SingleAgentPlanner single_planner; // Not in basic solver
    BasicSolver* solver;

    bool mr_active;
    int confs_mode = 0;
    bool restart_only;

    int restart_times;
    clock_t restart_duration;
    int restart_counter;

    typedef boost::heap::pairing_heap< CBSNode*, boost::heap::compare<CBSNode::compare_node> > heap_open_t;
    heap_open_t open_list;
    list<CBSNode*> allNodes_table;
    int min_sum_f_vals = 0;

    void initialClear();
    void updatePaths(CBSNode* curr);
    bool findConflictsMA (CBSNode& node);
    bool findConflicts(CBSNode& node);
    vector<list<tuple<int, int, bool>>>* collectConstraints(CBSNode* curr, int ag, const list<agent_info>& ma_info);
    void generateRoot(const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool generateChild(CBSNode* node, const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool findPathForSingleAgent(CBSNode*  node, int ag, 
        const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool findPathForMetaAgent(CBSNode* node, const list<int>& meta_ag, 
        const list<agent_info>& ma_info, const list<Path*>& in_other_paths);
    bool mergeAgents(list<int> ag1, list<int> ag2);
};