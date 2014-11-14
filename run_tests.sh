#!/bin/bash
coverage run --source=harvestscheduler setup.py test && coverage report -m
