import numpy as np
import pandas as pd
import statsmodels.api as sm
import metrics
import cluster
import sys
import seaborn as sns
import cluster
import itertools
import math
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

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

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"

# helper method to see if a list of customer data frames contains a particular customer
def contains_customer(lst, customer_id):
    for customer in lst:
        if customer_id == customer['customer_id'].values[0]:
            return customer, False
    return None, True
i = 0
# creates a list of customer objects
customer_list = []
for customer in sales_customers:
    sales_history = customer
    services_history, invalid = contains_customer(services_customers, customer['customer_id'].values[0])
    if invalid: continue
    survey_history = contains_customer(survey_customers, customer['customer_id'].values[0])

    obj = metrics.Customer(sales_history, services_history, survey_history, start_time_ind, end_time_ind, start_time_dep, end_time_dep)

    if obj.summary != None: customer_list.append(obj)
    i+=1

# creates a 2D array of independent variable values for all customers
independent_variables = []
dependent_variables = []
for customer in customer_list:
    valid = True
    for element in customer.summary:
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

# independent_variables = [customer.summary for customer in customer_list if float('nan') not in customer.summary]
x = np.asarray(independent_variables)

# creates a 1D array of dependent variable values for all customers
y = np.asarray(dependent_variables)

# join x and y
joined = np.vstack((np.transpose(metrics.Customer.metric_names), np.concatenate((x, y), axis=1)))

# visualization functions
def plot_2dcluster(dataframe):
	"""Same implementation as below, but with 2 columns of customer stats
	and the 3rd containing a clustering index"""
	fig = plt.figure()
	# Creating a grid
	ax = fig.add_subplot(111)
	df = dataframe
	# Adding in a color-coded scatterplot to the grid
	ax.scatter(df.ix[:, 0], df.iloc[:, 1], c = df.iloc[:, 2], s = 40, cmap = 'viridis')
	plt.show()

def plot_3dcluster(dataframe, z_elevation, xy_azimuth):
	"""Plot the clustering results, where dataframe is a dataframe with 
	3 columns containing customer statistics and the 4th containing a 
	clustering index identifying the cluster each customer is a part of.
	z_elevation = vertical angle of the 3d plot (the plane facing you)
	xy_azimuth = the right/left rotation of the 3d plot"""
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	df = dataframe
	# Adding in color-coded scatterplot to the grid
	ax.scatter(df.ix[:, 0], df.iloc[:, 1], df.iloc[:, 2], c = df.iloc[:, 3], s = 50, cmap = 'viridis') #Fun fact! With df.iloc[:, n] where n is an index, you can access any column in a dataframe using an index.  No need to know the names of the columns!
	ax.view_init(z_elevation, xy_azimuth)
	plt.show()

def plot_3dcluster_360(dataframe, z_elevation):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    df = dataframe
	# Adding in color-coded scatterplot to the grid
    ax.scatter(df.ix[:, 0], df.iloc[:, 1], df.iloc[:, 2], c = df.iloc[:, 3], s = 50, cmap = 'viridis')
    for angle in range(0, 360):
        ax.view_init(z_elevation, angle)
        plt.draw()
        plt.pause(.001)

# plot combos
combos_3 = itertools.combinations(range(len((joined)[0])), 3)
combos_3 = list(combos)
clustered_sets_3d = []
for combo_3 in combos_3:
    array_3 = (joined)[:, combo_3]
    std_array_3 = StandardScaler().fit_transform(array_3[1:])
    std_df_3 = pd.DataFrame(std_array_3, columns=std_array_3[0])
    k_3, gapdf_3 = cluster.optimalK(std_df_3)
    clustered_3 = cluster.clusterKMeans(std_df_3, k_3)
    clustered_sets_3d.append(clustered_3)
    print('gottem')
clustered_sets_3d.sort()
for i in range(10):
    plot_3dcluster(clustered_sets_3d[i][1], 30, 150)
combos_2 = itertools.combinations(range(len((joined)[0])), 2)
combos_2 = list(combos)
clustered_sets_2d = []
for combo_2 in combos_2:
    array_2 = (joined)[:, combo_2]
    std_array_2 = StandardScaler().fit_transform(array_2[1:])
    std_df_2 = pd.DataFrame(std_array_2, columns=std_array_2[0])
    k_2, gapdf_2 = cluster.optimalK(std_df_2)
    clustered_2 = cluster.clusterKMeans(std_df_2, k_2)
    clustered_sets_2d.append(clustered_2)
    print('gettem')
clustered_sets_2d.sort()
for i in range(10):
    plot_2dcluster(clustered_sets_2d[i][1], 30, 150)