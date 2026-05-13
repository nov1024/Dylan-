import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# 读取csv文件数据
# path ='./iris/iris.data'
path = 'iris.data'
# data =pd.read_csv(path)

# 改进:强制指定列名(不管文件是否有表头)
columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
data = pd.read_csv(path, header=None, names=columns)

# 验证列名是否正确
print("数据列名:", data.columns.tolist())  # 应该输出['sepal_length','sepal_width','petal_length','petal_width','species']
print("类别列唯一值:", data['species'].unique())  # 查看类别名称格式
print('数据量为:', len(data))
print(data.head())
print(data)
print('空值数量如下:')
print(data.isnull().sum())
print("各列数据数值分布为")

# 定义类别标签为二分类:virginica为1,其他类别为0
data['species'] = data['species'].apply(lambda x: 1 if x == 'Iris-virginica' else 0)
print(data)

# 统计species列中0和1的数量
counts = data['species'].value_counts()
print("非virginica的数量:", counts[0])
print("virginica的数量:", counts[1])

# 划分样本,7:3
train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)

# print("训练集数据量{}".format((len(train_data))))
#
col = train_data.shape[1]  # 求出表格的总列数col
X = train_data.iloc[:, 0:col - 1].values
y = train_data.iloc[:, col - 1:col].values
X_test = test_data.iloc[:, 0:col - 1].values
y_test = test_data.iloc[:, col - 1:col].values

# m为训练集的行数
m = X.shape[0]

# n为测试集行数
n = X_test.shape[0]

# print("X矩阵为")
# print(X)
# print("\ny矩阵为")
# print(y)

'''
#将X,y分到的数据值转为矩阵类型,便于后续的计算
X =np.matrix(X.values)
y=np.matrix(y.values)
X_test =np.matrix(X_test.values)
y_test=np.matrix(y_test.values)
'''

'''
print("X矩阵为")
# print(X)
print("\ny矩阵为")
# print(y)
'''

# 转置
y = y.T
y_test = y_test.T

# 梯度下降
# 添加偏置项
X = np.c_[np.ones(m), X]  # 第一列加1
X_test = np.c_[np.ones(n), X_test]

# 初始化参数
# theta =np.zeros((X.shape[1],1))#创建一个列向量
theta = (np.matrix([0, 0, 0, 0, 0])).T

# print("theta的形状为{}".format(theta.shape))

alpha = 0.01
iter = 1000

# 定义Sigmoid函数、损失函数和梯度下降
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def compute_cost(X, y, theta):
    m_2 = len(y)
    predictions = sigmoid(X @ theta)
    cost = -1 / m_2 * np.sum(y * np.log(predictions) + (1 - y) * np.log(1 - predictions))
    return cost

y = y.reshape(-1, 1)

# print("y的形状为{}".format(y.shape))
# print("X

# 梯度上升函数
def gradient_boost(theta, alpha):
    for i in range(iter):
        theta = theta + (alpha / m) * (X.T @ (y - sigmoid(X @ theta)))
    return theta

# #求解θ
theta = gradient_boost(theta, alpha)

# print("theta的形状为{}".format(theta.shape))
# print("X_test的形状为{}".format(X_test.shape))

# 计算准确率
pred = sigmoid(X_test @ theta)
correct_num = 0

# 将pred和y_test展平为一维数组
# pred =pred.reshape(-1)
# print("*pred的形状为{}".format(pred.shape))
# print(pred)
# print("*y_test

# 将预测值转换为类别标签(0或1)
pred_class = (pred >= 0.5).astype(int)

# print("预测序列为\n{}".format(pred_class))
#
# #计算准确率
correct_num = np.sum(pred_class.flatten() == y_test)  # 逐元素比较并求和
print("正确预测个数为{}个,总个数有{}个".format(correct_num, n))
rate = float(correct_num) / n  # 准确率=正确分类的数量/总样本数量

# #将预测结果与实际结果进行比较
TP = np.sum((pred_class.flatten() == 1) & (y_test == 1))
FP = np.sum((pred_class.flatten() == 1) & (y_test == 0))
FN = np.sum((pred_class.flatten() == 0) & (y_test == 1))
TN = np.sum((pred_class.flatten() == 0) & (y_test == 0))
print("TP为{}".format(TP))
print("FP为{}".format(FP))
print("FN为{}".format(FN))
print("TN为{}".format(TN))

# 计算Precision和Recall,以及accuarcy
precision = TP / (TP + FP)
recall = TP / (TP + FN)
accuracy = (TP + TN) / (TP + TN + FP + FN)

# 计算F1-score
f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1_score)
print("accuracy:", accuracy)

print("---" * 20)

# 朴素贝叶斯
# 计算每个类别的先验概率
v_prior = np.mean(y)  # Virginica的先验概率
nv_prior = 1 - v_prior  # 非Virginica的先验概率
y = y.flatten()

# 计算每个特征的均值和标准差
mean_v = X[:, 1:][y == 1].mean(axis=0)
std_v = X[:, 1:][y == 1].std(axis=0)
mean_nv = X[:, 1:][y == 0].mean(axis=0)
std_nv = X[:, 1:][y == 0].std(axis=0)

# 高斯分布概率密度函数
def gaussian_prob(x, mean, std):
    return (1 / (np.sqrt(2 * np.pi) * std)) * np.exp(-0.5 * ((x - mean) / std) ** 2)

# 预测函数
def predict(X):
    predictions = []
    for x in X:
        # 计算每个特征在Virginica类别下的条件概率
        prob_v = np.prod(gaussian_prob(x, mean_v, std_v)) * v_prior
        # 计算每个特征在非Virginica类别下的条件概率
        prob_nv = np.prod(gaussian_prob(x, mean_nv, std_nv)) * nv_prior
        # 比较两个类别的概率,取概率大的类别
        predictions.append(1 if prob_v > prob_nv else 0)
    return predictions

# 在测试集上预测
pred = predict(X_test[:, 1:])
y_test = y_test.flatten()

print("原始真值序列为")
print(y_test)
print("预测序列为")
print(pred)

# 计算准确率
correct_num = np.sum(pred == y_test)  # 逐元素比较并求和
print("正确预测个数为{}个,总个数有{}个".format(correct_num, n))
rate = float(correct_num) / n  # 准确率=正确分类的数量/总样本数量

# 将预测结果与实际结果进行比较
TP = np.sum((pred == 1) & (y_test == 1))
FP = np.sum((pred == 1) & (y_test == 0))
FN = np.sum((pred == 0) & (y_test == 1))
TN = np.sum((pred == 0) & (y_test == 0))
print("TP为{}".format(TP))
print("FP为{}".format(FP))
print("FN为{}".format(FN))
print("TN为{}".format(TN))

# 计算Precision和Recall,以及accuarcy
precision = TP / (TP + FP)
recall = TP / (TP + FN)
accuracy = (TP + TN) / (TP + TN + FP + FN)

# 计算F1-score
f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1_score)
print("accuracy:", accuracy)