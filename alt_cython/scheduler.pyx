from libc cimport math
import random
cimport numpy as np
import numpy as np
cimport cython
ctypedef np.float_t DTYPE_t

cdef extern from "math.h":
    double exp(double x)


@cython.boundscheck(False)
def schedule(np.ndarray[DTYPE_t, ndim=4] data not None, strategies, targets, weights, adjacency):
    cdef int num_stands = data.shape[0]
    cdef int num_states = data.shape[1]
    cdef int num_periods = data.shape[2]
    cdef int num_variables = data.shape[3]

    stand_range = np.arange(num_stands)

    assert len(strategies) == num_variables
    assert len(targets) == num_variables
    assert len(weights) == num_variables

    # initial state
    states = [random.randrange(num_states) for x in range(num_stands)]

    cdef float best_metric = float('inf')  
    best_states = states[:]
    cdef float prev_metric = float('inf')
    prev_states = states[:]

    cdef float temp_min = .01
    cdef float temp_max = 10.0
    cdef float temp_factor = -math.log( temp_max / temp_min )
    cdef int steps = 10000
    cdef int step
    cdef int report_interval = 1000
    cdef int accepts = 0
    cdef int improves = 0

    cdef float objective_metric
    cdef float delta
    cdef float rand
    cdef float temp

    #cdef np.ndarray[DTYPE_t, ndim=1] random_comparisons = np.random.uniform(size=steps) 
    #cdef np.ndarray[int, ndim=1] random_stands = np.random.random_integers(0,num_stands-1,size=steps)
    #cdef np.ndarray[int, ndim=1] random_states = np.random.random_integers(0,num_states-1,size=steps)

    cdef np.ndarray[DTYPE_t, ndim=1] property_stddevs
    cdef np.ndarray[DTYPE_t, ndim=2] cumulative_by_time_period
    cdef np.ndarray[DTYPE_t, ndim=3] selected

    for step in range(steps):

        # determine temperature
        temp = temp_max * exp(temp_factor * step / steps)

        # pick a random stand and apply a random state to it
        states[random.randrange(num_stands)] = random.randrange(num_states)
        #states[random_stands[step]] = random_states[step]

        # use numpy indexing to select only the desired state of each stand
        # effectively collapses array on states axis to a 3D array (stands x periods x variables)
        selected = data[stand_range, states]

        # calculate the objective metric

        # 2D array
        # stands x sum of each variable over time
        # cumulative_by_stand = selected.sum(axis=1)

        # 1D array
        # useful for cumulative maximize/target
        # property-level cumulative sum of each variable
        # property_cumulative = cumulative_by_stand.sum(axis=0)

        # 2D array
        # time periods x sum of each variable over all stands
        cumulative_by_time_period = selected.sum(axis=0)

        # 1D array
        # useful for evenflow
        # property-level standard deviation of each variable over time
        property_stddevs = cumulative_by_time_period.std(axis=0)

        # TODO just for testing
        objective_metric = property_stddevs[0]

        accept = False
        improve = False
        best = False

        delta = objective_metric - prev_metric

        rand = np.random.uniform()
        #rand = random_comparisons[step]
        if delta < 0.0:  # an improvement
            accept = True
            improve = True
        elif exp(-delta/temp) > rand:  # within temperature, accept it
            accept = True
            improve = False

        if step % report_interval == 0:
            print "step: %6d accepts:  %d improves:  %d metric:  %1.2f temp:  %1.2f" % (step, 
                    accepts, improves, prev_metric, temp)
            improves = 0
            accepts = 0

        if improve:
            improves += 1

        if accept:
            prev_states = states[:]  # record new state
            prev_metric = objective_metric
            accepts += 1
        else:
            states = prev_states[:]  # restore previous states

        if objective_metric < best_metric:
            best = True
            best_states = states[:]
            best_metric = objective_metric

    return best_metric, best_states
