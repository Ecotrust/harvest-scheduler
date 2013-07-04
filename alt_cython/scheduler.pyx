# from libc cimport math
import random
cimport numpy as np
import numpy as np
# cimport cython
# ctypedef np.int_t DTYPE_t


#@cython.boundscheck(False)
def schedule(data, strategies, targets, weights, adjacency):
    num_stands, num_states, num_periods, num_variables = data.shape

    stand_range = np.arange(num_stands)

    assert len(strategies) == num_variables
    assert len(targets) == num_variables
    assert len(weights) == num_variables

    # initial state
    states = [random.randrange(num_states) for x in range(num_stands)]

    for i in range(3):

        # pick a random stand and apply a random state to it
        states[random.randrange(num_stands)] = random.randrange(num_states)

        # use numpy indexing to select only the desired state of each stand
        selected = data[stand_range, states]

        # calculate the objective metric

        # 2D array
        # stands x sum of each variable over time
        cumulative_by_stand = selected.sum(axis=1)
        print "cumulative_by_stand"
        print cumulative_by_stand
        print

        # 1D array
        # useful for cumulative maximize/target
        # property-level cumulative sum of each variable
        property_cumulative = cumulative_by_stand.sum(axis=0)
        print "property_cumulative"
        print property_cumulative
        print

        # 2D array
        # time periods x sum of each variable over all stands
        cumulative_by_time_period = selected.sum(axis=0)
        print "cumulative_by_time_period"
        print cumulative_by_time_period
        print

        # 1D array
        # useful for evenflow
        # property-level standard deviation of each variable over time
        property_stddevs = cumulative_by_time_period.std(axis=0)
        print "property_stddevs"
        print property_stddevs
        print

        # print "-- max"
        # print selected.max(axis=1)
        print "-###############################-"
        print


    return True
