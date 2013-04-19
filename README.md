harvest-scheduler
=================

Simulated annealing for optimizing timber harvest schedules


# Overview

This project aims to take a directory of offset FVS runs and determine the optimal 
time offset or harvest schedule. 

Several steps are encompassed by this process:

1. post-process FVS treelist files into aggregate summaries (python based)
2. feed those aggreate summaries into the simulated annealing routine, outputting the optimal
 offset for each stand (C-based)

Ultimately this tool will be integrated with the `land_owner_tools` and
 `growth-yeild-batch` repositories.
 
# License

Licensing and redistribution rights are unclear at this time. Copyright for `schedule.c` is assumed to
belong to the original author, John Sessions, but the license under which the code was
release was not made explicit. Hence the private repository.