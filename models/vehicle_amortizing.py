import numpy as np
import scipy as sp
import pandas as pd
import math
import metrics

#https://www.statista.com/statistics/581017/average-length-of-vehicle-ownership-in-the-united-states-by-vehicle-type/
#avg length of vehicle usage
#2006, new: 52 mo, used: 38 mo
#2016 new: 79 mo, used: 66 mo ~7 years for new

#distribute the cost of a vehicle annually over average length of ownership

def uniform_decay(customer):
    prices = make_array()
    for price in customer.customer_history['msrp'].values:
        per_year = (price/79)*12 #annual "payment"
        for i in np.arange(7)
                prices.append(per_year)
    df = pd.DataFrame({'prices':prices})
    return df

#A = Pe^rt t=7 years, r=depreciation, P = MSRP
def exponential_decay(customer, class_depreciation):
    prices = make_array()
    for price in customer.customer_history['msrp'].values:
        P = price
        r = depreciation
        for time in np.arange(7)
            prices.append(P - P*(math.pow(math.e,r*(7-time)))
    ex = pd.DataFrame({'prices':prices})
    return ex


#https://leasehackr.com/calculator?make=Mercedes-Benz&msrp=50525&sales_price=44525&months=36&mf=.00109&dp=0&doc_fee=0&acq_fee=795&taxed_inc=0&untaxed_inc=0&rebate=0&resP=59&reg_fee=877&sales_tax=10&memo=WA%20State%20tax&monthlyTax_radio=true&miles=10000&msd=10
#https://www.statista.com/statistics/453170/average-monthly-new-automobile-lease-payment-usa/
#how leases are calculated: payment = depreciation + interest + tax
#unsure what average lease is for luxury cars

#average length 36 months
#california ta ~8.5%
#money factor = apr/2400 = .00109 with apr at = 2.62%
#depreciation = (Capitalized Cost - Residual) ÷ Term of Lease
#interest = (Capitalized Cost + Residual Value) × Money Factor
#taxes = assuming california (Monthly Depreciation Cost + Interest) × Local Sales Tax Rate
def lease_simulation(customer):
    lease_payments = make_array()
    for price in customer.customer_history['msrp'].values:
        depreciation = (price - 0)/36
        interest = (price + 0)*0.00109
        #taxes = (depreciation + interest)*0.085 uneeded does not add revenue
        monthly_pay = depreciation + interest
        while term_length
            lease_payments.appened(monthly_pay)
            price = price-monthly_pay
    lease = pd.DataFrame({'lease_payments':lease_payments})
    return lease

#in a period of time frame
def lease_simulation(customer, term_length):
    lease_payments = make_array()
    for price in customer.customer_history['msrp'].values:
        depreciation = (price - 0)/36
        interest = (price + 0)*0.00109
        #taxes = (depreciation + interest)*0.085 uneeded does not add revenue
        monthly_pay = depreciation + interest
        while term_length > 0:
            lease_payments.appened(monthly_pay)
            term_length -= 1
    lease = pd.DataFrame({'lease_payments':lease_payments})
    return lease
