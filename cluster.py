import numpy as np
import pandas as pd
import math
from scipy.spatial.distance import cdist
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import time
import hashlib
import scipy
from sklearn.datasets.samples_generator import make_blobs


# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.normalize.html 
# Normalize data: pre-processing 

def optimalK(data, nrefs=3, maxClusters=10):
    # Determines optimal amount of clusters using gap statistic
    # https://anaconda.org/milesgranger/gap-statistic/notebook

    gaps = np.zeros((len(range(1, maxClusters+1)),))
    resultsdf = pd.DataFrame({'clusterCount':[], 'gap':[]})
    for gap_index, k in enumerate(range(1, maxClusters+1)):
        # Holder for reference dispersion results
        refDisps = np.zeros(nrefs)
        # For n references, generate random sample and perform kmeans getting resulting dispersion of each loop
        for i in range(nrefs):
            # Create new random reference set
            randomReference = np.random.random_sample(size=data.shape)
            # Fit to it
            km = KMeans(k)
            km.fit(randomReference)
            refDisp = km.inertia_
            refDisps[i] = refDisp
        # Fit cluster to original data and create dispersion
        km = KMeans(k)
        km.fit(data)
        origDisp = km.inertia_
        # Calculate gap statistic
        gap = np.log(np.mean(refDisps)) - np.log(origDisp)
        # Assign this loop's gap statistic to gaps
        gaps[gap_index] = gap
        resultsdf = resultsdf.append({'clusterCount':k, 'gap':gap}, ignore_index=True)

    return (gaps.argmax() + 1, resultsdf)  # Plus 1 because index of 0 means 1 cluster is optimal, index 2 = 3 clusters are optimal

def clusterKMeans(df, k):
    #turn df into np.array
    points = df.values
    # create kmeans object
    kmeans = KMeans(n_clusters=k).fit(points)
    # save new clusters for chart - Assigns to every point what cluster it is in
    y_km = kmeans.fit_predict(points)
    # create a new dataframe 
    dataframe = pd.DataFrame(list(points), columns=df.columns)
    # append y_km to dataframe
    l = list(y_km)
    dataframe['Cluster'] = l 
    return kmeans.score(points), dataframe