import numpy as np
from scipy.spatial.distance import cdist
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

THRESHOLD = 0

def elbowPlot(df):
	# Functions that takes in a dataframe and returns elbow plot 
	# Kink in elbow plot is optimal amount of N clusters
    x = df.data
    res = list()
    n_cluster = range(2,20)
    
    for n in n_cluster:
        kmeans = KMeans(n_clusters = cn)
        kmeans.fit(x)
        res.append(np.average(np.min(cdist(x, kmeans.cluster_centers_, 'euclidean'), axis=1)))

    plt.plot(n_cluster, res)
    plt.title('elbow curve')
    
    return plt.show()

# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.normalize.html 
# Normalize data using scikit import 

def clusterKMeans(df, N):
    #turn df into np.array
    points = df.values
    # create kmeans object
    kmeans = KMeans(n_clusters=N)
    # fit kmeans object to data
    kmeans.fit(points)
    # print location of clusters learned by kmeans object
    cluster_location = kmeans.cluster_centers_
    # save new clusters for chart - Assigns to every point what cluster it is in
    y_km = kmeans.fit_predict(points)
    df.data['cluster'] = y_km
    
    return df

def validateCluster(something):
    # Function that validates the given clustering, returns True if the cluster should be
    # considered

    return True

def plotCluster(df):
    # Takes in a 2D or 3D dataframe of customer metrics and associated clusters,
    # and plots these points with color coded clusters
