from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sns
import metrics
from mpl_toolkits.mplot3d import Axes3D
import math

# PCA for data frames class
class PCADF:
    def __init__(self, ind_df):
        self.std_df = ind_df

    def pca_2d(self): # only supports 2D and 3D PCA
        pca = PCA(n_components=2)
        pca.fit(self.std_df)
        projected = pd.DataFrame(pca.transform(self.std_df), columns=['PCA%i' % i for i in range(2)], index=self.std_df.index)
        return projected, pca
    
    def pca_3d(self): # only supports 2D and 3D PCA
        pca = PCA(n_components=3)
        pca.fit(self.std_df)
        projected = pd.DataFrame(pca.transform(self.std_df), columns=['PCA%i' % i for i in range(3)], index=self.std_df.index)
        return projected, pca

    def plot_2d_pca(self, result):
        # df = dataframe
        # Run the PCA 
        # pca = PCA(n_components=2)
        # pca.fit(df)

        # Store results of PCA in a data frame
        # result = pd.DataFrame(pca.transform(df), columns=['PCA%i' % i for i in range(2)], index=df.index)

        # Plot!
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(result['PCA0'], result['PCA1'], c = 'navy', s = 50)

        # Label Axes + Title : Set "PC1", "PC2", "PCA on the Data Set" to whatever
        # you want!

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title("PCA on the Data Set")

        # Insert any design modifications here!

        plt.show()

    def plot_3d_pca(self, result, z_elevation=30, xy_azimuth=150):
        # df = dataframe
        # Run The PCA
        # pca = PCA(n_components=3)
        # pca.fit(df)
    
        # Store results of PCA in a data frame
        # result = pd.DataFrame(pca.transform(df), columns=['PCA%i' % i for i in range(3)], index=df.index)
    
        # Plot initialisation
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # Add in a scatterplot to the grid: set c to whatever color you want!
        ax.scatter(result['PCA0'], result['PCA1'], result['PCA2'], c = 'navy', s = 50)

    
        # make simple, bare axis lines through space.  If YOU DON'T WANT AXES lines, 
        # comment out lines 29-34
        xAxisLine = ((min(result['PCA0']), max(result['PCA0'])), (0, 0), (0,0))
        ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r')
        yAxisLine = ((0, 0), (min(result['PCA1']), max(result['PCA1'])), (0,0))
        ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r')
        zAxisLine = ((0, 0), (0,0), (min(result['PCA2']), max(result['PCA2'])))
        ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r')
    
        # Label the axes.  Set "PC1", "PC2", "PC3", and "PCA on the iris data set" 
        # to whatever you want!  They will represent the axes labels and the title"  

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_zlabel("PC3")
        ax.set_title("PCA on the Data Set")
        ax.view_init(z_elevation, xy_azimuth)
        plt.show()

    def plot_3d_pca_360_animation(self, result, z_elevation=30):
        
        # df = dataframe
        # Run The PCA
        # pca = PCA(n_components=3)
        # pca.fit(df)
    
        # Store results of PCA in a data frame
        # result = pd.DataFrame(pca.transform(df), columns=['PCA%i' % i for i in range(3)], index=df.index)
    
        # Plot initialisation
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # Add in a scatterplot to the grid: set c to whatever color you want!
        ax.scatter(result['PCA0'], result['PCA1'], result['PCA2'], c = 'navy', s = 50)

    
        # make simple, bare axis lines through space.  If YOU DON'T WANT AXES lines, 
        # comment out lines 29-34
        xAxisLine = ((min(result['PCA0']), max(result['PCA0'])), (0, 0), (0,0))
        ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r')
        yAxisLine = ((0, 0), (min(result['PCA1']), max(result['PCA1'])), (0,0))
        ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r')
        zAxisLine = ((0, 0), (0,0), (min(result['PCA2']), max(result['PCA2'])))
        ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r')
    
        # Label the axes.  Set "PC1", "PC2", "PC3", and "PCA on the iris data set" 
        # to whatever you want!  They will represent the axes labels and the title"  

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_zlabel("PC3")
        ax.set_title("PCA on the Data Set")

        for angle in range(0, 360):
            ax.view_init(z_elevation, angle)
            plt.draw()
            plt.pause(.001)

################# PARAMETERS ####################

# IMPORTANT: values for regression's start and end times (format: [M]M/[D]D/YYYY)
start_time_ind, end_time_ind, start_time_dep, end_time_dep = \
    "1/1/2005", "1/1/2015", "1/1/2015", "1/1/2019"
allow_single = True

#################################################

x, y = read_data.customer_df(start_time_ind, end_time_ind, start_time_dep, end_time_dep,
    allow_single)

# data frames
ind_df = pd.DataFrame(x, columns=metrics.Customer.metric_names[:len(metrics.Customer.metric_names)-2])

# instantiate the PCA object
pca_obj = PCADF(ind_df)

# PCA in 2D
df2d, pca2d = pca_obj.pca_2d()
pca_obj.plot_2d_pca(df2d)

# PCA in 3D
df3d, pca3d = pca_obj.pca_3d()
pca_obj.plot_3d_pca_360_animation(df3d, 30)

# return number of componenets needed for 95% of the variation in PCA to be accounted for
num_comp = pca_obj.general_pca_num_components(0.95)

# transform dataframe to the one with principal components (no need for u, s, and v matrices)
trans_df = pca_obj.general_pca(0.95)