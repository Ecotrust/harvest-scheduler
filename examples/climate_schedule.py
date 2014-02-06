import sys
sys.path.append('~/src/harvest-scheduler')
from scheduler.scheduler import schedule
from scheduler import prep_data
from scheduler.utils import print_results, write_stand_mgmt_csv

 
climates = [
    "CCSM4-rcp45",
    "CCSM4-rcp60",
    "CCSM4-rcp85",
    "Ensemble-rcp45",
    "Ensemble-rcp60",
    "Ensemble-rcp85",
    "GFDLCM3-rcp45",
    "GFDLCM3-rcp60",
    "GFDLCM3-rcp85",
    "HadGEM2ES-rcp45",
    "HadGEM2ES-rcp60",
    "HadGEM2ES-rcp85",
    "NoClimate"]

for climate in climates:
    print climate

    #----------- STEP 1: Read source data -------------------------------------#
    # 4D: stands, rxs, time periods, variables
    stand_data, axis_map, valid_mgmts = prep_data.prep_db(db="master.sqlite", batch="PN1B", climate=climate)

    #----------- STEP 2: Identify and configure variables ---------------------#
    # THIS MUST MATCH THE DATA COMING FROM prep_data!!!
    axis_map['variables'] = [  
        {   
            'name': 'timber',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 80.0 },
        {   
            'name': 'harvest flow',
            'strategy': 'evenflow', # minimize stddev over time
            'weight': 4.0 },
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
            'weight': 40.0 },
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
        steps=40000,
        report_interval=8000,
        temp_min=0.006,
        temp_max=100
    )

    #----------- STEP 4: output results ---------------------------------------#
    print_results(axis_map, vars_over_time)
    write_stand_mgmt_csv(optimal_stand_rxs, axis_map, filename="%s_stands_rx.csv" % climate, climate=climate)

