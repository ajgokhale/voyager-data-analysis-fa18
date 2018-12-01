import numpy as np
import pandas as pd
import statsmodels.api as sm
import metrics
import sys

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

# IMPORTANT: values for regression's start and end times (format: ___________)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = "1/1/2005", "12/31/2018", "1/1/2005", "12/31/2018"

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
    if obj.summary != None: customer_list.append(obj)
    i += 1
    # FOR TESTING
    #if i > 10:
    #    break

print(i, " customer objects successfully constructed and instantiated")

# creates a 2D array of independent variable values for all customers
independent_variables = [customer.summary for customer in customer_list]
x = np.asarray(independent_variables)

# creates a 1D array of dependent variable values for all customers
dependent_variable = [customer.response for customer in customer_list]
y = np.asarray(dependent_variable)

# JAKE: Horizontally concatenate x and y


print("Running OLS...")
print()
