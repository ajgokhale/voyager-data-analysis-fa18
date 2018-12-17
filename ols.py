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
from statsmodels.stats.outliers_influence import variance_inflation_factor 

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


def calculate_vif_(X, thresh=5.0):
    variables = list(range(X.shape[1]))
    dropped = True
    while dropped:
        dropped = False
        vif = [variance_inflation_factor(X.iloc[:, variables].values, ix)
               for ix in range(X.iloc[:, variables].shape[1])]

        maxloc = vif.index(max(vif))
        if max(vif) > thresh:
            #print('dropping \'' + X.iloc[:, variables].columns[maxloc] +
            #      '\' at index: ' + str(maxloc))
            del variables[maxloc]
            dropped = True
    print('Remaining variables:')
    print(X.columns[variables])
    return X.iloc[:, variables]

x_df = pd.DataFrame(data=x)
calculate_vif_(x_df)
x_df = x_df.iloc[:, [1,3,4,5,7,8,9,11]]

def valid_model(model):
    summary = model.summary()
    #if len(model.pvalues) >= 6: return True
    if '[2]' in str(summary): return False
    if len(model.pvalues) == 1: return False
    #for i in range(0, len(model.pvalues)):
    #    if model.pvalues[i] > 0.2: return False
    #if '[2]' not in str(summary): return False # FOR TESTING
    return True

def ols(x, y, ind, dep):
    # perform linear regression
    X = x[:, ind]
    X = sm.add_constant(X) # add constant term
    Y = y[:, dep]
    model = sm.OLS(Y, X).fit()

    #print("OLS performed successfully")

    # return table of stats
    return model

def iterative_ols(x, y, mandatory_ind, optional_ind, deps,try_combos=True):
    o = open(boundary + ".csv", 'w+')
    if try_combos:
        combos = all_combos(optional_ind)
    else:
        combos = [optional_ind]
    total = len(combos)*len(deps)
    dep_results = []
    i = 0
    for dep in deps:
        summaries = []
        model_results = []
        for iteration in combos:
            i+=1
            metrics = mandatory_ind + list(iteration)
            model = ols(x, y, metrics, [dep])
            if valid_model(model) or not try_combos:
                model_results.append((model, metrics, model.rsquared))
            if i%100==0: print("Ran",i, "/",total,"regressions")
    #model_results.sort(key=lambda x: -x[2])
        model_results.sort(key=lambda x: -len(x[0].pvalues))
        for model in model_results:
            metrics = model[1]
            model = model[0]
            for i in range(len(model.pvalues)):
                o.write(str(model.params[i]) + ",\n")
                o.write(str(model.pvalues[i])+",\n")
            o.write(str(model.rsquared_adj)+",\n")
            summaries.append(str(metrics) + "\n"+ str(model.summary()) +"\n\n\n")
        dep_results.append(summaries)
    return dep_results

def all_combos(lst):
    length = len(lst)
    result = []
    for i in range(1, length+1):
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


matrix = x_df.corr()
pvalues = calculate_pvalues(x_df)

print("Printing correlation matrix...")
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(matrix)
    print(pvalues)
    print(np.linalg.eig(matrix)[0])
input("Continue?")

print("Running OLS...")
mandatory_ind = []#[1,3,4,5,7,8,9]
optional_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10, 11]# 5, 6, 7,]
if not allow_single: optional_ind.extend([12, 13,14 ])

if len(sys.argv) > 5:
    optional_ind = []
    for i in range(5, len(sys.argv)):
        optional_ind.append(int(sys.argv[i]))

selected_dep = [0, 1, 2]
print(mandatory_ind)
print(optional_ind)
print(try_combos)
dep_results = iterative_ols(x, y, mandatory_ind, optional_ind, selected_dep,
    try_combos)

for i in range(len(dep_results)):
    results = dep_results[i]
    name = end_time_ind.split("/")[2]
    if allow_single: name += "-single"
    if amortized: name += "-amortized"
    curr_time = str(datetime.datetime.now().time())
    curr_time = curr_time.split(".")[0]
    curr_time = curr_time.replace(":", "-")
    name += '-' + curr_time
    write_data.save_ols_results(results, str(i)+"-"+name)
