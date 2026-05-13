import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
import matplotlib.pyplot as plt

# --- 1. 数据加载与预处理 ---
# 假设使用用户上传的 'iris_train.csv' 文件
df = pd.read_csv('iris_train.csv', index_col=0)

# 提取特征数据
X = df[['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']]

# 提取真实标签
true_labels = df['Species'].astype('category').cat.codes
species_names = df['Species'].unique()

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- 2. K-Means 聚类 (K=3) ---
K = 3
kmeans = KMeans(n_clusters=K, init='k-means++', max_iter=300, n_init=10, random_state=42)
cluster_labels = kmeans.fit_predict(X_scaled)
df['Cluster'] = cluster_labels

# --- 3. 结果可视化---
plt.figure(figsize=(12, 5))

# 子图 1: 真实标签分布
plt.subplot(1, 2, 1)
scatter1 = plt.scatter(df['Petal.Length'], df['Petal.Width'], c=true_labels, cmap='viridis', s=50, alpha=0.7)
plt.title('True Labels (Species)')
plt.xlabel('Petal.Length')
plt.ylabel('Petal.Width')

# 修复：确保 labels 是一个 Python 列表
handles1, _ = scatter1.legend_elements()
plt.legend(handles1, list(species_names), title="Species", loc="lower right")


# 子图 2: K-Means 聚类结果
plt.subplot(1, 2, 2)
scatter2 = plt.scatter(df['Petal.Length'], df['Petal.Width'], c=cluster_labels, cmap='viridis', s=50, alpha=0.7)
# 绘制质心
centers = scaler.inverse_transform(kmeans.cluster_centers_)
plt.scatter(centers[:, 2], centers[:, 3], marker='X', s=200, c='red', label='Centroids')
plt.title(f'K-Means Clustering (K={K})')
plt.xlabel('Petal.Length')
plt.ylabel('Petal.Width')

# 修复和增强：将聚类和质心标记都加入图例
handles2, _ = scatter2.legend_elements()
cluster_labels_list = [f'Cluster {i}' for i in range(K)]
# 手动创建一个质心 handle 并添加到图例中
plt.legend(handles2 + [plt.scatter([],[], marker='X', s=200, c='red')],
           cluster_labels_list + ['Centroids'],
           title="Cluster", loc="lower right")

plt.tight_layout()
plt.show() # 这会生成 'kmeans_visualization_fixed.png'

# --- 4. 结果评估 ---
sil_score = silhouette_score(X_scaled, cluster_labels)
ari_score = adjusted_rand_score(true_labels, cluster_labels)

# --- 5. 打印交叉表 ---
cross_tab = pd.crosstab(df['Species'], df['Cluster'])
# --- 2. 实验过程：最佳 K 值确定（肘方法） ---
# K值范围设置为1到10，计算每个K值对应的平方误差和（SSE）
sse = []
for k in range(1, 11):
    # n_init=10 表示重复运行10次K-Means，取最好的结果
    kmeans_elbow = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    kmeans_elbow.fit(X_scaled)
    sse.append(kmeans_elbow.inertia_) # inertia_ 即为 SSE

# 绘制肘部图 (请将此图嵌入报告的 3.3 节)
plt.figure(figsize=(8, 5))
plt.plot(range(1, 11), sse, marker='o', linestyle='--')
plt.title('Elbow Method for Optimal K')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Sum of Squared Errors (SSE)')
plt.grid(True)
plt.show()