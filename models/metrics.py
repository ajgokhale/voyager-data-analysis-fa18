import numpy as np
import scipy as sp
import pandas as pd

import statsmodels.api as sm
import math

class Customer:
    def __init__(self, sales_history, service_history, survey_history,
            start_time_ind, end_time_ind, start_time_dep, end_time_dep):
        self.customer_history = sales_history
        self.start = start_time_ind
        self.end = end_time_ind
        self.dep_times = (start_time_dep, end_time_dep)
        self.total_trans = self.total_transactions()
        self.summary = [
            self.max_purchase(),
            self.min_purchase(),
            self.total_revenue(),
            self.purchase_gap() / self.total_trans,
            self.retail_purchases() / self.total_trans,
        ]
        self.summary.extend(self.purchases_by_class())
        self.start, self.end = self.dep_times
        self.response = [
            self.total_revenue(),
            self.total_transactions() != 0
        ]

    def total_transactions(self):
        total = 0
        for date in self.customer_history['DATE'].values:
            encoded = encode_date(date)
            if encoded >= start and encoded < end:
                total += 1
        return total

    def transactions(self, f, init):
        agg = init
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['DATE'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                agg = f(self, agg, index)
        return agg

    def max_purchase(self):
        return self.transactions(self.update_max_purchase, 0)

    def update_max_purchase(self, max_value, index):
        return max(self.customer_history['TOT_MSRP'].values[index], max_value)

#    def max_purchase(customer_history, start, end):
#        max_value = 0
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                max_value = max(customer_history['TOT_MSRP'].values[index], max_value)
#        return max_value
#    def min_purchase(customer_history, start, end):
#        min_value = float('inf')
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                min_value = min(customer_history['TOT_MSRP'].values[index], min_value)
#        return min_value
#
    def min_purchase(self):
        return self.transactions(self.update_min_purchase, float('inf'))

    def update_min_purchase(self, min_value, index):
        return min(self.customer_history['TOT_MSRP'].values[index], min_value)

    def total_revenue(self):
        return self.transactions(self.update_total_revenue, 0)

    def update_total_revenue(self, total, index):
        return total + self.customer_history['TOT_MSRP'].values[index]
#    def total_revenue(customer_history, start, end):
#        total = 0
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                total += customer_history['TOT_MSRP'].values[index]
#        return total
#
    def purchase_gap(self):
        return self.transactions(self.update_purchase_gap, 0)

    def update_purchase_gap(self, sum_diff, index):
        date = self.customer_history['DATE'].values[index]
        purchase_month = encode_month(date)
        model_year = self.customer_history['MOD_YEAR'].values[index]
        model_month = (model_year - 1) * 12 + release_month
        return sum_diff + (purchase_month - model_month)

    # Need to confirm this is correct
#    def model_purchase_gap(customer_history, start, end):
#        release_month = 6
#        sum_of_diff = 0
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                purchase_month = encode_month(date)
#                model_year = customer_history['MOD_YEAR'].values[index]
#                model_month = (model_year - 1) * 12 + release_month
#                sum_of_diff += (purchase_month - model_month)
#        return sum_of_diff

    def purchases_by_class(self):
        purchases = dict()
        for model in self.classes:
            purchases[model] = 0
        purchases = self.transactions(self.update_purchases_by_class, purchases)
        distinct_classes = 0
        classes = []
        for model in purchases.keys():
            if purchases[model] != 0:
                classes.append(model)
                distinct_classes += 1
        classes.append(distinct_classes)
        return classes

    def update_purchases_by_class(self, purchases, index):
        classLetter = self.customer_history['MOD_CLASS'].values[index].strip()
        purchases[classLetter] += 1
        return purchases

#    def distinct_classes(customer_history, start, end):
#        classes = set()
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                classLetter = customer_history['MOD_CLASS'].values[index].strip()
#                classes.add(classLetter)
#        return len(classes)

    def retail_purchases(self):
        return self.transactions(self.update_retail_purchases, 0)

    def update_retail_purchases(self, total, index):
        contract = customer_history['CONTRACT_TYPE'].values[index]
        if contract == "Retail": total += 1
        return total

#    def retail_purchases(customer_history, start, end):
#        num_retail = 0
#        for index in range(len(customer_history.values)):
#            date = customer_history['DATE'].values[index]
#            encoded = encode_date(date)
#            if encoded >= start and encoded < end:
#                contract = customer_history['CONTRACT_TYPE'].values[index]
#                if contract == "Retail": num_retail += 1
#        return num_retail

    def purchase_indicator(self):
        return (self.total_trans != 0)
