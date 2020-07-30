#pragma once
#include "common.h"

class Grid2D
{
public:
    vector<int> start_locations;
    vector<int> goal_locations;
    vector< vector<int> > heuristics; // [agent_id][loc]
    vector<bool> my_map;
    double pre_time;  // Time for preprocessing heuristics
    int testing=0;
    enum valid_moves_t { NORTH, EAST, SOUTH, WEST, WAIT_MOVE, MOVE_COUNT };  // MOVE_COUNT is the enum's size
    int moves_offset[5];

    list<int> children_vertices(int vertex_id) const;
    bool is_node_conflict(int id_0, int id_1) const {return id_0 == id_1; }
    bool is_edge_conflict(int from_0, int to_0, int from_1, int to_1) const
    {
        return from_0 == to_1 && from_1 == to_0;
    }

    int get_location(int id) const { return id; }
    inline size_t map_size() const { return rows * cols; }
    inline int get_rows() const { return rows;}
    inline int get_cols() const { return cols;}
    inline int get_num_of_agents() const {return num_of_agents;}
    int* get_move_offset();

    Grid2D() {}
    Grid2D(int num_of_agents=0);
    bool load_map(string fname); // Load map from file
    bool load_agents(string fname, int start_id=0); // Load map from file
    vector<int> load_path(string fname, int in_agent_id=0);

    void preprocessing_heuristics();
    void printAgentsInfo(void);

private:
    int rows;
    int cols;
    int num_of_agents;

    inline int linearize_coordinate(int row, int col) const { return (this->cols * row + col); }
    inline int row_coordinate(int id) const { return id / this->cols; }
    inline int col_coordinate(int id) const { return id % this->cols; }
    void compute_heuristics(int goal_location, vector<int>& heuristics);
};
