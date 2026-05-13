import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

data = pd.read_csv('housing.csv')
# print(data)

pd.set_option('display.max_columns', None)  # 设置不折叠数据
pd.set_option('display.max_rows', None)

# 检查数据结构
# print(data)
print(data.info())
print(data['ocean_proximity'].value_counts())

# 将ocean_proximity转换为独热编码
data_1 = pd.get_dummies(data, columns=['ocean_proximity'], prefix='ocean', dtype=int)
# 检查转换后的数据
# print(data_1)

data_1 = data_1.dropna(axis=0, subset=["total_bedrooms"])

tmp = data_1.drop('median_house_value', axis=1)
y = data_1['median_house_value']
data_2 = pd.concat([tmp, y], axis=1)
print(data_2.shape)
# print(data_2)

# 划分训练集和测试集
train_data, test_data = train_test_split(data_2, test_size=0.2, random_state=42)

# print("训练集")
# print(train_data)
# print("测试集")
# print(test_data)

# 将训练集中的数据取出
n = train_data.shape[1]  # 求出表格的总列数n
# 将median_house_value单独分出给y，剩余数据给X
X = train_data.iloc[:, 0:n - 1]
y = train_data.iloc[:, n - 1:n]
X_test = test_data.iloc[:, 0:n-1]
y_test = test_data.iloc[:, n -1:n]

# print("X矩阵为")
# print(X)
# print("\ny矩阵为")
# print(y)

# 将X,y分到的数据值转为矩阵类型，便于后续的计算
X = np.matrix(X.values)
y = np.matrix(y.values)
X_test = np.matrix(X_test.values)
y_test = np.matrix(y_test.values)

# print("X矩阵为")
# print(X)
# print("\ny矩阵为")
# print(y)
# print("X的形状为{}".format(X.shape))
# print("y的形状为{}".format(y.shape))

# 定义归一化函数
def norm(X):
    sigma = np.std(X, axis=0)  # axis=0计算每一列的标准差，=1计算行的
    miu = np.mean(X, axis=0)
    X = (X - miu) / sigma
    return X

X = norm(X)
X_test = norm(X_test)

X = np.c_[np.ones(y.size), X]  # 矩阵合并，第一列为1
X_test = np.c_[np.ones(y_test.size), X_test]

# print("缩放后的X为\n{}".format(X))
# print("\n缩放后的X_test为\n{}".format(X_test))
# print("X的形状为{}".format(X.shape))
# print("X_test的形状为{}".format(X_test.shape))

# 初始化theta的值（theta用于梯度下降中）
theta = (np.matrix([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])).T
theta_2 = theta

num_iteration = 20000  # 初始化迭代次数
alpha = 0.005  # 初始化学习速率

# 初始化一个一维向量用于存放每次迭代的代价值
J = np.zeros(num_iteration)

# 定义代价函数
def cost(theta, X=X, y=y, n=y.size):
    h_x = X @ theta
    inner = np.sum(np.power(h_x - y, 2))
    return inner / (2 * n)

# 梯度下降函数
def gradient_descent(theta, alpha):
    for i in range(num_iteration):
        J[i] = cost(theta, X)  # 将每次迭代的代价函数值计入
        theta = theta - (alpha / y.size) * (X.T @ (X @ theta - y))
    return theta

# 求解theta
theta = gradient_descent(theta, alpha)

# print("学习率为{}".format(alpha))
# print("求得的theta为\n{}".format(theta))

# 图形表示迭代过程中代价函数的变化
plt.figure(0)
plt.plot(J)  # 打印代价函数-迭代次数图
plt.xlabel('steps')
plt.ylabel('loss')
plt.title('LinearRegression')
plt.show()

# R^2函数
def R_2(X_test, y_test, theta):
    y_pred = X_test * theta
    mu = np.mean(y_test, axis=0)
    SSE = np.sum(np.power(y_test - y_pred, 2))
    SSR = np.sum(np.power(y_pred - mu, 2))
    SST = SSR + SSE
    r_2 = 1 - SSE / SST
    return r_2

# 测试集上梯度下降的R2
print("测试集上梯度下降的R2：")
print(R_2(X_test, y_test, theta))
print("训练集上梯度下降的R2：")
print(R_2(X, y, theta))

# 定义正规方程函数
def NormalEquation(theta_2):
    theta_2 = np.linalg.inv(X.T @ X) @ X.T @ y  # 求矩阵的逆
    return theta_2

theta_2 = NormalEquation(theta_2)
print("求得的theta为\n{}".format(theta_2))

print("测试集上正规方程的R2：")
print(R_2(X_test, y_test, theta_2))

# 特征相关性分析
temp = data_1.copy()
corr = temp.corr()
score = corr['median_house_value'].sort_values()
print(score)
