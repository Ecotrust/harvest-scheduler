# encoding: utf-8
import random
import numpy as np
import math


def schedule(
        data,
        strategies,
        weights,
        variable_names,
        valid_mgmts,
        strategy_variables,
        adjacency=None,
        temp_min=0.01,
        temp_max=1000,
        steps=50000,
        report_interval=1000):

    num_stands, num_mgmts, num_periods, num_variables = data.shape

    stand_range = np.arange(num_stands).tolist()

    assert len(strategies) == num_variables
    assert len(weights) == num_variables
    assert len(variable_names) == num_variables
    assert len(valid_mgmts) == num_stands

    # initial mgmt
    mgmts = [random.randrange(num_mgmts) for x in range(num_stands)]
    # make sure each stand's mgmt starts with a valid mgmt
    for s, mgmt in enumerate(mgmts):
        if valid_mgmts[s]:
            mgmts[s] = valid_mgmts[s][0]

    # use numpy indexing to select only the desired mgmt of each stand
    # effectively collapses array on mgmts axis to a 3D array (stands x periods x variables)
    selected = data[stand_range, mgmts].copy()
    prev_selected = selected.copy()

    best_metric = float('inf')
    best_mgmts = mgmts[:]
    best_metrics = []
    prev_metric = float('inf')
    prev_mgmts = mgmts[:]

    accepts = 0
    improves = 0
    last_reported_step = 0
    temp_factor = -math.log(temp_max / temp_min)

    theoretical_maxes = [0 for x in range(num_variables)]
    theoretical_mins = [0 for x in range(num_variables)]
    for s, strategy in enumerate(strategies):
        # select the variable, sum to across time periods, take the max for each stand and add them
        theoretical_maxes[s] = data[:, :, :, s].sum(axis=2).max(axis=1).sum()
        theoretical_mins[s] = data[:, :, :, s].sum(axis=2).min(axis=1).sum()
        print variable_names[s], theoretical_mins[s], "to", theoretical_maxes[s]
    print

    for step in range(steps):

        # determine temperature
        temp = temp_max * math.exp(temp_factor * step / steps)

        new_stand = random.randrange(num_stands)
        old_mgmt = mgmts[new_stand]

        if valid_mgmts[new_stand]:
            # new stand has restricted mgmts, pick from the select list
            new_mgmt = random.choice(valid_mgmts[new_stand])
        else:
            # pick anything
            new_mgmt = random.randrange(num_mgmts)

        if old_mgmt == new_mgmt:
            step -= 1  # this one doesn't count as it wasn't a true change
            continue

        mgmts[new_stand] = new_mgmt

        # modify selected data and replace it out with the new move
        selected[new_stand] = data[new_stand, new_mgmt]

        # 2D array
        # time periods x sum of each variable over all stands
        cumulative_by_time_period = selected.sum(axis=0)

        # 1D array
        # useful for cumulative maximize/target
        # property-level cumulative sum of each variable
        property_cumulative = cumulative_by_time_period.sum(axis=0)

        objective_metrics = []
        for s, strategy in enumerate(strategies):
            # note that all cumulative metrics return some value that is effectively scaled 0-100
            # TODO make evenflow return a number scaled 0-100

            if strategy == 'cumulative_maximize':
                # compare the value to the theoretical maximum
                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                cumval = property_cumulative[s]
                objective_metrics.append(100*((maxval - cumval) / float(maxval - minval)) * weights[s])

            elif strategy == 'evenflow':
                values = cumulative_by_time_period[:, s]
                # property-level standard deviation of THIS variable over time
                property_stddev = values.std(axis=0)
                objective_metrics.append(property_stddev * weights[s])

            elif strategy == 'evenflow_target':
                values = cumulative_by_time_period[:, s]

                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                range_by_period = (maxval - minval) / float(num_periods)

                # property-level targets
                target_per_period = strategy_variables[s]
                targets = np.array([target_per_period] * num_periods)
                abs_diffs = np.absolute(values - targets)

                scaled_sum_diffs = 100 * ((abs_diffs / (range_by_period/2.0))).mean()
                objective_metrics.append(scaled_sum_diffs * weights[s])

            elif strategy == 'cumulative_minimize':
                # compare the value to the theoretical minimum
                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                cumval = property_cumulative[s]
                objective_metrics.append(100*((cumval - minval) / float(maxval - minval)) * weights[s])

            else:
                raise Exception("Unknown optimization strategy `%s`" % strategy)

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
            reported_steps = float(step - last_reported_step)
            print "step: %-7d  accepted %0.2f %%   improved %0.2f %%   best_metric:   %-6.2f    temp: %-1.4f" % (
                step+1, 100*accepts/reported_steps, 100*improves/reported_steps, best_metric, temp)
            print "  weighted best: ", ",  ".join(["%s: %.2f" % x
                                                   for x in zip(variable_names, best_metrics)])
            print "unweighted best: ", ",  ".join(["%s: %.2f" % x
                                                   for x in zip(variable_names,
                                                                [a / b for a, b in zip(best_metrics, weights)])])
            print
            improves = 0
            accepts = 0
            last_reported_step = step

        if improve:
            improves += 1

        if accept:
            prev_mgmts = mgmts[:]  # record new mgmts
            prev_selected = selected.copy()
            prev_metric = objective_metric
            accepts += 1
        else:
            mgmts = prev_mgmts[:]  # restore previous mgmts
            selected = prev_selected.copy()

        if objective_metric < best_metric:
            best_mgmts = mgmts[:]
            best_metric = objective_metric
            best_metrics = objective_metrics
            best_vars_over_time = cumulative_by_time_period.copy()

    return best_metric, best_mgmts, best_vars_over_time
