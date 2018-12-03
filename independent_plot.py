import numpy as np
import statsmodels.api as sm
import sys
import itertools
import math
import read_data
import write_data
import pickle
import metrics
import matplotlib.pyplot as plt

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True

#################################################

x, y = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single)

for i in range(len(metrics.Customer.metric_names(allow_single))):
    
    matplotlib