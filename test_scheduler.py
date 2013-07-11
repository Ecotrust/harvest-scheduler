from scheduler import schedule
import numpy as np
import json
import prep_data

if __name__ == '__main__':

    # 4D: stands, rxs, time periods, variables

    # Option 1: load from files
    try:
        stand_data = np.load('cache.array.npy')
        axis_map = json.loads(open('cache.axis_map').read())
        valid_mgmts = json.loads(open('cache.valid_mgmts').read())
    except:
        stand_data, axis_map, valid_mgmts = prep_data.from_files()

    # Option 2: random data
    # stand_data, axis_map, valid_mgmts = prep_data.from_random()

    # pick a strategy for each stand rx time period variable
    # cumulative_maximize : target the absolute highest cumulative value
    # evenflow            : minimize variance around a target
    # cumulative_minimize : treated as cost; target the lowest cumulative value
    strategies = ['cumulative_maximize', 'cumulative_maximize', 'evenflow', 'cumulative_minimize']
    variable_names = ['carbon', 'harvest', 'harvest flow', 'cost']
    weights = [1.0, 1.0, 1.0, .01]

    # TODO need to define which variable is considered ("harvest")
    # and when rx is changed, check the adjacent stands for each time period
    # penalize/avoid if they have overlapping harvests.
    adjacency = [None for x in range(stand_data.shape[0])]
    adjacency[4] = (3, 2, 4)  # avoid cutting stand 4 when 1,2,3 have harvests?

    # restrict managment options for certain stands
    # valid_mgmts = [None for x in range(stand_data.shape[0])]
    # valid_mgmts[0] = (0, 1, 2)
    # valid_mgmts[1] = (0, 1, 2)
    # valid_mgmts[2] = (0, 1, 2)

    best, optimal_stand_rxs = schedule(
        stand_data,
        strategies,
        weights,
        variable_names,
        adjacency,
        valid_mgmts,
        temp_min=sum(weights)/1000.0,
        temp_max=sum(weights)*5000,
        steps=100000,
        report_interval=10000
    )

    print best
    for osrx in optimal_stand_rxs:
        print axis_map['mgmt'][osrx]
