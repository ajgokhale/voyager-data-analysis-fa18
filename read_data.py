import numpy as np
import pandas as pd
import metrics
import sys
import math

def contains_customer(lst, customer_id):
    for customer in lst:
        if customer_id == customer['customer_id'].values[0]:
            return customer, False
    return None, True

def customers(start_time_ind, end_time_ind, start_time_dep, end_time_dep, allow_single, amortized=False):
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

    print("Data read in and parsed")

    # helper method to see if a list of customer data frames contains a particular customer
    i = 0
    # creates a list of customer objects
    customer_list = []
    for customer in sales_customers:
        sales_history = customer
        services_history, invalid = contains_customer(services_customers, customer['customer_id'].values[0])
        if invalid: continue
        survey_history = contains_customer(survey_customers, customer['customer_id'].values[0])

        obj = metrics.Customer(sales_history, services_history, survey_history, 
            start_time_ind, end_time_ind, start_time_dep, end_time_dep, allow_single)
        if obj.summary != None: customer_list.append(obj)
        i += 1

    print(i, " customer objects successfully constructed and instantiated")
    if amortized:
        for customer in customer_list:
            print(vehicle_amortizing.exponential_decay(customer))
    return customer_list

def customer_df(sti, eti, std, etd, allsin):
    # creates a 2D array of independent variable values for all customers
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg == "saved":
            try:
                x = np.load("output/ind_arr.npy")
                y = np.load("output/dep_arr.npy")
                return x, y
            except:
                print("Could not load saved files")
    customer_list = customers(sti, eti, std, etd, allsin)
    independent_variables = []
    dependent_variables = []
    for customer in customer_list:
        valid = True
        for index in range(len(customer.summary)):
            element = customer.summary[index]
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

    np.save("output/ind_arr.npy", x)
    np.save("output/dep_arr.npy", y)
    return x, y