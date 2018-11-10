import numpy as np
import scipy as sp
import pandas as pd

import statsmodels.api as sm
import math

# utility functions to convert date strings to encoded int
# encoded date is comparable, but does not support arithmetic
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
        for date in self.customer_history['datetime'].values:
            if date >= self.start and date < self.end:
                total += 1
        return total

    def max_purchase(customer_history, start, end):
        max_value = 0
        for index in range(len(customer_history.values)):
            date = customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                max_value = max(customer_history['msrp'].values[index], max_value)
        return max_value
    def min_purchase(customer_history, start, end):
        min_value = float('inf')
        for index in range(len(customer_history.values)):
            date = customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                min_value = min(customer_history['msrp'].values[index], min_value)
        return min_value
        
    def total_revenue(customer_history, start, end):
        total = 0
        for index in range(len(customer_history.values)):
            date = customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                total += customer_history['msrp'].values[index]
        return total

    # Need to confirm this is correct
    def model_purchase_gap(customer_history, start, end):
        release_month = 6
        sum_of_diff = 0
        for index in range(len(customer_history.values)):
            date = customer_history['datetime'].values[index]
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
            date = customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                classLetter = customer_history['model_class'].values[index].strip()
                classes.add(classLetter)
        return len(classes)

    def retail_purchases(customer_history, start, end):
        num_retail = 0
        for index in range(len(customer_history.values)):
            date = customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                contract = customer_history['contract_type'].values[index]
                if contract == "Retail": num_retail += 1
        return num_retail

    def purchase_indicator(self):
        return (self.total_trans != 0)
