
# Report results
def print_results(axis_map, vars_over_time):
    variable_names = [x['name'] for x in axis_map['variables']]
    print "    ", " ".join(["%15s" % x for x in variable_names])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    for i, annual_vars in enumerate(vars_over_time.tolist()):
        print "%4d" % i, " ".join(["%15d" % x for x in annual_vars])
    print "----|" + "".join([("-" * 15) + "|" for x in variable_names])
    print "sum ", " ".join(["%15d" % x for x in vars_over_time.sum(axis=0)])
    print "mean", " ".join(["%15d" % (float(x)/(i+1)) for x in vars_over_time.sum(axis=0)])

# write csv
def write_stand_mgmt_csv(optimal_stand_rxs, axis_map, filename=None):
    if not filename:
        filename = "__optimal_stand_mgmt.csv"

    with open(filename, 'w') as fh:
        fh.write("stand,rx,offset\n")
        for i, osrx in enumerate(optimal_stand_rxs):
            txtrow = ",".join([str(x) for x in ([i] + list(axis_map['mgmt'][osrx]))])
            fh.write(txtrow + "\n")
    print 
    print "Optimal stand management (rx, offset) written to " + filename
    print

def star_schedule(args):
    """
    The target function for pool.map() can only take one argument
    so we make that one argument a tuple of args and expand it with
    this wrapper function
    """
    from scheduler import schedule
    return schedule(*args)


