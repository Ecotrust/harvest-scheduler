from harvestscheduler import schedule, prep_data
from harvestscheduler.utils import print_results, write_stand_mgmt_csv

if __name__ == '__main__':
 
    #----------- STEP 1: Read source data -------------------------------------#
    # 4D: stands, rxs, time periods, variables
    stand_data, axis_map, valid_mgmts = prep_data.from_random(1000, 50, 20, 3)

    #----------- STEP 2: Identify and configure variables ---------------------#
    # ORDER MUST MATCH THE DATA COMING FROM prep_data!!!
    axis_map['variables'] = [  
        {   
            'name': 'timber',
            'strategy': 'within_bounds',  # Stay within range
            'targets': (
                [45.0] * 20, # 1 x time periods array of lower bounds
                [55.0] * 20  # 1 x time periods array of upper bounds
            ),
            'weight': 1.0
        },
        {   
            'name': 'carbon',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0
        },
        {   
            'name': 'cost proxy',
            'strategy': 'cumulative_minimize', # target the min cumulative value
            'weight': 1.0
        },
    ]

    #----------- STEP 3: Optimize (annealing over objective function) ---------#
    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        axis_map,
        valid_mgmts,
        steps=250000,
        report_interval=5000,
        temp_min=0.0006,
        temp_max=2,
        live_plot=True
    )

    #----------- STEP 4: output results ---------------------------------------#
    print_results(axis_map, vars_over_time)
    write_stand_mgmt_csv(optimal_stand_rxs, axis_map, filename="_results.csv")
