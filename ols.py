import numpy as np
import statsmodels.api as sm
import sys
import itertools
import math
import read_data

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True

#################################################

x, y = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single)

def ols(x, y, ind, dep):
    # perform linear regression
    X = x[:, ind]
    X = sm.add_constant(X) # add constant term
    Y = y[:, dep]
    model = sm.OLS(Y, X).fit()

    print("OLS performed successfully")

    # return table of stats
    return model.summary()

def iterative_ols(x, y, mandatory_ind, optional_ind, deps):
    combos = all_combos(optional_ind)
    print(combos)
    summaries = []
    for iteration in combos:
        for dep in deps:
            metrics = mandatory_ind + list(iteration)
            summaries.append(ols(x, y, metrics, [dep]))
    return summaries

def all_combos(lst):
    length = len(lst)
    result = []
    for i in range(1, length+1):
        result += itertools.combinations(optional_ind, i)
    return result

print("Running OLS...")
mandatory_ind = [0,1,2]
optional_ind = [3, 4]
# selected_dep MUST be one element
selected_dep = [0, 1]
# print(ols(x, y, selected_ind, selected_dep))
results = iterative_ols(x, y, mandatory_ind, optional_ind, selected_dep)
for summary in results:
    print(summary)

# if we eventually want predictions
# predictions = model.predict(data_df)
