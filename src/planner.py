import sklearn.cluster
import sklearn.metrics


def cluster(points, k=None):
    return sklearn.cluster.KMeans(n_clusters=k).fit(points)

