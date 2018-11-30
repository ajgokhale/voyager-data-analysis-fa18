from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sns

# PCA for data frames class
class PCADF:
    def __init__(self, ind_df):
        self.std_df = StandardScaler().fit_transform(ind_df) # must standardize before you do PCA

    def visualize_pca(self): # only supports 2D and 3D PCA
        pca = PCA(n_components=2)
        projected = pca.fit_transform(self.std_df)
        plt.scatter(projected[:, 0], projected[:, 1], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('spectral', 10))
        plt.xlabel('component 1')
        plt.ylabel('component 2')
        return projected # returns a dataframe with the principal components
    
    def general_pca(self, confidence): # PCA based on how much variation in the data at the minimum should be captured
        pca = PCA(confidence)
        trans_df = pca.transform(self.std_df)
        return trans_df

    def general_pca_num_components(self, confidence):
        pca = PCA(confidence)
        principal_comp = pca.fit_transform(self.std_df)
        num_comp = pca.n_components_
        return num_comp

# data frames
ind_df = None # whatever dataframe you want to run PCA on (remember to only have independent variables, not depenedent variables in here)
dep_df = None # whatever dataframe that contains the dependent variable, IMPORTANT: column name should be pcd

# instantiate the PCA object
pca_obj = PCADF(ind_df)

# PCA in 2D
principal_2d_df = pca_obj.visualize_pca(2)

# return number of componenets needed for 95% of the variation in PCA to be accounted for
num_comp = pca_obj.general_pca_num_components(0.95)

# transform dataframe to the one with principal components (no need for u, s, and v matrices)
trans_df = pca_obj.general_pca(0.95)

# run ols on the trans_df and dep_df