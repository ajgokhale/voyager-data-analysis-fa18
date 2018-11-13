import numpy as np
import scipy as sp
import pandas as pd
import sklearn.cluster as cl
import math

THRESHOLD = 0

def clusterKMeans(df):
    # Function that takes in a dataframe containing the summary metrics for a customer,
    # and returns a new dataframe with an additional column specifying the customer's
    # cluster (from 0 to n)

    # The cluster should also be validated using internal validation techniques (see validateCluster)

    return None

def validateCluster(something):
    # Function that validates the given clustering

    return False

def plotCluster(df):
    # Takes in a 2D or 3D dataframe of customer metrics and associated clusters,
    # and plots these points with color coded clusters
