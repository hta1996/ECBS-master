#include "grid2D.h"
#include "basic_solver.h"
#include "cbs.h"
#include "ecbs.h"
#include "epea.h"

#include "boost/program_options.hpp"
#include <boost/property_tree/ptree.hpp>

namespace pt = boost::property_tree;

int main(int argc, char** argv) 
{
	namespace po = boost::program_options;
	// Declare the supported options.
	po::options_description desc("Allowed options");
	desc.add_options()
		("help", "produce help message")
		("map,m", po::value<std::string>()->required(), "input file for map")
		("agents,a", po::value<std::string>()->required(), "input file for agents")
		("agentNum,n", po::value<int>()->required(), "number of agents")
		("output,o", po::value<std::string>()->required(), "output file for schedule")
		("solver,s", po::value<int>()->required(), "solver for MAPF")
		("weight,w", po::value<double>()->default_value(1.00), "suboptimal bound for ECBS")
		("mergeTh,b", po::value<int>()->default_value(1), "Merge Threshold for MACBS and MAECBS")
		("cutoffTime,t", po::value<double>()->required(), "cutoff time (seconds)")
		("startID,i", po::value<int>()->default_value(0), "start id for the benchmark")
		("makespan", po::value<int>()->default_value(INT_MAX), "Maximum makespan for single agent solver")
		("seed", po::value<int>()->default_value(0), "random seed")
		("debug", po::value<int>()->default_value(0), "debug")
		("k_robust", po::value<int>()->default_value(0), "k-robust distance")
		("mr", po::value<bool>()->default_value(false), "Merge and Restart.")
		("ro", po::value<bool>()->default_value(false), "Restart without merge, only available for NECBS.")
		("conf,c", po::value<int>()->default_value(0), "Methods to choose a conflict.")
		("sConf", po::value<int>()->default_value(0), "Methods to choose a conflict for MA solver.")
        ("featFile",po::value<std::string>()->default_value("feature.txt"), "The name for feature file")
        ("weightFile",po::value<std::string>()->default_value("NA"), "The name for weight file")
		("rt", po::value<int>()->default_value(0), "Restart for certain duration.")
        ("testing", po::value<int>()->default_value(0), "Testing (1) or not (0).")

	;

	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);

	if (vm.count("help")) {
		std::cout << desc << std::endl;
		return 1;
	}

	po::notify(vm);
	// Loading map and agents
	Grid2D G(vm["agentNum"].as<int>());
    G.testing=vm["testing"].as<int>();
	if (!G.load_map(vm["map"].as<string>()))
	{
	    cerr << "Fail to load the map" << endl;
	    return -1;
	}
	if (!G.load_agents(vm["agents"].as<string>(), vm["startID"].as<int>()))
    {
        cerr << "Fail to load the agents" << endl;
        return -1;
    }
	G.preprocessing_heuristics();

	// Parameters for solvers
	srand(vm["seed"].as<int>());
	int k_robust = vm["k_robust"].as<int>();
	int screen = vm["debug"].as<int>();
	double cutoff_time = vm["cutoffTime"].as<double>();
	double f_weight = vm["weight"].as<double>();
	int mth = vm["mergeTh"].as<int>();
	SingleAgentPlanner single_planner(G.map_size(), vm["makespan"].as<int>());
	int solver_type = vm["solver"].as<int>();
	bool mr_active = vm["mr"].as<bool>();
	bool restart_only = vm["ro"].as<bool>();
	int conf_mode = vm["conf"].as<int>();
	int solver_conf_mode = vm["sConf"].as<int>();
	int restart_times = vm["rt"].as<int>();
    std::string featFile=vm["featFile"].as<std::string>();
    std::string weightFile=vm["weightFile"].as<std::string>();
    int testing=vm["testing"].as<int>();
    
    
	// Choose a solver
	switch (solver_type)
	{
	case 0:  // EPEA*
	{
		EPEA epea(G, k_robust, screen, cutoff_time, false);
		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		epea.run(dummy_info, dummy_other_paths);

		// test the solution
		if (!epea.evaluateSolution() && epea.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}

		if (vm.count("output"))
		{
			epea.printResults();
			epea.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			ofstream stats;
			stats.open("EPEA_path.txt", std::ios::out);
			int soc = 0;
			for (const auto& path: epea.get_solution())
			{
				stats << *path << endl;
				soc += (path->size() - 1);
			}
			cout << "Real Cost: " << soc << endl;
		}
		break;
	}

	case 1:  // CBS
	{
		CBS cbs(G, k_robust, screen, cutoff_time, INT_MAX, false, single_planner, nullptr, false, conf_mode, false, restart_times);

		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		cbs.run(dummy_info, dummy_other_paths);

		// test the solution
		if (!cbs.evaluateSolution() && cbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}

		if (vm.count("output"))
		{
			cbs.printResults();
			cbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			ofstream stats;
			stats.open("CBS_path.txt", std::ios::out);
			int soc = 0;
			for (const auto& path: cbs.get_solution())
			{
				stats << *path << endl;
				soc += (path->size() - 1);
			}
			cout << "Real Cost: " << soc << endl;
		}
		break;
	}

	case 2:  // ECBS
	{
		ECBS ecbs(G, k_robust, screen, cutoff_time, INT_MAX, false, single_planner, nullptr, f_weight, 
			false, conf_mode, false, restart_times);
        ecbs.weightFile=weightFile;
        ecbs.testing=testing;
        if(weightFile=="NA")ecbs.focal_mode=0;
        else
        {
            ecbs.focal_mode=1;
            freopen(weightFile.c_str(),"r",stdin);
            double x;
            ecbs.feature_weight.clear();
            while(scanf("%lf",&x)!=EOF)ecbs.feature_weight.push_back(x);
            ecbs.feature_weight.push_back(0);
            fclose(stdin);
        }
        cerr<<weightFile<<endl;
        //for(auto x:ecbs.feature_weight)cerr<<x<<" ";
        //cerr<<endl;
        
        
        ecbs.featFile=featFile;
		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		ecbs.run(dummy_info, dummy_other_paths);

		// test the solution
		if (!ecbs.evaluateSolution() && ecbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
            //exit(1);
		}

		if (vm.count("output"))
		{
			ecbs.printResults();
			ecbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			ofstream stats;
			stats.open("ECBS_path.txt", std::ios::out);
			int soc = 0;
			for (const auto& path: ecbs.get_solution())
			{
				stats << *path << endl;
				soc += (path->size() - 1);
			}
			cout << "Real Cost: " << soc << endl;
		}
		break;
	}

	case 3:  // MA-CBS (EPEA*)
	{
		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		BasicSolver* solver = new EPEA(G, k_robust, screen, cutoff_time, true);
		
		CBS cbs(G, k_robust, screen, cutoff_time, mth, false, single_planner, solver, mr_active, conf_mode, false, 0);
		cbs.run(dummy_info, dummy_other_paths);
		if (!cbs.evaluateSolution() && cbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}

		// save results
		if (vm.count("output"))
		{
			cbs.printResults();
			cbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			int path_len = 0;
			ofstream stats;
			stats.open("MACBS_EPEA_path.txt", std::ios::out);
			for (const auto& path: cbs.get_solution())
			{
				stats << *path << endl;
				path_len += (path->size() -1);
			}
			cout << "Real Cost: " << path_len << endl;
		}
		break;
	}

	case 4:  // MA-CBS (CBS)
	{
		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		BasicSolver* solver = new CBS(G, k_robust, 0, cutoff_time, INT_MAX, true, single_planner, nullptr, false, solver_conf_mode, false, 0);

		CBS cbs(G, k_robust, screen, cutoff_time, mth, false, single_planner, solver, mr_active, conf_mode, restart_only, restart_times);
		cbs.run(dummy_info, dummy_other_paths);
		
		if (!cbs.evaluateSolution() && cbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}

		// save results
		if (vm.count("output"))
		{
			cbs.printResults();
			cbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			int path_len = 0;
			ofstream stats;
			stats.open("MACBS_CBS_path.txt", std::ios::out);
			for (const auto& path: cbs.get_solution())
			{
				stats << *path << endl;
				path_len += (path->size() -1);
			}
			cout << "Real Cost: " << path_len << endl;
		}
		break;
	}

	case 5:  // MA-ECBS (ECBS)
	{
		if (f_weight == 1)
		{
			cerr << "f_weight should > 0!!" << endl;
			exit(1);
		}

		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		BasicSolver* solver = new ECBS(G, k_robust, 0, cutoff_time, INT_MAX, true, single_planner, nullptr, f_weight, 
			false, solver_conf_mode, false, 0);
		
		ECBS ecbs(G, k_robust, screen, cutoff_time, mth, false, single_planner, solver, f_weight, 
			mr_active, conf_mode, restart_only, restart_times);

		ecbs.run(dummy_info, dummy_other_paths);
		if (!ecbs.evaluateSolution() && ecbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}
		// save results
		if (vm.count("output"))
		{
			ecbs.printResults();
			ecbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			int path_len = 0;
			ofstream stats;
			stats.open("MAECBS_path.txt", std::ios::out);
			for (const auto& path: ecbs.get_solution())
			{
				stats << *path << endl;
				path_len += (path->size() -1);
			}
			cout << "Real Cost: " << path_len << endl;
		}
		break;
	}

	case 6:  // MA-ECBS (EPEA*)
	{
		if (f_weight == 1)
		{
			cerr << "f_weight should > 0!!" << endl;
			exit(1);
		}

		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		BasicSolver* solver = new EPEA(G, k_robust, screen, cutoff_time, true);
		
		ECBS ecbs(G, k_robust, screen, cutoff_time, mth, false, single_planner, solver, f_weight, 
			mr_active, conf_mode, false, restart_times);
			
		ecbs.run(dummy_info, dummy_other_paths);
		if (!ecbs.evaluateSolution() && ecbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}
		// save results
		if (vm.count("output"))
		{
			ecbs.printResults();
			ecbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			int path_len = 0;
			ofstream stats;
			stats.open("MAECBS_EPEA_path.txt", std::ios::out);
			for (const auto& path: ecbs.get_solution())
			{
				stats << *path << endl;
				path_len += (path->size() -1);
			}
			cout << "Real Cost: " << path_len << endl;
		}
		break;
	}

	case 7:  // MA-ECBS (CBS)
	{
		if (f_weight == 1)
		{
			cerr << "f_weight should > 0!!" << endl;
			exit(1);
		}

		list<agent_info> dummy_info;
		list<Path*> dummy_other_paths;
		BasicSolver* solver = new CBS(G, k_robust, 0, cutoff_time, INT_MAX, true, single_planner, nullptr, false, solver_conf_mode, false, 0);
		
		ECBS ecbs(G, k_robust, screen, cutoff_time, mth, false, single_planner, solver, f_weight, 
			mr_active, conf_mode, false, restart_times);

		ecbs.run(dummy_info, dummy_other_paths);
		if (!ecbs.evaluateSolution() && ecbs.solution_cost != -1)
		{
			cerr << "The solution is not feasible!" << endl;
			exit(1);
		}
		// save results
		if (vm.count("output"))
		{
			ecbs.printResults();
			ecbs.saveResults(vm["output"].as<string>(), vm["agents"].as<string>());
		}
		
		if (screen == 1)
		{
			int path_len = 0;
			ofstream stats;
			stats.open("MAECBS_CBS_path.txt", std::ios::out);
			for (const auto& path: ecbs.get_solution())
			{
				stats << *path << endl;
				path_len += (path->size() -1);
			}
			cout << "Real Cost: " << path_len << endl;
		}
		break;
	}

	case 8:  // Evaluate the path only
	{
		CBS cbs(G, k_robust, screen, cutoff_time, INT_MAX, false, single_planner, nullptr, mr_active, conf_mode, false, 0);
		for (int i = 0; i < G.get_num_of_agents(); i++)
		{
			vector<int> out_path = G.load_path("/home/rdaneel/MACBS_EPEA_path.txt", i);
			cbs.paths.push_back(new Path(out_path.size()));
			for (int t = 0; t < (int)out_path.size(); t++)
				cbs.paths.back()->at(t).id = out_path[t];
		}

		for (int i = 0; i < G.get_num_of_agents(); i++)
		{
			cout << "Agent [" << i << "] ";
			for (size_t t = 0; t < cbs.paths[i]->size(); t++)
			{
				cout << cbs.paths[i]->at(t).id << ",";
			}
			cout << endl;
		}

		if (cbs.evaluateSolution())
			cout << "The solution is conflict-free!" << endl;
		else
			cout << "The solution is not feasible!" << endl;
		break;
	}

	default:
		break;
	}
	
	return 0;
}
