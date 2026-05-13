import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from scipy.stats import multivariate_normal
from sklearn import preprocessing

# ========================== K-Means 聚类算法 ==========================

# 加载数据集（修改路径为同级目录）
iris_data = pd.read_csv("iris.data", header=None,
                        names=['sepal length', 'sepal width', 'petal length', 'petal width', 'class'])
print(iris_data.info())

# 发现有iris-setosa iris-versicolor iris-virginica三种
print(iris_data['class'].value_counts())

# 对labels进行标签编码
labels = iris_data['class'].values
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(labels)

# 挑选sepal length、petal length两维特征作为聚类依据
x_axis = iris_data['sepal length']
y_axis = iris_data['petal length']
print(x_axis.shape)
print(y_axis.shape)

# 随机三个index值，在150条数据集中随机选中三个种类的开始点的标号
indexList = random.sample(range(0, 150), 3)
print(indexList)

# 随机初始的中心点
x_center1 = x_axis[indexList[0]]
y_center1 = y_axis[indexList[0]]
x_center2 = x_axis[indexList[1]]
y_center2 = y_axis[indexList[1]]
x_center3 = x_axis[indexList[2]]
y_center3 = y_axis[indexList[2]]

print(x_center1)
print(x_axis[0])

# ---------------------开始训练，训练100次
for i in range(100):
    # 用来装分属于三类的数据的index值
    belong1 = []
    belong2 = []
    belong3 = []

    # 计算每条分数据别到3个聚类中心的距离
    for j in range(150):
        belong = 0  # belong用来记录该条数据属于的类别
        dis_1 = pow((x_axis[j] - x_center1), 2) + pow((y_axis[j] - y_center1), 2)
        dis_2 = pow((x_axis[j] - x_center2), 2) + pow((y_axis[j] - y_center2), 2)
        dis_3 = pow((x_axis[j] - x_center3), 2) + pow((y_axis[j] - y_center3), 2)

        # 比较离三类中心点哪个更近，将该条数据归于距离更近的中心点所属类
        if dis_2 < dis_1:
            belong = 2
            if dis_3 < dis_2:
                belong = 3
        else:
            belong = 1
            if dis_3 < dis_1:
                belong = 3

        if belong == 1:
            belong1.append(j)
        elif belong == 2:
            belong2.append(j)
        else:
            belong3.append(j)

    # 进行center点的位置更新
    for k in range(len(belong1)):
        x_center1 += x_axis[belong1[k]]
        y_center1 += y_axis[belong1[k]]
    for k in range(len(belong2)):
        x_center2 += x_axis[belong2[k]]
        y_center2 += y_axis[belong2[k]]
    for k in range(len(belong3)):
        x_center3 += x_axis[belong3[k]]
        y_center3 += y_axis[belong3[k]]

    x_center1 = x_center1 / (1 + len(belong1))
    x_center2 = x_center2 / (1 + len(belong2))
    x_center3 = x_center3 / (1 + len(belong3))
    y_center1 = y_center1 / (1 + len(belong1))
    y_center2 = y_center2 / (1 + len(belong2))
    y_center3 = y_center3 / (1 + len(belong3))

# y_pred用来装k-means聚类算法对每条数据所归到的类
y_pred = np.array(np.zeros(150))
for i in range(len(belong1)):
    y_pred[belong1[i]] = 1
for i in range(len(belong2)):
    y_pred[belong2[i]] = 2
for i in range(len(belong3)):
    y_pred[belong3[i]] = 3

# k-means求出的聚类中心
x_center = [x_center1, x_center2, x_center3]
y_center = [y_center1, y_center2, y_center3]

# 数据集的实际中心
x_ac_center = [x_axis[0:50].mean(), x_axis[50:100].mean(), x_axis[100:150].mean()]
y_ac_center = [y_axis[0:50].mean(), y_axis[50:100].mean(), y_axis[100:150].mean()]

# 画图 - 聚类算法的归类情况
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.scatter(x_axis, y_axis, c=y_pred)
plt.scatter(x_center, y_center, c='r', marker='x')
plt.title('K-Means Clustering')
plt.xlabel('sepal length')
plt.ylabel('petal length')

# 实际数据的归类情况
plt.subplot(1, 2, 2)
plt.scatter(x_axis, y_axis, c=labels)
plt.scatter(x_ac_center, y_ac_center, c='r', marker='x')
plt.title('Actual Classes')
plt.xlabel('sepal length')
plt.ylabel('petal length')
plt.tight_layout()
plt.show()

