import statsmodels.api as sm
import ols
import read_data
import write_data
import numpy as np

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2014", "1/1/2014", "1/1/2019"
allow_single = True
amortized = True

#################################################

x, y, end_time_ind, allow_single, amortized \
    = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single, amortized)

# K Folds - returns accuracy of the model
def accuracy(actual, predicted):
    accurate = 0
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            accurate += 1
    return accurate / len(actual)

def kfolds(regression_results, x_indices, y_index, k):
    new_x = np.zeros(len(x))
    for x_index in x_indices:
        new_x = np.concatenate(new_x, x[:, x_index], axis=1)
    new_y = y[:, y_index]
    fold_size = len(x) // k
    accuracy_sum = 0
    for i in range(k):
        k_x = new_x[(i * fold_size):((i + 1) * fold_size)]
        k_x = new_y[(i * fold_size):((i + 1) * fold_size)]
        rest_x = np.vstack([new_x[0:(i * fold_size)], new_x[((i + 1) * fold_size):len(new_x)]])
        rest_x = np.vstack([new_y[0:(i * fold_size)], new_y[((i + 1) * fold_size):len(new_y)]])
        k_x = sm.add_constant(k_x)
        accuracy_sum += accuracy(k_y, sm.OLS(rest_y, rest_x).fit().fitted_values())
    return accuracy_sum / k

# AIC - returns a score that measures goodness of fit and "simplicity," lower values are better
def aic(regression_results):
    return regression_results.aic()