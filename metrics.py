import numpy as np
import scipy as sp
import pandas as pd

import statsmodels.api as sm
import math
import vehicle_amortizing

from datetime import date

# utility functions to convert date strings to encoded int
# encoded date is comparable, but does not support arithmetic
def encode_year(date_str):
    date = date_str.split('/')
    return int(date[2])
def encode_month(date_str):
    date = date_str.split('/')
    return int(date[0]) + int(date[2])*12
def encode_date(date_str):
    date_lst = date_str.split('/')
    #return (int(date[0]) - 1)*31 + (int(date[1]) - 1) + int(date[2])*372
    return date(int(date_lst[2]), int(date_lst[0]), int(date_lst[1]))

class Customer:
    classes = ["CL ", "GL ", "C  ", "R  ", "GLE", "M  ", "B  ", 
    "CLA", "CLK", "E  ", "CLS", "GLA", "GLC", "GLK", "GLS", "S  ", 
    "SL ", "SLK", "SLS", "SMT", "SPR", "SLR", "G  "]
    release_month = 6 # the month at which next year's model is released (ex: 2018 model releases in June 2017)
    mcsi = pd.read_csv('mcsi.csv')
    inactivity_years = 2
    inactivity_threshold = inactivity_years * 365
    #metric_names = np.asarray(["Maximum Purchase", "Minimum Purchase", "Model & Purchase Year Disparity", "Percentage of Retail Purchases",
    # "Number of Distinct Vehicle Classes Purchased", "Average Service Transaction", "Total Revenue", "Vehicle Purchase Indicator"])

    # when the Customer object is instantiated, all its information will be calculated automatically

    def __init__(self, sales_history, service_history, survey_history,
            start_time_ind, end_time_ind, start_time_dep, end_time_dep,
            allow_single=True):

        self.customer_history = sales_history
        self.service_history = service_history
        self.survey_history = survey_history

        # set the time period for which metrics are being calculated, start_time_ind/end_time_ind
        # is the time period for independent variables
        self.start = encode_date(start_time_ind)
        self.end = encode_date(end_time_ind)
        # save the time period for dependent variables
        # calculate total number of transactions a customer has made (helps for calculating other metrics)
        self.total_trans, self.service_trans = self.total_transactions()
        # store behavioral metrics in a "summary" list
        if allow_single: minimum = 0
        else: minimum = 1
        if self.total_trans > minimum and self.service_trans > minimum: #and allow_single:
            if self.average_vehicle_interval() == 0:
                self.summary = None
                self.response = None
            else:
                self.summary = [
                    self.total_trans, #0
                    self.service_trans, #1
                    self.max_purchase(), #2
                    self.model_purchase_gap(), #3
                    self.retail_purchases(), #4
                    self.distinct_classes(), #5
                    self.spend_per_service(), #6
                    self.aggregate_service_inactivity(self.inactivity_threshold), #7
                ]
                # self.add_classes()
                if not allow_single:
                    self.summary.extend([
                        self.average_vehicle_interval(), #8
                        self.change_vehicle_spend(), #9
                        self.recency_score(), #10
                        ])
                # reset the time period for dependent variables
                self.start, self.end = encode_date(start_time_dep), encode_date(end_time_dep) 
                # store dependent metrics in a "response" list
                self.response = [
                    self.total_revenue(),
                    self.purchase_indicator()
                ]
        else:
            self.summary = None
            self.response = None
    @staticmethod
    def metric_names(allow_single):
        metric_list = ["Total Purchases", "Total Servicing Visits", "Maximum Purchase", "Model & Purchase Year Disparity", "Percentage of Retail Purchases",
            "Number of Distinct Vehicle Classes Purchased", "Average Service Transaction", "Total " + str(self.inactivity_years) + "-Year Inactivity Periods", ]
        if not allow_single:
            metric_list.extend(["Average Purchase Interval", "Average Change in Purchase","Recency Score", ])
        metric_list.extend(["Total Revenue", "Vehicle Purchase Indicator",])
        return np.asarray(metric_list)

    def add_classes(self):
        class_purchases = self.total_class_purchase()
        for vehicle_class in self.classes:
            self.summary.append(class_purchases[vehicle_class])

    def total_transactions(self):
        total = 0
        service_total = 0
        for date in self.customer_history['datetime'].values:
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                total += 1
        for date in self.service_history['datetime'].values:
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                service_total += 1
        return total, service_total

####################
#SALES METRICS
####################
    def max_purchase(self):
        max_value = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                max_value = max(self.customer_history['msrp'].values[index], max_value)
        return max_value
    def min_purchase(self):
        min_value = float('inf')
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                min_value = min(self.customer_history['msrp'].values[index], min_value)
        return min_value

    def total_sales_revenue(self):
        total = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                total += self.customer_history['msrp'].values[index]
        # for index in range(len(self.service_history.values)):
        #     date = self.service_history['datetime'].values[index]
        #     encoded = encode_date(date)
        #     if encoded >= self.start and encoded < self.end:
        #         purchase = self.service_history['amount_paid'].values[index]
        #         if purchase > 0:
        #             total += purchase
        return total

    # Need to confirm this is correct
    def model_purchase_gap(self):
        release_month = 6
        sum_of_diff = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                purchase_month = encode_month(date)
                model_year = self.customer_history['model_year'].values[index]
                model_month = (model_year - 1) * 12 + release_month
                sum_of_diff += (purchase_month - model_month)
        return sum_of_diff / self.total_trans

    def distinct_classes(self):
        """Returns the number of distinct car classes the customer owns, E.g. if
        a customer owns 2 M class cars and 3 GLA class cars, distinct_classes
        will return 2."""
        classes = set()
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                classLetter = self.customer_history['model_class'].values[index].strip()
                classes.add(classLetter)
        return len(classes)

    def retail_purchases(self):
        num_retail = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                contract = self.customer_history['contract_type'].values[index]
                if contract == "Retail": num_retail += 1
        return num_retail

    def purchase_indicator(self):
        if self.total_trans != 0:
            return 1
        else:
            return 0

    def total_class_purchase(self):
        """Returns a dictionary where each key is the name of a class and
        the value is the total number of X-class purchased."""
        class_totals = dict()
        for vehicle_class in self.classes:
            class_totals[vehicle_class] = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                model = self.customer_history['model_class'].values[index]
                class_totals.update({model: class_totals.get(model) + 1})
        return class_totals

