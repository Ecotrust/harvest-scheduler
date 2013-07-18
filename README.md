harvest-scheduler
=================

Simulated annealing for optimizing timber harvest schedule


# Overview

Determine the best timber stand management strategies over time to 
optimize for multiple property-level objectives. 

For example, the harvest scheduler can answer questions such as 

> What is the best combination of management prescriptions and temporal offsets
> in order to maximize both carbon sequestration AND timber revenue at the lowest 
> cost.

# Details

The input data for the harvest scheduler is a 4D Array.

> Variable of Interest  X  Stands  X  Rx  X  Time Period 

It is easier to visualize this 
as multiple 3D arrays, one of each variable of interest.

![ScreenShot](https://raw.github.com/Ecotrust/harvest-scheduler/master/img/4DArray.png)

The scheduler will

1. Select a random management for each stand 
2. Assess the performance of that state by calculating an objective metric - a single number which
   we are attempting to minimize. 
3. Change the management of a single stand randomly and reassess the objective metric. 
4. Decide whether to accept or reject the change based on the simulated annealing algorithm. Goto step 3 and repeat. 


![ScreenShot](https://raw.github.com/Ecotrust/harvest-scheduler/master/img/ObjectiveMetric.png)

### Objective Metric

The calculation of the objective metric involves looking at each variable, for each stand over time (a 3D array) 
and distilling it down to a single number. In order to do this, each variable can 
be handled according to a preset *strategy*

* **Cumulative-Maximize**: Attempt to maximize the cumulative property-level sum of the variable over time. 
* **Cumulative-Minimize**: Attempt to minimize the cumulative property-level sum over time. 
* **Evenflow**: Attempt to minimize the cumulative property-level standard deviation over time.



