import numpy as np
import pandas as pd
import metrics
import sys
import math
import amortizing

parameter_file = 'output/cache/parameters.txt'

def contains_customer(lst, customer_id):
    for customer in lst:
        if customer_id == customer['customer_id'].values[0]:
            return customer, False
    return None, True

def customers(start_time_ind, end_time_ind, start_time_dep, end_time_dep, allow_single, amortized):
    # read in data as Pandas DataFrames
    sales = pd.read_csv('../data/salescsv.csv')
    services = pd.read_csv('../data/servicescsv.csv')
    survey = pd.read_csv('../data/surveycsv.csv')

    # remove any duplicate data in each of the data sets
    sales.drop_duplicates(subset=['customer_id','household_id','model_year',
        'model_class', 'role', 'trans_type', 'contract_type'], inplace=True)
    #services.drop_duplicates(subset=['customer_id','household_id','amount_paid', 'amount_warranty', 'model_year', 'model_type'], inplace=True)
    #survey.drop_duplicates(subset=['customer_id','household_id','ltr','model_year','model_class','model_type'], inplace=True)

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
        #if amortized:
        #    sales_history = amortizing.amortize(sales_history)
        services_history, invalid = contains_customer(services_customers, customer['customer_id'].values[0])
        if invalid: continue
        #survey_history = contains_customer(survey_customers, customer['customer_id'].values[0])
        survey_history = None
        obj = metrics.Customer(sales_history, services_history, survey_history, 
            start_time_ind, end_time_ind, start_time_dep, end_time_dep, allow_single,
            amortized)
        if obj.summary != None: 
            customer_list.append(obj)
            i += 1
            if i%100 == 0:
                print(i, "customer objects constructed")

    print("Finished with", i, "customer objects constructed")
    return customer_list

def customer_df(sti, eti, std, etd, allsin, amort=False):
    # creates a 2D array of independent variable values for all customers
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg == "saved":
            try:
                f = open(parameter_file,'r')
                eti_read    = f.readline().strip()
                allsin_read = (f.readline().strip() == "1")
                amort_read  = (f.readline().strip() == "1")
                f.close()
                load = True
                if eti_read != eti or \
                    allsin_read != allsin or \
                    amort_read != amort:
                    response = input("Saved data does not match given parameters,"
                        +" continue? [y/n]")
                    if response.strip() == "n":
                        load = False
                if load:
                    x = np.load("output/cache/ind_arr.npy")
                    y = np.load("output/cache/dep_arr.npy")
                    return x, y, eti_read, allsin_read, amort_read
            except:
                print("Could not load saved files")
    customer_list = customers(sti, eti, std, etd, allsin, amort)
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

    np.save("output/cache/ind_arr.npy", x)
    np.save("output/cache/dep_arr.npy", y)
    write_eti = eti
    write_sing  = "1" if allsin else "0"
    write_amort = "1" if amort else "0"
    f = open(parameter_file,'w')
    f.seek(0)
    f.truncate()
    f.write(write_eti+'\n')
    f.write(write_sing+'\n')
    f.write(write_amort+'\n')
    f.close()
    return x, y, eti, allsin, amort