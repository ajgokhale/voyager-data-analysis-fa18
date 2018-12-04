import numpy as np
import statsmodels.api as sm
import sys
import itertools
import math
import read_data
import write_data
import pickle
import matplotlib.pyplot as plt
import metrics
import datetime

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2008", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True
amortized = True

#################################################

x, y, end_time_ind, allow_single, amortized \
    = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single, amortized)

plots = []
for i in range(len(metrics.Customer.metric_names(allow_single)) - 2):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x[:, i], y[:, 0], c = 'green', s = 50,
        alpha=0.1)
    ax.set_xlabel(metrics.Customer.metric_names(allow_single)[i])
    ax.set_ylabel("Total Revenue")
    ax.set_title("Plot of " + metrics.Customer.metric_names(allow_single)[i] + " and Total Revenue")
    figi = plt.gcf()
    plots.append((figi, metrics.Customer.metric_names(allow_single)[i]))

name = end_time_ind.split("/")[2]
if allow_single: name += "-single"
if amortized: name += "-amortized"
curr_time = str(datetime.datetime.now().time())
curr_time = curr_time.split(".")[0]
curr_time = curr_time.replace(":", "-")
name += '-' + curr_time
write_data.save_plots(plots, name)
