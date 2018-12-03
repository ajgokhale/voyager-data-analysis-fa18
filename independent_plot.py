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

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2012", "1/1/2012", "1/1/2019"
allow_single = False

#################################################

x, y = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single)

for i in range(len(metrics.Customer.metric_names(allow_single)) - 2):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x[:, i], y[:, 0], c = 'green', s = 50)
    ax.set_xlabel(metrics.Customer.metric_names(allow_single)[i])
    ax.set_ylabel("Total Revenue")
    ax.set_title("Plot of " + metrics.Customer.metric_names(allow_single)[i] + " and Total Revenue")
    figi = plt.gcf()
    name = "Column" + str(i) + "andTotalRevenue"
    figi.savefig("output/scatters/"+name+".png", format='png')
