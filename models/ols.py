import numpy as np
import pandas as pd
from sklearn import linear_model
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

# creates a column of independent variable values for all customers
total_transactions = [customer.total_transactions() for customer in customer_list]
min_purchase = [customer.min_purchase() for customer in customer_list]
max_purchase = [customer.max_purchase() for customer in customer_list]
purchases_by_class = [customer.purchases_by_class() for customer in customer_list]
retail_purchases = [customer.retail_purchases() for customer in customer_list]
purchase_indicator = [customer.purchase_indicator() for customer in customer_list]

# creates a column of dependent variable values for all customers
total_revenue = [customer.total_revenue() for customer in customer_list]

def ols(dependent_variable, *args):
    # read all independent and dependent variables into two data frames
    data_array = [0] * len(*args)
    for i, arg in enumerate(*args):
        data_array[i] = arg
    data_np_array = np.transpose(data_array)
    data_df = pd.DataFrame(data=data_np_array[1:,:], columns=data_np_array[0])
    target_df = pd.DataFrame(data=dependent_variable[1:], columns=dependent_variable[0])

    # perform linear regression
    lm = linear_model.LinearRegression()
    model = lm.fit(data_df, target_df) # creates a linear model
    predictions = lm.predict(data_df) # predicts values using the model
    score = lm.score(data_df, target_df) # returns R^2 score
    coef = lm.coef_ # returns an array of the coefficients of the model
    intercept = lm.intercept_ # returns the intercept of the model

    # what do you want to return?
    return score 

print(ols(total_revenue, total_transactions, min_purchase, max_purchase))