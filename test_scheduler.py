from scheduler.scheduler import schedule
from scheduler import prep_data


if __name__ == '__main__':

    # 4D: stands, rxs, time periods, variables
    stand_data, axis_map, valid_mgmts = prep_data.from_shp_csv(shp="data/test_stands2", 
                                                               csvdir="data/csvs2")

    # Pick a strategy for each stand rx time period variable
    #  cumulative_maximize : target the absolute highest cumulative value
    #  evenflow_target     : minimize variance around a target
    #  evenflow            : minimize stddev over time
    #  cumulative_minimize : treated as cost; target the lowest cumulative value
    variable_names = ['harvest', 'harvest flow', 'carbon', 'owl habitat', 'fire hazard', 'cost proxy']
    strategies = ['cumulative_maximize', 'evenflow', 'cumulative_maximize', 'cumulative_maximize', 'cumulative_minimize', 'cumulative_minimize']
    weights = [8.0, 4.0, 1.0, 1.0, 1.0, 1.0]

    #flow = [250] * 2 + [140] * 6 + [500] + [100] * 11
    #flow = [320, 40] * 10
    #strategy_variables = [None, flow, None, None]
    strategy_variables = [None] * 6

    adjacency = {
        # 18: [19, 20],
        # 19: [18, 17],
        # 20: [18]
    }

    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        strategies,
        weights,
        variable_names,
        valid_mgmts,
        strategy_variables,
        adjacency,
        temp_min=sum(weights)/100.0,
        temp_max=sum(weights)*100,
        steps=250000,
        report_interval=25000
    )

    # Report results
    print "Stand, Rx, Offset"
    for i, osrx in enumerate(optimal_stand_rxs):
        print ", ".join([str(x) for x in ([i] + list(axis_map['mgmt'][osrx]))])
    print

    print "    ", " ".join(["%15s" % x for x in variable_names])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    for i, annual_vars in enumerate(vars_over_time.tolist()):
        print "%4d" % i, " ".join(["%15d" % x for x in annual_vars])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    print "sum ", " ".join(["%15d" % x for x in vars_over_time.sum(axis=0)])
    print "mean", " ".join(["%15d" % (float(x)/(i+1)) for x in vars_over_time.sum(axis=0)])
