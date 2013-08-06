from scheduler.scheduler import schedule
from scheduler import prep_data


if __name__ == '__main__':

    # 4D: stands, rxs, time periods, variables
    # Option 1: load from files
    stand_data, axis_map, valid_mgmts = prep_data.from_shp_csv()
    # Option 2: random data
    # stand_data, axis_map, valid_mgmts = prep_data.from_random()

    ###########################################################################
    # pick a strategy for each stand rx time period variable
    # cumulative_maximize : target the absolute highest cumulative value
    # evenflow_target     : minimize variance around a target
    # evenflow            : minimize stddev over time
    # cumulative_minimize : treated as cost; target the lowest cumulative value
    strategies = ['cumulative_maximize', 'evenflow_target', 'cumulative_maximize', 'cumulative_minimize']
    strategy_variables = [None, 150, None, None]
    variable_names = ['carbon', 'harvest flow', 'owl habitat', 'cost']
    weights = [1.0, 3.0, 1.0, 1.0]

    # TODO need to define which variable is considered ("harvest")
    # and when rx is changed, check the adjacent stands for each time period
    # penalize/avoid if they have overlapping harvests.
    adjacency = [None for x in range(stand_data.shape[0])]
    adjacency[4] = (3, 2, 4)  # avoid cutting stand 4 when 1,2,3 have harvests?

    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        strategies,
        weights,
        variable_names,
        adjacency,
        valid_mgmts,
        strategy_variables,
        temp_min=sum(weights)/1000.0,
        temp_max=sum(weights)*1000,
        steps=300000,
        report_interval=10000
    )

    print "Stand, Rx, Offset"
    for i, osrx in enumerate(optimal_stand_rxs):
        print ", ".join([str(x) for x in ([i] + axis_map['mgmt'][osrx])])
    print

    print "    ", " ".join(["%15s" % x for x in variable_names])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    for i, annual_vars in enumerate(vars_over_time.tolist()):
        print "%4d" % i, " ".join(["%15d" % x for x in annual_vars])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    print "sum ", " ".join(["%15d" % x for x in vars_over_time.sum(axis=0)])
    print "mean", " ".join(["%15d" % (float(x)/(i+1)) for x in vars_over_time.sum(axis=0)])