# 计算准确率
y_pred_1 = np.array(np.zeros(150))
y_pred_2 = np.array(np.zeros(150))
y_pred_3 = np.array(np.zeros(150))
y_pred_4 = np.array(np.zeros(150))
y_pred_5 = np.array(np.zeros(150))
y_pred_6 = np.array(np.zeros(150))

for i in range(150):
    if y_pred[i] == 1:
        y_pred_1[i] = 0
        y_pred_2[i] = 1
        y_pred_3[i] = 0
        y_pred_4[i] = 1
        y_pred_5[i] = 2
        y_pred_6[i] = 2
    if y_pred[i] == 2:
        y_pred_1[i] = 1
        y_pred_2[i] = 0
        y_pred_3[i] = 2
        y_pred_4[i] = 2
        y_pred_5[i] = 1
        y_pred_6[i] = 0
    if y_pred[i] == 3:
        y_pred_1[i] = 2
        y_pred_2[i] = 2
        y_pred_3[i] = 1
        y_pred_4[i] = 0
        y_pred_5[i] = 0
        y_pred_6[i] = 1


def correct_rate(lei_list):
    correct_num = 0
    for i in range(150):
        if (lei_list[i] == labels[i]):
            correct_num += 1
    rate = correct_num / 150
    return rate


rate1 = correct_rate(y_pred_1)
rate2 = correct_rate(y_pred_2)
rate3 = correct_rate(y_pred_3)
rate4 = correct_rate(y_pred_4)
rate5 = correct_rate(y_pred_5)
rate6 = correct_rate(y_pred_6)

rate = [rate1, rate2, rate3, rate4, rate5, rate6]
max_rate = 0
for i in range(6):
    if rate[i] > max_rate:
        max_rate = rate[i]

print('K-Means准确率为:', max_rate)


# ========================== 混合高斯聚类（GMM）算法 ==========================

class GMM_EM():
    def __init__(self, n_components, max_iter=1000, error=1e-6):
        self.n_components = n_components
        self.max_iter = max_iter
        self.error = error
        self.samples = 0
        self.features = 0
        self.alpha = []
        self.mu = []
        self.sigma = []

    def _init(self, data):
        np.random.seed(4)
        self.mu = np.array(np.random.rand(self.n_components, self.features))
        self.sigma = np.array([np.eye(self.features) / self.features] * self.n_components)
        self.alpha = np.array([1.0 / self.n_components] * self.n_components)
        print(self.alpha.shape, self.mu.shape, self.sigma.shape)
        print(self.alpha, self.mu, self.sigma)

    def gauss(self, Y, mu, sigma):
        return multivariate_normal.pdf(Y, mean=mu, cov=sigma)

    def preprocess(self, data):
        self.samples = data.shape[0]
        self.features = data.shape[1]
        pre = preprocessing.MinMaxScaler()
        return pre.fit_transform(data)

    def fit_predict(self, data):
        data = self.preprocess(data)
        self._init(data)
        weighted_probs = np.zeros((self.samples, self.n_components))
        print(weighted_probs.shape)

        for i in range(self.max_iter):
            prev_weighted_probs = weighted_probs
            weighted_probs = self._e_step(data)
            change = np.linalg.norm(weighted_probs - prev_weighted_probs)
            if change < self.error:
                break
            self._m_step(data, weighted_probs)

        return weighted_probs.argmax(axis=1)

    def _e_step(self, data):
        probs = np.zeros((self.samples, self.n_components))
        for i in range(self.n_components):
            probs[:, i] = self.gauss(data, self.mu[i, :], self.sigma[i, :, :])

        weighted_probs = np.zeros(probs.shape)
        for i in range(self.n_components):
            weighted_probs[:, i] = self.alpha[i] * probs[:, i]

        for i in range(self.samples):
            weighted_probs[i, :] /= np.sum(weighted_probs[i, :])

        return weighted_probs

    def _m_step(self, data, weighted_probs):
        for i in range(self.n_components):
            sum_probs_i = np.sum(weighted_probs[:, i])
            # ========== 修改：np.mat 改为 np.asmatrix ==========
            self.mu[i, :] = np.sum(np.multiply(data, np.asmatrix(weighted_probs[:, i]).T), axis=0) / sum_probs_i
            self.sigma[i, :, :] = (data - self.mu[i, :]).T * np.multiply((data - self.mu[i, :]), np.asmatrix(
                weighted_probs[:, i]).T) / sum_probs_i
            self.alpha[i] = sum_probs_i / data.shape[0]


