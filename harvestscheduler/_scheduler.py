# encoding: utf-8
from __future__ import absolute_import
import random
import numpy as np
import math
import json


def schedule(
        data,
        axis_map,
        valid_mgmts,
        temp_min=None,
        temp_max=None,
        steps=20000,
        report_interval=1000,
        logfile=None,
        adjacency=False,
        starting_mgmts=None,
        live_plot=False):

    if live_plot:
        import redis
        rc = redis.Redis()

    if temp_min is None:
        temp_min=sum([x['weight'] for x in axis_map['variables']])/1000.0

    if temp_max is None:
        temp_max=sum([x['weight'] for x in axis_map['variables']])*10    

    num_stands, num_mgmts, num_periods, num_variables = data.shape

    stand_range = np.arange(num_stands).tolist()

    strategies = [x['strategy'] for x in axis_map['variables']]
    weights = [x['weight'] for x in axis_map['variables']]
    variable_names = [x['name'] for x in axis_map['variables']]
    strategy_variables = [x.get("targets", None) for x in axis_map['variables']]

    assert len(strategies) == num_variables
    assert len(weights) == num_variables
    assert len(variable_names) == num_variables
    assert len(valid_mgmts) == num_stands

    # initial mgmt
    if starting_mgmts:
        mgmts = starting_mgmts[:]
    else:
        mgmts = [random.randrange(num_mgmts) for x in range(num_stands)]

    # make sure each stand's mgmt starts with a valid mgmt
    for s, mgmt in enumerate(mgmts):
        if valid_mgmts[s]:
            mgmts[s] = valid_mgmts[s][0]

    # use numpy indexing to select only the desired mgmt of each stand and collapse accross stands
    vars_over_time = data[stand_range, mgmts].sum(axis=0)
    prev_vars_over_time = vars_over_time.copy()

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
        print(' '.join(variable_names[s], theoretical_mins[s], "to", theoretical_maxes[s]))
    print('')

    enum_strategies = list(enumerate(strategies))

    # property-level targets over time for evenflow_target variables
    targets = []
    uppers = [] 
    lowers = []
    for s, strategy in enum_strategies:
        if strategy == 'evenflow_target':
            target_per_period = strategy_variables[s]
            try:
                assert len(target_per_period) == num_periods
                # it's a list
                targets.append(np.array(target_per_period))
            except TypeError:
                # it's a scalar
                targets.append(np.array([target_per_period] * num_periods))

        if strategy == 'within_bounds':
            lower, upper = strategy_variables[s]
            try:
                assert len(upper) == len(lower) == num_periods
                # it's a list
                uppers.append(np.array(upper))
                lowers.append(np.array(lower))
            except (TypeError, AssertionError):
                # it's a scalar?
                uppers.append(np.array([upper] * num_periods))
                lowers.append(np.array([lower] * num_periods))

        else:
            uppers.append(None)
            lowers.append(None)
            targets.append(None)

    fh = None
    if logfile:
        fh = open(logfile, 'w')

    if live_plot:
        from harvestscheduler.plot import AnalogPlot
        analog_plot = AnalogPlot(steps)
        plot_cache = []

    select_sum_time = 0
    fsteps = float(steps)

    for step in range(steps):

        # determine temperature
        temp = temp_max * math.exp(temp_factor * step / fsteps)

        actual_change = False
        while not actual_change:
            new_stand = random.randrange(num_stands)
            old_mgmt = mgmts[new_stand]

            if valid_mgmts[new_stand]:
                # new stand has restricted mgmts, pick from the select list
                new_mgmt = random.choice(valid_mgmts[new_stand])
            else:
                # pick anything
                new_mgmt = random.randrange(num_mgmts)

            if old_mgmt != new_mgmt:
                actual_change = True

        mgmts[new_stand] = new_mgmt

        # determine if adjacent stands constitue clumps of harvesting that
        # might exceed regulatory limits
        adjacency_penalty = 0
        # TODO 
        # adj_stands = adjacency[new_stand]
        # harvest = selected[:, :, 1]
        # harvest_clump = harvest[([new_stand] + adj_stands)].sum(axis=0)
        # # TODO - don't hardcode
        # MAX_HARVEST_CLUMP = 75
        # if harvest_clump.max() > MAX_HARVEST_CLUMP:
        #     adjacency_penalty = 1000

        # Calculate the diff to vars_over_time due to the change in mgmt
        olddata = data[new_stand, old_mgmt]
        newdata = data[new_stand, new_mgmt]
        diff = newdata - olddata

        # 2D array
        # time periods x sum of each variable over all stands
        # apply diff 
        vars_over_time += diff

        # 1D array
        # useful for cumulative maximize/target
        # property-level cumulative sum of each variable
        property_cumulative = vars_over_time.sum(axis=0)

        objective_metrics = []

        for s, strategy in enum_strategies:
            # note that all cumulative metrics return some value that is effectively scaled 0-100

            if theoretical_mins[s] == theoretical_maxes[s]:
                #if there's no variation, don't even bother
                objective_metrics.append(0)

            elif strategy == 'cumulative_maximize':
                # compare the value to the theoretical maximum
                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                cumval = property_cumulative[s]
                objective_metrics.append(100*((maxval - cumval) / float(maxval - minval)) * weights[s])

            elif strategy == 'evenflow':
                values = vars_over_time[:, s]
                # property-level variance of THIS variable over time
                property_variance = values.var(axis=0)

                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                range_by_period = (maxval - minval) / float(num_periods)

                # TODO make evenflow return a number scaled 0-100
                objective_metrics.append(property_variance / range_by_period * weights[s] * 100)

            elif strategy == 'within_bounds':
                values = vars_over_time[:, s]
                periods = values.shape[0]
                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                refval = ((maxval-minval)/periods)

                below = lowers[s] - values
                below = below[below > 0] # positive values are below the min

                above = values - uppers[s]
                above = above[above > 0] # positive values are above the max

                outofbounds = below.sum() + above.sum()
                objective_metrics.append((outofbounds / refval) * 100 * weights[s])
                
            elif strategy == 'evenflow_target':
                values = vars_over_time[:, s]

                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                range_by_period = (maxval - minval) / float(num_periods)

                diffs = values - targets[s]
                # absolute val but 10x penalty for going *below* target
                diffs[diffs < 0] *= -10
                # diffs = np.absolute(values - targets[s])

                scaled_sum_diffs = 100 * ((diffs / (range_by_period/2.0))).mean()
                objective_metrics.append(scaled_sum_diffs * weights[s])

            elif strategy == 'cumulative_minimize':
                # compare the value to the theoretical minimum
                maxval = theoretical_maxes[s]
                minval = theoretical_mins[s]
                cumval = property_cumulative[s]
                objective_metrics.append(100*((cumval - minval) / float(maxval - minval)) * weights[s])

            else:
                raise Exception("Unknown optimization strategy `%s`" % strategy)

        objective_metric = sum(objective_metrics) + adjacency_penalty

        accept = False
        improve = False
        new_best = False

        delta = objective_metric - prev_metric

        rand = np.random.uniform()
        k = 1
        if delta < 0.0:  # an improvement
            accept = True
            improve = True
        elif math.exp(-(k*delta)/temp) > rand:  # within temperature, accept it
            accept = True
            improve = False

        if (step+1) % report_interval == 0 and step > 0:
            reported_steps = float(step - last_reported_step)
            print("step: %-7d  accepted %0.2f %%   improved %0.2f %%   best_metric:   %-6.2f    temp: %-1.4f" % (
                step+1, 100*accepts/reported_steps, 100*improves/reported_steps, best_metric, temp))
            print("  weighted best: ", ",  ".join(["%s: %.2f" % x
                                                   for x in zip(variable_names, best_metrics)]))
            print("unweighted best: ", ",  ".join(["%s: %.2f" % x
                                                   for x in zip(variable_names,
                                                                [a / b for a, b in zip(best_metrics, weights)])]))
            print()
            if live_plot:
                rc.publish("test_channel", 
                    json.dumps({'plot_cache': plot_cache})
                )
                analog_plot.append(plot_cache)
                plot_cache = []
            improves = 0
            accepts = 0
            last_reported_step = step

        if improve:
            improves += 1

        if accept:
            prev_mgmts = mgmts[:]  # record new mgmts
            prev_vars_over_time = vars_over_time.copy()
            prev_metric = objective_metric
            accepts += 1
        else:
            mgmts = prev_mgmts[:]  # restore previous mgmts
            vars_over_time = prev_vars_over_time.copy()

        if objective_metric < best_metric:
            best_mgmts = mgmts[:]
            best_metric = objective_metric
            best_metrics = objective_metrics
            best_vars_over_time = vars_over_time[:]
            new_best = True

        if live_plot:
            if not accept:
                stype = "reject"
            elif accept and not improve:
                stype = "accept"
            elif accept and improve and not new_best:
                stype = "acceptimprove"
            elif new_best:
                stype = "newbest"  
            
            plot_cache.append((objective_metric, step, stype, best_metric))
            

        if logfile and fh:
            if not accept:
                stype = "reject"
            elif accept and not improve:
                stype = "accept"
            elif accept and improve and not new_best:
                stype = "accept+improve"
            elif new_best:
                stype = "new best"

            fh.write(','.join(str(x) for x in [step, objective_metric, stype, temp]))
            fh.write("\n")

    print("Select sum time: " + select_sum_time)

    if fh:
        fh.close()
    return best_metric, best_mgmts, best_vars_over_time

