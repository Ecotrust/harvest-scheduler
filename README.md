harvest-scheduler
=================

Python/Numpy-based simulated annealing for optimizing timber land management.


# Overview

Determine the best timber stand management strategies over time to 
optimize for multiple property-level objectives. 

For example, the harvest scheduler can answer questions such as 

> What is the best combination of management prescriptions and temporal offsets
> in order to maximize both carbon sequestration AND timber revenue at the lowest 
> cost?

# Details

The input data for the harvest scheduler is a 4D Array.

`Variable of Interest`  X  `Stands`  X  `Rx`  X  `Time Period` 

It is easier to visualize this 
as multiple 3D arrays, one for each variable of interest.

![ScreenShot](https://raw.github.com/Ecotrust/harvest-scheduler/master/img/4Darray.png)

The scheduler will

1. Select a random management for each stand 
2. Assess the performance of that state by calculating an objective metric - a single number which
   we attempt to minimize. 
3. Randomly change the management of a single stand and reassess the objective metric. 
4. Decide whether to accept or reject the change based on the simulated annealing algorithm. Goto step 3 and repeat. 

![ScreenShot](https://raw.github.com/Ecotrust/harvest-scheduler/master/img/ObjectiveMetric.png)

### Objective Metric

The calculation of the objective metric involves looking at each variable, for each stand over time (a 3D array) 
and distilling it down to a single number. In order to do this, each variable can 
be handled according to a preset *strategy*

* **cumulative-maximize**: Attempt to maximize the cumulative property-level sum of the variable over time. 
* **cumulative-minimize**: Attempt to minimize the cumulative property-level sum over time. 
* **evenflow**: Attempt to minimize the cumulative property-level standard deviation over time.
* **evenflow-target**: Attempt to minimize the variation over time around a set target. Target can be scalar or array of values over time.

# Usage

### Data Prep

See `scheduler/prep_data.py` for details.

This module contains a function `prep_data.from_shp_csv` which takes two arguments:
1. Path to a shapefile containing stand polygons. Required attributes, projection, etc. are all defined by the `prep_data.py` module. 
This will eventually be specified/documented but for now, just read the code *carefully* for the specs.
2. Path to the *directory* containing the csvs output from the FVS batch growth-yield process. 

The data from the shapfile and csvs will be combined to form the data structures expected 
by the scheduler.

The data will be cached to disk to avoid recalculating expensive datasets. Remove the 
`cache.*` files in order to force a recalculation.

### Using the scheduler

See `test_scheduler.py` for an example of usage of the scheduler interface. 



