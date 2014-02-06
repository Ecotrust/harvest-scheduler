from scheduler.scheduler import schedule
from scheduler import prep_data
from scheduler.utils import print_results, write_stand_mgmt_csv

if __name__ == '__main__':
 
    #----------- STEP 1: Read source data -------------------------------------#
    # 4D: stands, rxs, time periods, variables
    # stand_data, axis_map, valid_mgmts = prep_data.prep_shp_db(
    #    shp="data/test_stands2", 
    #    db="e:/git/growth-yield-batch/projects/__scheduler_test/final/data.db")
    
    stand_data, axis_map, valid_mgmts = prep_data.from_random(950, 56, 20, 6)

    #----------- STEP 2: Identify and configure variables ---------------------#
    # THIS MUST MATCH THE DATA COMING FROM prep_data!!!
    axis_map['variables'] = [  
        {   
            'name': 'timber',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0 },
        {   
            'name': 'harvest flow',
            'strategy': 'evenflow', # minimize stddev over time
            'weight': 1.0 },
        {   
            'name': 'carbon',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0 },
        {   
            'name': 'owl habitat',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0 },
        {   
            'name': 'fire hazard',
            'strategy': 'cumulative_minimize', # target the min cumulative value
            'weight': 1.0 },
        {   
            'name': 'cost proxy',
            'strategy': 'cumulative_minimize', # target the min cumulative value
            'weight': 1.0 },
        # {   
        #     'name': 'harvest flow',
        #     'strategy': 'evenflow_target', # minimize variance around a target
        #     'targets': [200] * 20  # single value or array of values per year
        #     'weight': 1.0 },
    ]

    #----------- STEP 3: Optimize (annealing over objective function) ---------#
    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        axis_map,
        valid_mgmts,
        steps=90000,
        report_interval=500,
        temp_min=0.006,
        temp_max=20   
    )

    #----------- STEP 4: output results ---------------------------------------#
    print_results(axis_map, vars_over_time)
    write_stand_mgmt_csv(optimal_stand_rxs, axis_map, filename="__stands_rx.csv")

