import numpy as np
import pandas as pd
import statsmodels.api as sm
import metrics

# read in data as Pandas DataFrames
sales = pd.read_excel('sales.xlsx')
services = pd.read_excel('services.xlsx')
survey = pd.read_excel('survey.xlsx')

# remove any duplicate data in each of the data sets
sales.drop_duplicates(subset=['customer_id','household_id','model_year', 'model_type', 'msrp', 'trans_type', 'contract_type'])
services.drop_duplicates(subset=['customer_id','household_id','amount_paid', 'amount_warranty', 'model_year', 'model_type'])
survey.drop_duplicates(subset=['customer_id','household_id','ltr','model_year','model_class','model_type'])

# make a new data frame for each customer within each data set and store in a list (with respect to each data set)
sales_customers = [customer for _, customer in sales.groupby(sales['customer_id'])] # 5000 unique customers
services_customers = [customer for _, customer in services.groupby(services['customer_id'])] # 4307 unique customers
survey_customers = [customer for _, customer in survey.groupby(survey['customer_id'])] # 1528 unique customers

# IMPORTANT: values for regression's start and end times (format: ___________)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = None, None, None, None

# helper method to see if a list of customer data frames contains a particular customer
def contains_customer(lst, customer_id):
    for customer in lst:
        if customer_id == customer['customer_id'].values[0]:
            return customer
    return None

# creates a list of customer objects
customer_list = []
for customer in sales_customers:
    sales_history = customer
    services_history = contains_customer(services_customers, customer['customer_id'].values[0])
    survey_history = contains_customer(survey_customers, customer['customer_id'].values[0])
    obj = metrics.Customer(sales_history, services_history, survey_history, start_time_ind, end_time_ind, start_time_dep, end_time_dep)
    customer_list.append(obj)

# creates a 2D array of independent variable values for all customers
independent_variables = [customer.summary for customer in customer_list]

# creates a 1D array of dependent variable values for all customers
dependent_variable = [customer.response for customer in customer_list]

def ols(independent_variables, dependent_variable):
    # read all independent and dependent variables into two data frames
    data_df = pd.DataFrame(data=independent_variables)
    target_df = pd.DataFrame(data=dependent_variable)

    # perform linear regression
    target_df = sm.add_constant(target_df) # add constant term
    model = sm.OLS(target_df, data_df).fit()

    # Print out the statistics
    model.summary()

    # returning model at the moment, change to whatever you want
    return model

print(ols(independent_variables, dependent_variable))

# if we eventually want predictions
# predictions = model.predict(data_df)