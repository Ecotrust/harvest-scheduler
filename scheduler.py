# encoding: utf-8
import random
import numpy as np
import math


def schedule(
        data,
        strategies,
        weights,
        variable_names,
        adjacency,
        valid_rxs,
        temp_min=0.01,
        temp_max=1000,
        steps=50000,
        report_interval=1000):

    num_stands, num_rxs, num_periods, num_variables = data.shape

    stand_range = np.arange(num_stands).tolist()

    assert len(strategies) == num_variables
    assert len(weights) == num_variables
    assert len(variable_names) == num_variables
    assert len(adjacency) == num_stands
    assert len(valid_rxs) == num_stands

    # initial rx
    rxs = [random.randrange(num_rxs) for x in range(num_stands)]
    # make sure each stand's rx starts with a valid rx
    for s, rx in enumerate(rxs):
        if valid_rxs[s]:
            rxs[s] = valid_rxs[s][0]

    best_metric = float('inf')
    best_rxs = rxs[:]
    best_metrics = []
    prev_metric = float('inf')
    prev_rxs = rxs[:]

    accepts = 0
    improves = 0
    temp_factor = -math.log(temp_max / temp_min)

    theoretical_maxes = [0 for x in range(num_variables)]
    for s, strategy in enumerate(strategies):
        # select the variable, sum to across time periods, take the max for each stand and add them
        theoretical_maxes[s] = data[:, :, :, s].sum(axis=2).max(axis=1).sum()

    for step in range(steps):

        # determine temperature
        temp = temp_max * math.exp(temp_factor * step / steps)

        def move():
            '''
            pick a random stand and apply a random rx to it
            '''
            this_stand = random.randrange(num_stands)

            if valid_rxs[this_stand]:
                # this stand has restricted rxs, pick from the select list
                this_rx = random.choice(valid_rxs[this_stand])
            else:
                # pick anything
                this_rx = random.randrange(num_rxs)

            if adjacency[this_stand]:
                # Check for adjacenct harvests and do ... what exactly?
                # The original scheduler was ineffective at answering this question
                pass

            return this_stand, this_rx

        new_stand, new_rx = move()
        rxs[new_stand] = new_rx

        # use numpy indexing to select only the desired rx of each stand
        # effectively collapses array on rxs axis to a 3D array (stands x periods x variables)
        def select():
            # selected = data[stand_range, rxs]
            import ipdb; ipdb.set_trace()
            return data[stand_range, rxs]

        selected = select()

        # calculate the objective metric

        # 2D array
        # stands x sum of each variable over time
        # cumulative_by_stand = selected.sum(axis=1)

        # 2D array
        # time periods x sum of each variable over all stands
        cumulative_by_time_period = selected.sum(axis=0)

        # 1D array
        # useful for cumulative maximize/target
        # property-level cumulative sum of each variable
        property_cumulative = cumulative_by_time_period.sum(axis=0)

        # 1D array
        # useful for evenflow
        # property-level standard deviation of each variable over time
        property_stddevs = cumulative_by_time_period.std(axis=0)

        def calculate_objective_metrics():
            metrics = []
            for s, strategy in enumerate(strategies):
                if strategy == 'cumulative_maximize':
                    # compare the value to the theoretical maximum
                    metrics.append((theoretical_maxes[s] - property_cumulative[s]) * weights[s])
                elif strategy == 'evenflow':
                    # minimize the standard deviation
                    metrics.append(property_stddevs[s] * weights[s])
                elif strategy == 'cumulative_cost':
                    # just take cumulative cost
                    metrics.append(property_cumulative[s] * weights[s])
            return metrics

        objective_metrics = calculate_objective_metrics()
        objective_metric = sum(objective_metrics)

        accept = False
        improve = False

        delta = objective_metric - prev_metric

        rand = np.random.uniform()
        if delta < 0.0:  # an improvement
            accept = True
            improve = True
        elif math.exp(-delta/temp) > rand:  # within temperature, accept it
            accept = True
            improve = False


        if (step+1) % report_interval == 0 and step > 0:
            print "step: %-7d accepts: %-5d improves: %-5d best_metric:   %-6.2f    temp: %-1.2f" % (
                step+1, accepts, improves, best_metric, temp)
            print "   weighted best: ", zip(variable_names, best_metrics)
            print " unweighted best: ", zip(variable_names, [a / b for a, b in zip(best_metrics, weights)])
            print
            improves = 0
            accepts = 0

        if improve:
            improves += 1

        if accept:
            prev_rxs = rxs[:]  # record new rx
            prev_metric = objective_metric
            accepts += 1
        else:
            rxs = prev_rxs[:]  # restore previous rxs

        if objective_metric < best_metric:
            best_rxs = rxs[:]
            best_metric = objective_metric
            best_metrics = objective_metrics

    return best_metric, best_rxs
