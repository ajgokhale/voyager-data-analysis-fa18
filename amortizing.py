import numpy as np
import scipy as sp
import pandas as pd
import math
import metrics

#https://www.statista.com/statistics/581017/average-length-of-vehicle-ownership-in-the-united-states-by-vehicle-type/
#avg length of vehicle usage
#2006, new: 52 mo, used: 38 mo
#2016 new: 79 mo, used: 66 mo ~7 years for new

mercedes_coeff = 67/79
money_factor = 0.0019

#distribute the cost of a vehicle annually over average length of ownership

def modify_year(date, year):
    values = date.split("/")
    return values[0] + "/" + values[1] + "/" + str(year)

def calculate_real_price(price, year, row):
    depreciation_time = year - (row['model_year'] - 1)

    depreciation_3yr = \
        1 - metrics.Customer.depreciation_mapping[row['model_class']]
    depreciation = math.pow(depreciation_3yr, 0.33)

    return price * math.pow(depreciation, depreciation_time)

def uniform_distribution(customer_history, row):
    raw_date = row['datetime']
    year = metrics.encode_year(raw_date)
    decay_length = mercedes_coeff*((year - 2006)*2.7+52)
    price = row['msrp']
    price = calculate_real_price(price, year, row)
    num_years = decay_length // 12
    per_year = price / num_years # annual "payment"
    for i in range(int(num_years)):
        new_row = row.copy()
        dummy_year = year + i
        dummy_year = modify_year(raw_date, dummy_year)
        new_row.datetime = dummy_year
        new_row.msrp = per_year
        customer_history = customer_history.append(new_row, ignore_index=True)
    return customer_history

def account_depreciation(customer_history, row):
    raw_date = row['datetime']
    year = metrics.encode_year(raw_date)
    price = row['msrp']
    price = calculate_real_price(price, year, row)
    new_row = row.copy()
    new_row.msrp = price
    customer_history = customer_history.append(new_row, ignore_index=True)
    return customer_history

# def lease_conversion(customer_history, row):
#     raw_date = row['datetime']
#     year = metrics.encode_year(raw_date)
#     price = row['msrp']
#     price = calculate_real_price(price, year, row)
#     num_years = 3
#     residual = price*(1 - metrics.Customer.depreciation_mapping[row['model_class']])
#     depreciation = price - residual
#     per_year = (price + residual) * money_factor * 12 + \
#         (depreciation / num_years)
#     for i in range(int(num_years)):
#         new_row = row.copy()
#         dummy_year = year + i
#         dummy_year = modify_year(raw_date, dummy_year)
#         new_row.datetime = dummy_year
#         new_row.msrp = per_year
#         customer_history = customer_history.append(new_row, ignore_index=True)
#     return customer_history

def lease_conversion(customer_history, row):
    raw_date = row['datetime']
    year = metrics.encode_year(raw_date)
    price = row['msrp']
    price = calculate_real_price(price, year, row)
    residual = price*(1 - metrics.Customer.depreciation_mapping[row['model_class']])
    depreciation = price - residual
    total_lease = (price + residual) * money_factor * 36 + \
        depreciation
    new_row = row.copy()
    new_row.msrp = total_lease
    customer_history = customer_history.append(new_row, ignore_index=True)
    return customer_history

def amortize(customer_history):
    rows_to_remove = []
    ind = 0
    for index, row in customer_history.iterrows():
        #rows_to_remove.append(ind)
        if row['contract_type'] == "Retail":
            rows_to_remove.append(ind)
            #customer_history = uniform_distribution(customer_history, row)
            customer_history = account_depreciation(customer_history, row)
        elif row['contract_type'] == "Lease":
            rows_to_remove.append(ind)
            customer_history = lease_conversion(customer_history, row)
        ind += 1
    customer_history = customer_history.drop(rows_to_remove)
    return customer_history


#A = Pe^rt t=7 years, r=depreciation, P = MSRP
def exponential_decay(customer):
    prices = []
    for price in customer.customer_history['msrp'].values:
        P = price
        r = -0.3 #average decay rate
        for time in np.arange(7):
            prices.append(P - P*(math.pow(math.e,r*(7-time))))
            P = (P - P*(math.pow(math.e,r*(7-time))))
    ex = pd.DataFrame({'prices':prices})
    return ex


#https://leasehackr.com/calculator?make=Mercedes-Benz&msrp=50525&sales_price=44525&months=36&mf=.00109&dp=0&doc_fee=0&acq_fee=795&taxed_inc=0&untaxed_inc=0&rebate=0&resP=59&reg_fee=877&sales_tax=10&memo=WA%20State%20tax&monthlyTax_radio=true&miles=10000&msd=10
#https://www.statista.com/statistics/453170/average-monthly-new-automobile-lease-payment-usa/
#how leases are calculated: payment = depreciation + interest + tax

#average length 36 months
#california ta ~8.5%
#money factor = apr/2400 = .00109 with apr at = 2.62%
#depreciation = (Capitalized Cost - Residual) ÷ Term of Lease
#interest = (Capitalized Cost + Residual Value) × Money Factor
#taxes = assuming california (Monthly Depreciation Cost + Interest) × Local Sales Tax Rate
"""def lease_simulation(customer):
    lease_payments = []
    for price in customer.customer_history['msrp'].values:
        depreciation = (price - 0)/36
        interest = (price + 0)*0.00109
        #taxes = (depreciation + interest)*0.085 uneeded does not add revenue
        monthly_pay = depreciation + interest
        while term_length:
            lease_payments.appened(monthly_pay)
            price = price-monthly_pay
    lease = pd.DataFrame({'lease_payments':lease_payments})
    return lease"""

#in a period of time frame
def lease_simulation(customer, monthly_term_length):
    lease_payments = []
    for price in customer.customer_history['msrp'].values:
        depreciation = (price)/36
        interest = (price)*0.00109
        #taxes = (depreciation + interest)*0.085 uneeded does not add revenue
        monthly_pay = depreciation + interest
        while monthly_term_length > 0:
            lease_payments.append(monthly_pay)
            monthly_term_length -= 1
    lease = pd.DataFrame({'lease_payments':lease_payments})
    return lease

def lease_conversion_old(customer):
    """Converts car MSRP to total amount paid by a lease over an average of 36 months."""
    leases = 0
    for index, row in customer.customer_history.iterrows():
        date = metrics.encode_year(row['datetime'])
        price = row['msrp']
        contract = row['contract_type']
        if contract == 'Lease':
            depreciation = (price)/36
            interest = (price)*0.00109
            monthly_pay = depreciation + interest
            leases += monthly_pay*36
    return leases
