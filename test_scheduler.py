from scheduler.scheduler import schedule
from scheduler import prep_data


if __name__ == '__main__':

    # 4D: stands, rxs, time periods, variables
    # stand_data, axis_map, valid_mgmts = prep_data.prep_shp_db(
    #     shp="data/test_stands2", 
    #     db="e:/git/growth-yield-batch/projects/__scheduler_test/final/data.db")

    stand_data, axis_map, valid_mgmts = prep_data.from_random(450, 56, 20, 6)

    # Pick a strategy for each stand rx time period variable

    axis_map['variables'] = [
        {   
            'name': 'timber',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0 },
        {   
            'name': 'harvest flow',
            'strategy': 'evenflow', # minimize stddev over time
            'weight': 1.0 },
        # {   
        #     'name': 'harvest flow',
        #     'strategy': 'evenflow_target', # minimize variance around a target
        #     'targets': [200] * 20  # single value or array of values per year
        #     'weight': 1.0 },
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
        #     'name': 'adjacency',
        #     'strategy': 'adjacency',
        #     'map': {
        #         18: [19, 20],
        #         19: [18, 17],
        #         20: [18]
        #     } },
    ]

    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        axis_map,
        valid_mgmts,
        temp_min=sum([x['weight'] for x in axis_map['variables']])/100.0,
        temp_max=sum([x['weight'] for x in axis_map['variables']])*10,
        steps=20000,
        report_interval=500,
    )

    # Report results
    variable_names = [x['name'] for x in axis_map['variables']]
    print "    ", " ".join(["%15s" % x for x in variable_names])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    for i, annual_vars in enumerate(vars_over_time.tolist()):
        print "%4d" % i, " ".join(["%15d" % x for x in annual_vars])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    print "sum ", " ".join(["%15d" % x for x in vars_over_time.sum(axis=0)])
    print "mean", " ".join(["%15d" % (float(x)/(i+1)) for x in vars_over_time.sum(axis=0)])

    # write csv
    csvpath = "optimal_stand_mgmt.csv"
    with open(csvpath, 'w') as fh:
        fh.write("stand,rx,offset\n")
        for i, osrx in enumerate(optimal_stand_rxs):
            txtrow = ",".join([str(x) for x in ([i] + list(axis_map['mgmt'][osrx]))])
            fh.write(txtrow + "\n")
            # print txtrow
    print 
    print "Optimal stand management (rx, offset) written to " + csvpath
    print

