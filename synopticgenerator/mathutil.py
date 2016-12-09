""" coding: utf-8 """
# 以下の論文で提案された改良 x-means法の実装
# クラスター数を自動決定する k-meansアルゴリズムの拡張について
# http://www.rd.dnc.ac.jp/~tunenori/doc/xmeans_euc.pdf
# の実装である
# http://web-salad.hateblo.jp/entry/2014/07/19/200347
# https://gist.github.com/yasaichi/254a060eff56a3b3b858
#
# をもとに scikit-learn KMeans ではなく OpenCV の kmeans を使用するように改変
#
##############################################################################

import numpy as np
from scipy import stats
import cv2


class XMeans:
    """
    x-means法を行うクラス
    """

    def __init__(self, k_init=2, **k_means_args):
        """
        k_init : The initial number of clusters applied to KMeans()
        """
        self.k_init = k_init
        self.k_means_args = k_means_args

    def fit(self, X):
        """
        x-means法を使ってデータXをクラスタリングする
        X : array-like or sparse matrix, shape=(n_samples, n_features)
        """
        self.clusters = []

        compactness, labels, centers = cv2.kmeans(
            data=X, K=self.k_init, bestLabels=None,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10),
            attempts=1, flags=cv2.KMEANS_RANDOM_CENTERS)

        clusters = self.Cluster.build(X, compactness, labels.flatten(), centers)

        self.__recursively_split(clusters)

        self.labels = np.empty(X.shape[0], dtype=np.intp)
        for i, c in enumerate(self.clusters):
            self.labels[c.index] = i

        self.cluster_centers = np.array([c.center for c in self.clusters])
        self.cluster_log_likelihoods = np.array([c.log_likelihood() for c in self.clusters])
        self.cluster_sizes = np.array([c.size for c in self.clusters])

        return self

    def __recursively_split(self, clusters):
        """
        引数のclustersを再帰的に分割する
        clusters : list-like object, which contains instances of 'XMeans.Cluster'
        """
        for cluster in clusters:
            if cluster.size <= 3:
                self.clusters.append(cluster)
                continue

            compactness, labels, centers = cv2.kmeans(
                data=cluster.data, K=2, bestLabels=None,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10),
                attempts=1, flags=cv2.KMEANS_RANDOM_CENTERS)

            c1, c2 = self.Cluster.build(cluster.data, compactness, labels.flatten(), centers, cluster.index)

            beta = np.linalg.norm(c1.center - c2.center) / np.sqrt(np.linalg.det(c1.cov) + np.linalg.det(c2.cov))
            alpha = 0.5 / stats.norm.cdf(beta)
            bic = -2 * (cluster.size * np.log(alpha) + c1.log_likelihood() + c2.log_likelihood()) + 2 * cluster.df * np.log(cluster.size)

            if bic < cluster.bic():
                self.__recursively_split([c1, c2])
            else:
                self.clusters.append(cluster)

    class Cluster:
        """
        k-means法によって生成されたクラスタに関する情報を持ち、尤度やBICの計算を行うクラス
        """

        @classmethod
        def build(cls, X, compactness, labels, centers, index=None):
            if index is None:
                index = np.array(range(0, X.shape[0]))
            indice = range(0, len(centers))
            # labels = range(0, k_means.get_params()["n_clusters"])

            return tuple(cls(X, index, compactness, labels, centers, i) for i in indice)

        # index: Xの各行におけるサンプルが元データの何行目のものかを示すベクトル
        def __init__(self, X, index, compactness, labels, centers, label):
            self.data = X[labels==label]
            self.index = index[labels==label]
            self.size = self.data.shape[0]
            self.df = self.data.shape[1] * (self.data.shape[1] + 3) / 2
            self.center = centers[label]
            self.cov = np.cov(self.data.T)

        def log_likelihood(self):
            try:
                return sum(stats.multivariate_normal.logpdf(x, self.center, self.cov) for x in self.data)
            except ValueError:
                return 0.
            except np.linalg.LinAlgError:
                return 0.

        def bic(self):
            return -2 * self.log_likelihood() + self.df * np.log(self.size)


'''
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # データの準備
    x = np.array([np.random.normal(loc, 0.1, 20) for loc in np.repeat([1,2], 2)]).flatten() #ランダムな80個の数を生成
    y = np.array([np.random.normal(loc, 0.1, 20) for loc in np.tile([1,2], 2)]).flatten() #ランダムな80個の数を生成

    # クラスタリングの実行
    x_means = XMeans(random_state=1).fit(np.c_[x,y])
    print(x_means.labels)
    print(x_means.cluster_centers)
    print(x_means.cluster_log_likelihoods)
    print(x_means.cluster_sizes)

    # 結果をプロット
    plt.rcParams["font.family"] = "Hiragino Kaku Gothic Pro"
    plt.scatter(x, y, c = x_means.labels, s = 30)
    plt.scatter(x_means.cluster_centers[:,0], x_means.cluster_centers[:,1], c = "r", marker = "+", s = 100)
    plt.xlim(0, 3)
    plt.ylim(0, 3)
    plt.title("x-means_test1")
    plt.legend()
    plt.grid()
    plt.show()
    # plt.savefig("clustering.png", dpi = 200)
'''