# 重新加载数据用于GMM（修改路径为同级目录）
iris_data = pd.read_csv("iris.data", header=None,
                        names=['sepal length', 'sepal width', 'petal length', 'petal width', 'class'])

# 对labels进行标签编码
labels = iris_data['class'].values
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(labels)

# 挑选sepal length、petal length两维特征作为聚类依据
x_axis = iris_data['sepal length']
y_axis = iris_data['petal length']

data = np.array(pd.concat([x_axis, y_axis], axis=1))

gmm = GMM_EM(3)
pre_label = gmm.fit_predict(data)
print(pre_label)
print(labels)

# 混合高斯算法求出的聚类中心
num_0, num_1, num_2 = [0, 0, 0]
xsum_0, xsum_1, xsum_2 = [0, 0, 0]
ysum_0, ysum_1, ysum_2 = [0, 0, 0]

for i in range(len(pre_label)):
    if pre_label[i] == 0:
        num_0 += 1
        xsum_0 += x_axis[i]
        ysum_0 += y_axis[i]
    elif pre_label[i] == 1:
        num_1 += 1
        xsum_1 += x_axis[i]
        ysum_1 += y_axis[i]
    else:
        num_2 += 1
        xsum_2 += x_axis[i]
        ysum_2 += y_axis[i]

x_center_0 = xsum_0 / num_0
y_center_0 = ysum_0 / num_0
x_center_1 = xsum_1 / num_1
y_center_1 = ysum_1 / num_1
x_center_2 = xsum_2 / num_2
y_center_2 = ysum_2 / num_2

x_center = [x_center_0, x_center_1, x_center_2]
y_center = [y_center_0, y_center_1, y_center_2]

# 数据集的实际中心
x_ac_center = [x_axis[0:50].mean(), x_axis[50:100].mean(), x_axis[100:150].mean()]
y_ac_center = [y_axis[0:50].mean(), y_axis[50:100].mean(), y_axis[100:150].mean()]

# 画混合高斯聚类图
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.scatter(x_axis, y_axis, c=pre_label)
plt.scatter(x_center, y_center, c='r', marker='x')
plt.title('GMM Clustering')
plt.xlabel('sepal length')
plt.ylabel('petal length')

# 实际数据图
plt.subplot(1, 2, 2)
plt.scatter(x_axis, y_axis, c=labels)
plt.scatter(x_ac_center, y_ac_center, c='r', marker='x')
plt.title('Actual Classes')
plt.xlabel('sepal length')
plt.ylabel('petal length')
plt.tight_layout()
plt.show()

# 计算准确率
y_pred_1 = np.array(np.zeros(150))
y_pred_2 = np.array(np.zeros(150))
y_pred_3 = np.array(np.zeros(150))
y_pred_4 = np.array(np.zeros(150))
y_pred_5 = np.array(np.zeros(150))
y_pred_6 = np.array(np.zeros(150))

for i in range(150):
    if pre_label[i] == 0:
        y_pred_1[i] = 0
        y_pred_2[i] = 1
        y_pred_3[i] = 0
        y_pred_4[i] = 1
        y_pred_5[i] = 2
        y_pred_6[i] = 2
    if pre_label[i] == 1:
        y_pred_1[i] = 1
        y_pred_2[i] = 0
        y_pred_3[i] = 2
        y_pred_4[i] = 2
        y_pred_5[i] = 1
        y_pred_6[i] = 0
    if pre_label[i] == 2:
        y_pred_1[i] = 2
        y_pred_2[i] = 2
        y_pred_3[i] = 1
        y_pred_4[i] = 0
        y_pred_5[i] = 0
        y_pred_6[i] = 1


def correct_rate(lei_list):
    correct_num = 0
    for i in range(150):
        if (lei_list[i] == labels[i]):
            correct_num += 1
    rate = correct_num / 150
    return rate


rate1 = correct_rate(y_pred_1)
rate2 = correct_rate(y_pred_2)
rate3 = correct_rate(y_pred_3)
rate4 = correct_rate(y_pred_4)
rate5 = correct_rate(y_pred_5)
rate6 = correct_rate(y_pred_6)

rate = [rate1, rate2, rate3, rate4, rate5, rate6]
max_rate = 0
for i in range(6):
    if rate[i] > max_rate:
        max_rate = rate[i]

print('GMM准确率为:', max_rate)