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
from numpy.polynomial.polynomial import polyfit

################# PARAMETERS ####################

boundary, allow_single, try_combos, exit = \
    read_data.read_command_line()
if exit: sys.exit()

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2008", "1/1/", "1/1/", "1/1/2019"
end_time_ind += boundary
start_time_dep += boundary

amortized = True

print("Analyzing customer behavior from", start_time_ind, "to", end_time_ind)
print("Regressing on customer behavior from", start_time_dep, "to", end_time_dep)
if allow_single: print("Single transaction customers included")
else: print("Single transaction customers not included")
if try_combos: print("Trying all combinations of metrics")
else: print("Trying single combination of metrics")

#################################################

x, y, end_time_ind, allow_single, amortized \
    = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single, amortized)

dependent_map = {0:"Total Revenue",1:"Total Revenue from Sales",
    2:"Total Revenue from Services", 3:"Vehicle Purchase or Lease Indicator"}

plots = []
for dep_index in range(4):
    for i in range(len(metrics.Customer.metric_names(allow_single)) - 4):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.scatter(x[:, i], y[:, dep_index], c = 'green', s = 50,
            alpha=0.045)
        if dep_index != 3:
            b, m = polyfit(x[:, i], y[:, dep_index], 1)
            ax.plot(x[:, i], x[:, i]*m+b, color='black')
        if metrics.Customer.metric_names(allow_single)[i] == "Total Servicing Transactions":
            ax.set_xlim(-0.5, 10.5)
        if metrics.Customer.metric_names(allow_single)[i] == "Maximum Vehicle MSRP":
            ax.set_xlim(right=125000)
        if metrics.Customer.metric_names(allow_single)[i] == "Average Vehicle MSRP":
            ax.set_xlim(right=100000)
        if metrics.Customer.metric_names(allow_single)[i] == "Maximum Servicing Transaction":
            ax.set_xlim(right=4000)
        if metrics.Customer.metric_names(allow_single)[i] == "Average Servicing Transaction":
            ax.set_xlim(right=3000)
        ax.set_xlabel(metrics.Customer.metric_names(allow_single)[i])
        dep_name = dependent_map[dep_index]
        ax.set_ylabel(dep_name)
        #ax.set_title("Plot of " + metrics.Customer.metric_names(allow_single)[i] + " and Total Revenue")
        for item in ([ax.xaxis.label, ax.yaxis.label]):
            item.set_fontsize(17)
            item.set_weight("bold")
            item.set_family('Arial')
        fig.tight_layout()
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
