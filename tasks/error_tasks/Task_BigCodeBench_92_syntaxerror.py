import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def task_func(data, n_clusters):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input 'data' must be a pandas DataFrame.")
    if not isinstance(n_clusters, int) or n_clusters <= 1:
        raise ValueError("'n_clusters' must be an integer greater than 1.")

    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(data)
    centroids = kmeans.cluster_centers_

    fig, ax = plt.subplots()
    ax.scatter(data.iloc[:, 0], data.iloc[:, 1], c=labels, cmap='viridis', alpha=0.6, label='Data points')
    ax.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=200, c='red', label='Centroids'
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')
    ax.set_title('K-Means Clustering')
    ax.legend()

    return labels, ax

