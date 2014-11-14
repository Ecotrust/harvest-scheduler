=============================
Harvest Scheduler
=============================

Optimization for multi-objective timber harvest scheduling and forest resource mangement

Overview
--------

The harvest scheduler allows you find a set of management options (prescriptions)
for each spatial unit (stands) on your property that best meet multiple property-level objectives.

For example, the harvest scheduler answers questions such as 

	What is the best combination of prescriptions across the landscape 
	in order to hit timber volume targets while maximizing carbon storage 
	and minimizing operating costs?


Installation
------------

You can install directly from the master branch::
  
    pip install https://github.com/Ecotrust/harvest-scheduler/zipball/master

Or get the source code and install from there::
  
    git clone https://github.com/Ecotrust/harvest-scheduler
    cd harvest-scheduler
    python setup.py develop


Using the Harvest Scheduler
----------------------------

The following is a quick overview. For more details, please check out the examples.

1. **Simulate Forest Growth and Yield** - for each stand and prescription, you'll
need to have a dataset describing how each of your objectives will change over time.

2. **Load data** - your script must load the data into a python numpy array with 4 dimensions
representing your stands, prescriptions, variables and time periods.

3. **Configure** - your script should identify the weighting and optimization strategy
for each of your objectives. 

4. **Run** - running your scheduler script, once properly configured, will give you 
the results of the most optimal configuration: a list of stands and 
their management prescription. 

