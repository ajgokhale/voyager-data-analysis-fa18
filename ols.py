import numpy as np
import statsmodels.api as sm
import sys
import itertools
import math
import read_data
import write_data
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from   scipy.stats import pearsonr

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True
amortized = True

#################################################

x, y, end_time_ind, allow_single, amortized \
    = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single, amortized)

def valid_model(model):
    summary = model.summary()
    #if len(model.pvalues) >= 6: return True
    if '[2]' in str(summary): return False
    if len(model.pvalues) == 1: return False
    for i in range(0, len(model.pvalues)):
        if model.pvalues[i] > 0.2: return False
    #if '[2]' not in str(summary): return False # FOR TESTING
    return True

def ols(x, y, ind, dep):
    # perform linear regression
    X = x[:, ind]
    X = sm.add_constant(X) # add constant term
    Y = y[:, dep]
    model = sm.OLS(Y, X).fit()

    print("OLS performed successfully")

    # return table of stats
    return model

def iterative_ols(x, y, mandatory_ind, optional_ind, deps):
    combos = all_combos(optional_ind)
    print(combos)
    summaries = []
    model_results = []
    for iteration in combos:
        for dep in deps:
            metrics = mandatory_ind + list(iteration)
            model = ols(x, y, metrics, [dep])
            if valid_model(model):
                model_results.append((model, metrics, model.rsquared))
    model_results.sort(key=lambda x: -x[2])
    for model in model_results:
        metrics = model[1]
        model = model[0]
        summaries.append(str(metrics) + "\n"+ str(model.summary()) +"\n\n\n")
    return summaries

def all_combos(lst):
    length = len(lst)
    result = []
    for i in range(4, length+1):
        result += itertools.combinations(optional_ind, i)
    result.append(tuple())
    return result

def calculate_pvalues(df):
    df = df.dropna()._get_numeric_data()
    dfcols = pd.DataFrame(columns=df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    for r in df.columns:
        for c in df.columns:
            pvalues[r][c] = round(pearsonr(df[r], df[c])[1], 4)
    return pvalues

x_df = pd.DataFrame(data=x)
matrix = x_df.corr()
pvalues = calculate_pvalues(x_df)

print("Printing correlation matrix...")
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(matrix)
    print(pvalues)
    print(np.linalg.eig(matrix)[0])
input("Continue?")

print("Running OLS...")
mandatory_ind = []
optional_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,]# 5, 6, 7,]
if not allow_single: optional_ind.extend([10, 11, 12, ])

selected_dep = [0]
results = iterative_ols(x, y, mandatory_ind, optional_ind, selected_dep)

name = end_time_ind.split("/")[2]
if allow_single: name += "-single"
if amortized: name += "-amortized"
curr_time = str(datetime.datetime.now().time())
curr_time = curr_time.split(".")[0]
curr_time = curr_time.replace(":", "-")
name += '-' + curr_time
write_data.save_ols_results(results, name)

# if we eventually want predictions
# predictions = model.predict(data_df)
