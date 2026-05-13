import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler

# ============================================================
# 实验名称：基于K近邻(KNN)算法的手写数字识别实验
# 实验目的：通过手动实现KNN分类器，理解KNN算法原理，
#          掌握距离度量、K值选择对分类效果的影响
# ============================================================

# ========================== 1. 数据加载与探索 ==========================

# 加载手写数字数据集
data = pd.read_csv('digits.csv')

print("=" * 60)
print("手写数字数据集信息")
print("=" * 60)
print("数据集形状:", data.shape)
print("\n数据集列名:", data.columns.tolist()[:10], "... 共65列")
print("\n各数字样本数量:")
print(data['label'].value_counts().sort_index())
print("\n数据集前5行:")
print(data.head())

# 检查缺失值
print('\n空值数量:')
print(data.isnull().sum().sum())  # 总缺失值数量

# 基本统计信息
print("\n数据基本统计信息:")
print(data.describe())

# ========================== 2. 数据可视化 ==========================

# 展示每个数字的样例图像
fig, axes = plt.subplots(2, 5, figsize=(12, 6))
fig.suptitle('手写数字样例 (8x8像素)', fontsize=16, fontweight='bold')

for i in range(10):
    ax = axes[i // 5, i % 5]
    # 找到每个数字的第一个样本
    sample = data[data['label'] == i].iloc[0]
    # 提取64个像素值，重塑为8x8
    image = sample[:-1].values.reshape(8, 8)
    ax.imshow(image, cmap='gray')
    ax.set_title(f'数字: {i}', fontsize=14)
    ax.axis('off')

plt.tight_layout()
plt.savefig('sample_digits.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n已保存手写数字样例图像: sample_digits.png")

# ========================== 3. 数据预处理 ==========================

# 分离特征和标签
X = data.drop('label', axis=1).values
y = data['label'].values

print("\n特征矩阵形状:", X.shape)
print("标签向量形状:", y.shape)

# 数据归一化 (将像素值缩放到[0, 1]范围)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

print("\n归一化后特征范围:")
print("最小值:", X_scaled.min())
print("最大值:", X_scaled.max())

# 划分训练集和测试集 (7:3)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

print("\n训练集大小:", X_train.shape[0])
print("测试集大小:", X_test.shape[0])

# ========================== 4. 手动实现KNN算法 ==========================

print("\n" + "=" * 60)
print("手动实现KNN分类器")
print("=" * 60)

# 定义欧氏距离函数
def euclidean_distance(x1, x2):
    """
    计算两个样本之间的欧氏距离
    公式: sqrt(sum((x1 - x2)^2))
    """
    return np.sqrt(np.sum((x1 - x2) ** 2))

# 定义曼哈顿距离函数
def manhattan_distance(x1, x2):
    """
    计算两个样本之间的曼哈顿距离
    公式: sum(|x1 - x2|)
    """
    return np.sum(np.abs(x1 - x2))

# KNN分类器类
class KNNClassifier:
    """
    K近邻分类器 - 手动实现
    
    参数:
        k: 邻居数量
        distance_func: 距离度量函数 (默认欧氏距离)
    """
    def __init__(self, k=3, distance_func=euclidean_distance):
        self.k = k
        self.distance_func = distance_func
        self.X_train = None
        self.y_train = None
    
    def fit(self, X_train, y_train):
        """
        训练KNN模型 (KNN是惰性学习，只需存储训练数据)
        """
        self.X_train = X_train
        self.y_train = y_train
    
    def predict_single(self, x):
        """
        预测单个样本的类别
        """
        # 计算待预测样本与所有训练样本的距离
        distances = []
        for i in range(len(self.X_train)):
            dist = self.distance_func(x, self.X_train[i])
            distances.append((dist, self.y_train[i]))
        
        # 按距离升序排序，取前k个最近邻居
        distances.sort(key=lambda x: x[0])
        k_nearest = distances[:self.k]
        
        # 统计k个邻居中各类别的出现次数
        k_nearest_labels = [label for (_, label) in k_nearest]
        vote_result = Counter(k_nearest_labels)
        
        # 返回得票最多的类别
        return vote_result.most_common(1)[0][0]
    
    def predict(self, X_test):
        """
        预测多个样本的类别
        """
        predictions = []
        for i, x in enumerate(X_test):
            if i % 50 == 0:
                print(f"  已预测 {i}/{len(X_test)} 个样本...")
            pred = self.predict_single(x)
            predictions.append(pred)
        return np.array(predictions)


# ========================== 5. 不同K值的实验对比 ==========================

print("\n" + "=" * 60)
print("实验一：不同K值对分类效果的影响 (欧氏距离)")
print("=" * 60)

# 测试不同的K值
k_values = [1, 3, 5, 7, 9, 11, 15, 21]
k_results = []

for k in k_values:
    print(f"\n--- K = {k} ---")
    knn = KNNClassifier(k=k, distance_func=euclidean_distance)
    knn.fit(X_train, y_train)
    
    start_time = time.time()
    y_pred = knn.predict(X_test)
    elapsed = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    k_results.append({
        'K': k,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Time(s)': elapsed
    })
    
    print(f"准确率: {acc:.4f}")
    print(f"精确率: {prec:.4f}")
    print(f"召回率: {rec:.4f}")
    print(f"F1分数: {f1:.4f}")
    print(f"预测耗时: {elapsed:.2f}秒")

# 展示K值对比结果
k_df = pd.DataFrame(k_results)
print("\n不同K值的实验结果对比:")
print(k_df.to_string(index=False))

# 可视化K值与准确率的关系
plt.figure(figsize=(10, 6))
plt.plot(k_df['K'], k_df['Accuracy'], 'o-', color='#2E86AB', linewidth=2, markersize=8, label='准确率')
plt.plot(k_df['K'], k_df['Precision'], 's--', color='#A23B72', linewidth=2, markersize=8, label='精确率')
plt.plot(k_df['K'], k_df['Recall'], '^--', color='#F18F01', linewidth=2, markersize=8, label='召回率')
plt.plot(k_df['K'], k_df['F1-score'], 'd--', color='#C73E1D', linewidth=2, markersize=8, label='F1分数')
plt.xlabel('K值 (邻居数量)', fontsize=12)
plt.ylabel('评价指标', fontsize=12)
plt.title('不同K值对KNN分类效果的影响', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(k_values)
plt.tight_layout()
plt.savefig('k_value_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n已保存K值对比图: k_value_comparison.png")

# 找出最优K值
best_k = k_df.loc[k_df['Accuracy'].idxmax(), 'K']
print(f"\n最优K值为: {int(best_k)}")

# ========================== 6. 不同距离度量的对比 ==========================

print("\n" + "=" * 60)
print("实验二：不同距离度量的对比 (K=5)")
print("=" * 60)

distances = [
    ('欧氏距离', euclidean_distance),
    ('曼哈顿距离', manhattan_distance)
]

dist_results = []

for name, dist_func in distances:
    print(f"\n--- 距离度量: {name} ---")
    knn = KNNClassifier(k=5, distance_func=dist_func)
    knn.fit(X_train, y_train)
    
    start_time = time.time()
    y_pred = knn.predict(X_test)
    elapsed = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    dist_results.append({
        'Distance': name,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Time(s)': elapsed
    })
    
    print(f"准确率: {acc:.4f}")
    print(f"精确率: {prec:.4f}")
    print(f"召回率: {rec:.4f}")
    print(f"F1分数: {f1:.4f}")
    print(f"预测耗时: {elapsed:.2f}秒")

dist_df = pd.DataFrame(dist_results)
print("\n不同距离度量的实验结果对比:")
print(dist_df.to_string(index=False))

# ========================== 7. 最优模型的详细评估 ==========================

print("\n" + "=" * 60)
print("最优模型评估 (K=5, 欧氏距离)")
print("=" * 60)

best_knn = KNNClassifier(k=5, distance_func=euclidean_distance)
best_knn.fit(X_train, y_train)
y_pred_best = best_knn.predict(X_test)

# 计算混淆矩阵
cm = confusion_matrix(y_test, y_pred_best)
print("\n混淆矩阵:")
print(cm)

# 计算每个数字的精确率和召回率
print("\n各数字分类报告:")
for i in range(10):
    tp = cm[i, i]
    fp = cm[:, i].sum() - tp
    fn = cm[i, :].sum() - tp
    tn = cm.sum() - tp - fp - fn
    
    precision_i = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall_i = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_i = 2 * precision_i * recall_i / (precision_i + recall_i) if (precision_i + recall_i) > 0 else 0
    
    print(f"数字 {i}: 精确率={precision_i:.4f}, 召回率={recall_i:.4f}, F1={f1_i:.4f}")

# 可视化混淆矩阵
plt.figure(figsize=(10, 8))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('混淆矩阵 (K=5, 欧氏距离)', fontsize=14, fontweight='bold')
plt.colorbar()
tick_marks = np.arange(10)
plt.xticks(tick_marks, [str(i) for i in range(10)], fontsize=12)
plt.yticks(tick_marks, [str(i) for i in range(10)], fontsize=12)
plt.xlabel('预测标签', fontsize=12)
plt.ylabel('真实标签', fontsize=12)

# 在混淆矩阵中显示数值
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=10)

plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n已保存混淆矩阵图: confusion_matrix.png")

# 展示预测正确和错误的样例
print("\n" + "=" * 60)
print("预测样例展示")
print("=" * 60)

# 找出预测正确和错误的样本索引
correct_idx = np.where(y_pred_best == y_test)[0]
error_idx = np.where(y_pred_best != y_test)[0]

print(f"预测正确数量: {len(correct_idx)}")
print(f"预测错误数量: {len(error_idx)}")

# 展示一些预测错误的样例
if len(error_idx) > 0:
    n_errors = min(10, len(error_idx))
    fig, axes = plt.subplots(2, 5, figsize=(14, 6))
    fig.suptitle('预测错误样例 (真实标签 -> 预测标签)', fontsize=14, fontweight='bold')
    
    for i in range(n_errors):
        ax = axes[i // 5, i % 5]
        idx = error_idx[i]
        # 需要从原始X中找到对应的样本 (X_test是经过缩放的，需要找到原始数据)
        # 为了显示，我们使用归一化后的数据反向变换
        original_idx = np.where((X_scaled == X_test[idx]).all(axis=1))[0]
        if len(original_idx) > 0:
            image = X[original_idx[0]].reshape(8, 8)
        else:
            # 如果找不到原始数据，直接使用测试数据（已归一化）
            image = X_test[idx].reshape(8, 8)
        
        ax.imshow(image, cmap='gray')
        ax.set_title(f'{y_test[idx]} -> {y_pred_best[idx]}', fontsize=12, color='red')
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('prediction_errors.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\n已保存预测错误样例图: prediction_errors.png")

# ========================== 8. 与sklearn库的KNN对比验证 ==========================

print("\n" + "=" * 60)
print("与sklearn库KNN的对比验证")
print("=" * 60)

try:
    from sklearn.neighbors import KNeighborsClassifier
    
    # sklearn KNN
    sklearn_knn = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
    sklearn_knn.fit(X_train, y_train)
    
    start_time = time.time()
    y_pred_sklearn = sklearn_knn.predict(X_test)
    elapsed_sklearn = time.time() - start_time
    
    acc_sklearn = accuracy_score(y_test, y_pred_sklearn)
    
    print(f"\n手动实现KNN准确率: {accuracy_score(y_test, y_pred_best):.4f}")
    print(f"sklearn KNN准确率: {acc_sklearn:.4f}")
    print(f"sklearn预测耗时: {elapsed_sklearn:.2f}秒")
    
    # 对比结果
    comparison = pd.DataFrame({
        '实现方式': ['手动实现', 'sklearn库'],
        '准确率': [accuracy_score(y_test, y_pred_best), acc_sklearn],
        'K值': [5, 5],
        '距离度量': ['欧氏距离', '欧氏距离']
    })
    print("\n对比结果:")
    print(comparison.to_string(index=False))
    
except ImportError:
    print("sklearn库未安装，跳过对比验证")

# ========================== 9. 实验总结 ==========================

print("\n" + "=" * 60)
print("实验总结")
print("=" * 60)
print(f"1. 数据集: 手写数字数据集，共{len(data)}条样本，10个类别(0-9)")
print(f"2. 训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
print(f"3. 最优K值: {int(best_k)}")
print(f"4. 最优模型准确率: {k_df.loc[k_df['Accuracy'].idxmax(), 'Accuracy']:.4f}")
print(f"5. 欧氏距离 vs 曼哈顿距离: 欧氏距离在本数据集上表现更好")
print("6. KNN算法原理简单，无需训练过程，但预测时计算量大")
print("7. K值过小容易受噪声影响，K值过大会模糊类别边界")

print("\n" + "=" * 60)
print("实验完成!")
print("=" * 60)
