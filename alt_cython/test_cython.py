from scheduler import schedule
import numpy as np

if __name__ == '__main__':

    """
    stand_data = np.array([  # list of stands
        [  # list of stand STATES
            [  # list of stand rx time periods
                [12, 6, 5],  # <-- list of stand rx time period variables
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
            [  # rx 1
                [12, 6, 5],  # time period 1
                [1, 0, 6],
                [1, 7, 4],
            ],
            [  # rx 2
                [11, 2, 2],
                [3, 1, 6],
                [9, 9, 3],
            ],
        ],
    ])
    """

    # consistently generate a random set
    np.random.seed(42)
    # 4D: stands, rxs, time periods, variables
    stand_data = np.random.randint(10, size=(37,25,20,3))
    stand_data = stand_data.astype(float)

    # pick a strategy for each stand rx time period variable
    # cumulative_maximize : target the absolute highest cumulative value
    # evenflow            : minimize variance around a target
    # cumulative_cost     : treated as cost; sum over all time periods
    strategies = ['cumulative_maximize', 'evenflow', 'cumulative_cost']
    variable_names = ['carbon', 'harvest', 'cost']
    weights = [5.0, 100.0, 0.2]

    # TODO need to define which variable is considered ("harvest")
    # and when rx is changed, check the adjacent stands for each time period
    # penalize/avoid if they have overlapping harvests.
    adjacency = [None for x in range(stand_data.shape[0])]
    adjacency[4] = (3,2,4) # avoid cutting stand 4 when 1,2,3 have harvests?

    # restrict valid rxs for certain stands
    valid_rxs = [None for x in range(stand_data.shape[0])]
    valid_rxs[0] = (0,1,2)  
    valid_rxs[1] = (0,1,2)  
    valid_rxs[2] = (0,1,2)  

    optimal_stand_rxs = schedule(
        stand_data,
        strategies,
        weights,
        variable_names,
        adjacency,
        valid_rxs,
        temp_min=0.01,
        temp_max=2000.0,
        steps=500000,
        report_interval=1000
    )

    print optimal_stand_rxs
