from scheduler import schedule
import numpy as np

if __name__ == '__main__':

    stand_data = np.array([  # list of stands
        [  # list of stand STATES
            [  # list of stand state time periods
                [12, 6, 5],  # <-- list of stand state time period variables
                [12, 0, 6],
                [3, 7, 4],
            ],
            [
                [11, 2, 2],
                [2, 1, 6],
                [10, 9, 3],
            ],
        ],
        [  # stand 2
            [  # state 1
                [12, 6, 5],  # time period 1
                [1, 0, 6],
                [1, 7, 4],
            ],
            [  # state 2
                [11, 2, 2],
                [3, 1, 6],
                [9, 9, 3],
            ],
        ],
    ])

    # pick a strategy for each stand state time period variable
    strategies = ['cumulative_maximize', 'flow_target', 'cumulative_cost']
    """
    cumulative_maximize : target the absolute highest cumulative value

    flow_maximize        : minimize variance WHILE targeting highest cumulative
    flow_target          : minimize variance WHILE targeting user-specified cumulative

    cumulative_cost     : treated as cost; sum over all time periods
    """

    # todo .. flow must specify weight of missed target vs 
    targets = [
        None,       # maximized variables don't have target; target is calculated
        [5, 5, 5],  # flow_target is an array same length as time period
        None        # maximize and costs variables don't need an explicit target
    ]

    weights = [1, 2, 1]

    adjacency = []  # need to define which variable is considered ("harvest")
     # and when state is changed, check the adjacent stands for each time period
     # penalize/avoid if they have overlapping harvests.

    mandatory_states = []  # when changing state, make sure these don't get altered

    optimal_stand_states = schedule(stand_data, strategies,
                                    targets, weights, adjacency)

    print optimal_stand_states
