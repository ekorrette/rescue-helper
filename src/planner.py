import sklearn.cluster
import sklearn.metrics


def cluster(points, k=None):
    return sklearn.cluster.KMeans(n_clusters=min(k, len(points))).fit(points)

