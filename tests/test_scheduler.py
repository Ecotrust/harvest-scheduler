"""
Tests for `harvestscheduler` module.
"""
import pytest
from harvestscheduler import schedule, prep_data


# Create a random 4D array
# stands, mgmts, timeperiods, numvars
STAND_DATA, AXIS_MAP, VALID_MGMTS = prep_data.from_random(100, 25, 20, 3)

def test_schedule_random():
    axis_map = AXIS_MAP.copy()	

    axis_map['variables'] = [  
        {   
            'name': 'timber',
            'strategy': 'within_bounds',  # Stay within range
            'targets': (
            	[45.0] * 20, # 1 x time periods array of lower bounds
            	[55.0] * 20  # 1 x time periods array of upper bounds
            ),
            'weight': 1.0
        },
        {   
            'name': 'carbon',
            'strategy': 'cumulative_maximize', # target the max cumulative value
            'weight': 1.0
        },
        {   
            'name': 'cost proxy',
            'strategy': 'cumulative_minimize', # target the min cumulative value
            'weight': 1.0
        },
    ]  

    best, optimal_stand_rxs, vars_over_time = schedule(
        STAND_DATA,
        axis_map,
        VALID_MGMTS,
        steps=15000,
        report_interval=5000,
        temp_min=0.006,
        temp_max=20   
    )

    # stochastic process, just make sure it's in the ballpark
    assert 5000 < best and 6000 > best

