import numpy as np
import scipy as sp
import pandas as pd

import statsmodels.api as sm
import math

# utility functions to convert date strings to encoded int
# encoded date is comparable, but does not support arithmetic
def encode_year(date_str):
    date = date_str.split('/')
    return int(date[2])
def encode_month(date_str):
    date = date_str.split('/')
    return int(date[0]) + int(date[2])*12
def encode_date(date_str):
    date = date_str.split('/')
    return (int(date[0]) - 1)*31 + (int(date[1]) - 1) + int(date[2])*372

class Customer:
    classes = []
    release_month = 6 # the month at which next year's model is released (ex: 2018 model releases in June 2017)

    # when the Customer object is instantiated, all its information will be calculated automatically
    def __init__(self, sales_history, service_history, survey_history,
            start_time_ind, end_time_ind, start_time_dep, end_time_dep):
        self.customer_history = sales_history
        # set the time period for which metrics are being calculated, start_time_ind/end_time_ind
        # is the time period for independent variables
        self.start = start_time_ind
        self.end = end_time_ind
        # save the time period for dependent variables
        self.dep_times = (start_time_dep, end_time_dep)
        # calculate total number of transactions a customer has made (helps for calculating other metrics)
        self.total_trans = self.total_transactions()
        # store behavioral metrics in a "summary" list
        self.summary = [
            self.max_purchase(),
            self.min_purchase(),
            self.total_revenue(),
            self.purchase_gap() / self.total_trans,
            self.retail_purchases() / self.total_trans,
        ]
        self.summary.extend(self.purchases_by_class())
        # reset the time period for dependent variables
        self.start, self.end = self.dep_times
        # store dependent metrics in a "response" list
        self.response = [
            self.total_revenue(),
            self.total_transactions() != 0
        ]

    def total_transactions(self):
        total = 0
        for date in self.customer_history['strdatetime'].values:
            encoded = encode_date(date)
            print(encoded)
            if encoded >= self.start and encoded < self.end:
                total += 1
        return total
    def purchase_freq(customer_history, start, end):
        num_trans = 0
        for date in self.customer_history['strdatetime'].values:
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                num_trans += 1
            return num_trans
    def max_purchase(customer_history, start, end):
        max_value = 0
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                max_value = max(customer_history['msrp'].values[index], max_value)
        return max_value
    def min_purchase(customer_history, start, end):
        min_value = float('inf')
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                min_value = min(customer_history['msrp'].values[index], min_value)
        return min_value
    def total_revenue(customer_history, start, end):
        total = 0
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                total += customer_history['msrp'].values[index]
        return total

    # Need to confirm this is correct
    def model_purchase_gap(customer_history, start, end):
        release_month = 6
        sum_of_diff = 0
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                purchase_month = encode_month(date)
                model_year = customer_history['model_year'].values[index]
                model_month = (model_year - 1) * 12 + release_month
                sum_of_diff += (purchase_month - model_month)
        return sum_of_diff

    def distinct_classes(customer_history, start, end):
        classes = set()
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                classLetter = customer_history['model_class'].values[index].strip()
                classes.add(classLetter)
        return len(classes)

    def retail_purchases(customer_history, start, end):
        num_retail = 0
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                contract = customer_history['contract_type'].values[index]
                if contract == "Retail": num_retail += 1
        return num_retail

    def purchase_indicator(self):
        return (self.total_trans != 0)


    #compile a dictionary of model to base MSRP data structure to reference
    #(base_msrp, key: mdoel, value: price)

    #Average difference between  base MSRP and transaction MSRP
    def average_value_options(self, start, end):
        #iterate through transaction and access correct base msrp through data structure
        #add total transactions, subtract sum base msrp, divide by #transactions
        return

    #Average amount spent on each servicing transaction
    def spend_per_service(self, start, end):
        service_num = 0
        service_paid = 0
        #for the values in the service history strdatetime, pick appropriate timeframe
        for index in range(len(self.service_history.values)):
            date = self.service_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                service = self.service_history['AMT_DMS_CP_STOT'].values[index]
                warranty = self.service_history['AMT_DMS_WARR_STOT'].values[index]
                service_paid = service_num + service + warranty
                service_num += 1
        return service_paid/service_num

    #Average difference between successive vehicle purchase MSRPs
    def change_vehicle_spend(self, start, end):
        differences = []
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                if customer_history['contract_type'].values[index] == "Retail" and index < len(customer_history) - 1:
                    prev = customer_history['AMT_TOT_MSRP'].values[index]
                    cur = customer_history['AMT_TOT_MSRP'].values[index + 1]
                    differences.append((prev-cur))
        return sum(differences)/self.total_trans

    #Total number of X-class vehicles purchased
    #dictionary for each X-class. kinda clunky but should work
    def total_class_purchase(self, start, end):
        class_totals = dictionary()
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                if  customer_history['contract_type'].values[index] == "Retail":
                    model = customer_history['MODEL_CLASS'].values[index]
                    if model not in class_totals:
                        class_totals.update(model, 1)
                    else:
                        class_totals.update(model, class_totals.get(model) + 1)
        return class_totals

    #Number of household vehicles serviced within the last year
    #maybe wrong, this is total services used within a time interval
    def active_household_inventory(self, start, end):
        service_total = 0
        for date in self.service_history['strdatetime'].values:
            if date >= start and date < end:
                service_total += 1
        return total

    #Average amount of time between individual vehicle purchases
    #How did we say we were doing strdatetime?
    def average_vehicle_interval(self, start, end):
        count = 0
        holder = list()
        differences = list()
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                if customer_history['contract_type'].values[index] == "Retail":
                    holder.append(encoded)
                    count +=1
        for i in len(holder)-1:
            differences.append(holder[i+1] - holder[i])
        return sum(differences)/count

    #Average number of transactions per year
    #need to re-write to go by year
    def annual_service_freq(self, start, end):
        service_total = 0
        for date in self.service_history['strdatetime'].values:
            if date >= start and date < end:
                service_total += 1
        return service_total

    #Ratio of leasing transactions to total transactions
    def lease_rate(self, start, end):
        lease_count = 0
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if date >= start and date < end:
                if customer_history['contract_type'].values[index] == "lease":
                    lease_count += 1
        return lease_count/self.total_trans

    #Ratio of time since last purchase versus average purchase interval
    def recency_score(self, today_date):
        last_purchase_date = 0
        today = encode_date(today_date)
        avgerage_interval = average_vehicle_interval(start, end)
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            encoded = encode_date(date)
            last_purchase_date = max(last_purchase_date, encoded)
        return (today - last_purchase_date)/average_interval

    #Number of intervals between servicing transactions that exceed X years
    def aggregate_service_inactivity(self, start, end, x_years):
        holder = list()
        differences = list()
        for index in range(len(self.service_history.values)):
            date = self.service_history['strdatetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                holder.append(encoded)
        for i in len(holder)-1:
            differences.append(holder[i+1] - holder[i])
        return len([y for y in differences if y > x_years])

    #Average difference between year of purchase and model year of vehicle
    def year_disparity(self):
        differences = list()
        for index in range(len(customer_history.values)):
            date = customer_history['strdatetime'].values[index]
            purchase_year = encode_year(date)
            model_year = customer_history['MODEL_YEAR'].values[index]
            differences.append(purchase_year - model_year)
        return sum(differences)/self.total_trans

    #Index reflecting consumer sentiment and buying intentions
    def cci(self):
        return

    #Average annual disposable income
    def disposable_income(self):
        return