#Average difference between successive vehicle purchase MSRPs
    def change_vehicle_spend(self):
        """Returns the average difference in spend between each successive
        vehicle purchase."""
        holder = list()
        differences = list()
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                msrp = self.customer_history['msrp'].values[index]
                holder.append((encoded, msrp))
        holder.sort(key=lambda x: x[0])
        for i in range(len(holder) - 1):
            diff = holder[i+1][1]-holder[i][1]
            differences.append(diff)
        return sum(differences) / (len(holder) - 1)

    def average_vehicle_interval(self):
        """Returns the average amount of time between each vehicle purchase."""
        count = 0
        holder = list()
        differences = list()
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                holder.append(encoded)
                count +=1
        holder.sort()
        for i in range(len(holder) - 1):
            delta = holder[i+1]-holder[i]
            differences.append(delta.days)
        return sum(differences)/(len(holder) - 1)

    def used_purchases(self):
        num_used = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                contract = self.customer_history['contract_type'].values[index]
                used = self.customer_history['trans_type']
                if contract == "Retail" and (used == "Pre-owned" or used == "Used") : num_used += 1
        return num_used

    def used_retail(self):
        return used_purchases(self)/retail_purchases(self)

#######################
#SERVICE METRICS
#######################

    #Average amount spent on each servicing transaction
    def spend_per_service(self):
        service_num = 0
        service_paid = 0
        #for the values in the service history datetime, pick appropriate timeframe
        for index in range(len(self.service_history.values)):
            date = self.service_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                service = self.service_history['amount_paid'].values[index]
                #warranty = self.service_history['amount_warranty'].values[index]
                if service > 0:
                    service_paid += service
                    service_num += 1
        if service_num == 0:
            return 0
        return service_paid/service_num

    def total_service_revenue(self):
        total = 0
        for index in range(len(self.service_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                total += self.service_history['amount_paid'].values[index]
        return total

    #Number of household vehicles serviced within the last year
    #maybe wrong, this is total services used within a time interval
    def active_household_inventory(self):
        return None


    #amount of service charge vs total transaction sum
    def paid_service_proportion(self):
        return self.total_service_revenue/self.total_sales_revenue

############################
############################

    #Average amount of time between individual vehicle purchases
    #How did we say we were doing datetime?
    # def average_vehicle_interval(self):
    #     count = 0
    #     holder = list()
    #     differences = list()
    #     for index in range(len(self.customer_history.values)):
    #         date = self.customer_history['datetime'].values[index]
    #         encoded = encode_date(date)
    #         if encoded >= self.start and encoded < self.end:
    #             holder.append(encoded)
    #             count +=1
    #     holder.sort()
    #     for i in range(len(holder) - 1):
    #         delta = holder[i+1]-holder[i]
    #         differences.append(delta.days)
    #     if count == 1:
    #         timeframe = self.end - self.start
    #         return timeframe.days / 1.5
    #     else:
    #         return sum(differences)/(count - 1)


############################
############################

    #Ratio of time since last purchase versus average purchase interval
    def recency_score(self):
        date = encode_date(self.customer_history['datetime'].values[0])
        last_purchase_date = date.min
        today = date.today()
        average_interval = self.average_vehicle_interval()
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                last_purchase_date = max(last_purchase_date, encoded)
        return (today - last_purchase_date).days/average_interval

############################
############################

    #Number of intervals between servicing transactions that exceed X days
    def aggregate_service_inactivity(self, x_days):
        holder = list()
        differences = list()
        for index in range(len(self.service_history.values)):
            date = self.service_history['datetime'].values[index]
            encoded = encode_date(date)
            if encoded >= self.start and encoded < self.end:
                holder.append(encoded)
        holder.sort()
        for i in range(len(holder) - 1):
            delta = holder[i+1] - holder[i]
            differences.append(delta.days)
        return len([y for y in differences if y > x_days])

###CANNOT IMPLEMENT#########
############################

    #Average difference between year of purchase and model year of vehicle
    #def year_disparity(self):
    #    differences = list()
    #    for index in range(len(self.customer_history.values)):
    #        date = self.customer_history['datetime'].values[index]
    #        purchase_year = encode_year(date)
    #        model_year = self.customer_history['MODEL_YEAR'].values[index]
    #        differences.append(purchase_year - model_year)
    #    return sum(differences)/self.total_trans

    #Index reflecting consumer sentiment and buying intentions
    def calculate_mcsi_score(self):
        total = 0
        for index in range(len(self.customer_history.values)):
            date = self.customer_history['datetime'].values[index]
            month = encode_month(date)
            year = encode_year(date)
            total += self.mcsi.values.enumerate()[12 * (year - 2005) + (month - 9)]
        return total / self.total_trans


    #Average annual disposable income
    def disposable_income(self):
        return
