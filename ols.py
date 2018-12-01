import numpy as np
import pandas as pd
import statsmodels.api as sm
import metrics
import sys
import itertools
import math

# read in data as Pandas DataFrames
sales = pd.read_csv('../data/salescsv.csv')
services = pd.read_csv('../data/servicescsv.csv')
survey = pd.read_csv('../data/surveycsv.csv')

# remove any duplicate data in each of the data sets
sales.drop_duplicates(subset=['customer_id','household_id','model_year', 'model_type', 'msrp', 'trans_type', 'contract_type'])
services.drop_duplicates(subset=['customer_id','household_id','amount_paid', 'amount_warranty', 'model_year', 'model_type'])
survey.drop_duplicates(subset=['customer_id','household_id','ltr','model_year','model_class','model_type'])

# make a new data frame for each customer within each data set and store in a list (with respect to each data set)
sales_customers = [customer for _, customer in sales.groupby(sales['customer_id'])] # 5000 unique customers
services_customers = [customer for _, customer in services.groupby(services['customer_id'])] # 4307 unique customers
survey_customers = [customer for _, customer in survey.groupby(survey['customer_id'])] # 1528 unique customers

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"

print("Data read in and parsed without a hitch")

# helper method to see if a list of customer data frames contains a particular customer
def contains_customer(lst, customer_id):
    for customer in lst:
        if customer_id == customer['customer_id'].values[0]:
            return customer
    return None
i = 0
# creates a list of customer objects
customer_list = []
for customer in sales_customers:
    sales_history = customer
    services_history = contains_customer(services_customers, customer['customer_id'].values[0])
    survey_history = contains_customer(survey_customers, customer['customer_id'].values[0])
    obj = metrics.Customer(sales_history, services_history, survey_history, start_time_ind, end_time_ind, start_time_dep, end_time_dep)
    # FOR TESTING
    # print(obj.summary)
    if obj.summary != None: customer_list.append(obj)
    i += 1
    # FOR TESTING
    #if i > 10:
    #    break

print(i, " customer objects successfully constructed and instantiated")

# creates a 2D array of independent variable values for all customers
independent_variables = []
dependent_variables = []
for customer in customer_list:
    valid = True
    for element in customer.summary:
        if math.isnan(element) or math.isinf(element):
            valid = False
    for element in customer.response:
        if math.isnan(element) or math.isinf(element):
            valid = False
    if valid:
        independent_variables.append(customer.summary)
        dependent_variables.append(customer.response)
    else:
        print(customer.summary)
#independent_variables = [customer.summary for customer in customer_list if float('nan') not in customer.summary]
x = np.asarray(independent_variables)

# creates a 1D array of dependent variable values for all customers
y = np.asarray(dependent_variables)

print(x)

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
