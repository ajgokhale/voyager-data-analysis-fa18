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
import read_data

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True

#################################################

x, y = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single)

# join x and y
joined = np.vstack((np.transpose(metrics.Customer.metric_names(allow_single)), np.concatenate((x, y), axis=1)))

# visualization functions
def plot_2dcluster(dataframe):
	"""Same implementation as below, but with 2 columns of customer stats
	and the 3rd containing a clustering index"""
	fig = plt.figure()
	# Creating a grid
	ax = fig.add_subplot(111)
	df = dataframe
	# Adding in a color-coded scatterplot to the grid
	ax.scatter(df.iloc[:, 0], df.iloc[:, 1], c = df.iloc[:, 2], s = 40, cmap = 'viridis')
	plt.show()

def plot_3dcluster(dataframe, z_elevation=30, xy_azimuth=150):
	"""Plot the clustering results, where dataframe is a dataframe with 
	3 columns containing customer statistics and the 4th containing a 
	clustering index identifying the cluster each customer is a part of.
	z_elevation = vertical angle of the 3d plot (the plane facing you)
	xy_azimuth = the right/left rotation of the 3d plot"""
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	df = dataframe
	# Adding in color-coded scatterplot to the grid
	ax.scatter(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2], c = df.iloc[:, 3], s = 50, cmap = 'viridis') #Fun fact! With df.iloc[:, n] where n is an index, you can access any column in a dataframe using an index.  No need to know the names of the columns!
	ax.view_init(z_elevation, xy_azimuth)
	plt.show()

def plot_3dcluster_360(dataframe, z_elevation):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    df = dataframe
	# Adding in color-coded scatterplot to the grid
    ax.scatter(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2], c = df.iloc[:, 3], s = 50, cmap = 'viridis')
    for angle in range(0, 360):
        ax.view_init(z_elevation, angle)
        plt.draw()
        plt.pause(.001)

# plot combos
i = 0
combos_3 = itertools.combinations(range(len((joined)[0])), 3)
combos_3 = list(combos_3)
clustered_sets_3d = []
for combo_3 in combos_3:
    # FOR TESTING
    i += 1
    if i > 10:
        break

    array_3 = (joined)[:, combo_3]
    std_array_3 = StandardScaler().fit_transform(array_3[1:])
    std_df_3 = pd.DataFrame(std_array_3, columns=std_array_3[0])
    k_3, gapdf_3 = cluster.optimalK(std_df_3)
    clustered_3 = cluster.clusterKMeans(std_df_3, k_3)

    #plot_3dcluster(clustered_3[1])

    clustered_sets_3d.append(clustered_3)
    print("#############################")
    print()
    print("Finished 3D cluster " + str(i))
    print()
    print("#############################")

clustered_sets_3d.sort(key=lambda x: x[0])

print("Finished 3D clustering")

i = 0
combos_2 = itertools.combinations(range(len((joined)[0])), 2)
combos_2 = list(combos_2)
clustered_sets_2d = []
for combo_2 in combos_2:
    # FOR TESTING
    i += 1
    if i > 10:
        break

    array_2 = (joined)[:, combo_2]
    std_array_2 = StandardScaler().fit_transform(array_2[1:])
    std_df_2 = pd.DataFrame(std_array_2, columns=std_array_2[0])
    k_2, gapdf_2 = cluster.optimalK(std_df_2)
    clustered_2 = cluster.clusterKMeans(std_df_2, k_2)

    #plot_2dcluster(clustered_2[1])

    clustered_sets_2d.append(clustered_2)
    print("#############################")
    print()
    print("Finished 2D cluster " + str(i))
    print()
    print("#############################")

clustered_sets_2d.sort(key=lambda x: x[0])

print("Finished 2D clustering")

i = 0
for cluster in clustered_sets_3d:
    i+=1
    if i > 5: break
    plot_3dcluster(cluster[1])

i = 0
for cluster in clustered_sets_2d:
    i+=1
    if i > 5: break
    plot_2dcluster(cluster[1])