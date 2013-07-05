from scheduler import schedule
import prep_data

if __name__ == '__main__':
    # 4D: stands, rxs, time periods, variables
    stand_data = prep_data.from_files()

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
    adjacency[4] = (3, 2, 4)  # avoid cutting stand 4 when 1,2,3 have harvests?

    # restrict valid rxs for certain stands
    valid_rxs = [None for x in range(stand_data.shape[0])]
    valid_rxs[0] = (0, 1, 2)
    valid_rxs[1] = (0, 1, 2)
    valid_rxs[2] = (0, 1, 2)

    optimal_stand_rxs = schedule(
        stand_data,
        strategies,
        weights,
        variable_names,
        adjacency,
        valid_rxs,
        temp_min=0.10,
        temp_max=300.0,
        steps=20000,
        report_interval=1000
    )

    print optimal_stand_rxs
