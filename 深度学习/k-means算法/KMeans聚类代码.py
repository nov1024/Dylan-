#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验2：K-Means聚类算法
使用NBA球员赛季统计数据，对球员进行聚类分析
数据集：NBA_Season_Stats.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
df = pd.read_csv('NBA_Season_Stats.csv')

# 选择特征
feature_cols = ['Age', 'G', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%',
                '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
X = df[feature_cols].copy()
X = X.fillna(X.median())

# 特征标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 1. 肘部法则确定最佳K值
inertias = []
silhouettes = []
K_range = range(2, 11)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(X_scaled, kmeans.labels_))

# 绘制肘部法则图
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(list(K_range), inertias, 'bo-', linewidth=2, markersize=8)
axes[0].set_xlabel('聚类数 K')
axes[0].set_ylabel('惯性 (Inertia)')
axes[0].set_title('肘部法则')
axes[0].grid(True, alpha=0.3)
axes[1].plot(list(K_range), silhouettes, 'go-', linewidth=2, markersize=8)
axes[1].set_xlabel('聚类数 K')
axes[1].set_ylabel('轮廓系数')
axes[1].set_title('轮廓系数法')
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('exp2_elbow.png', dpi=150)
plt.show()

# 2. K-Means聚类 (K=5)
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# 聚类评估
sil_score = silhouette_score(X_scaled, clusters)
ch_score = calinski_harabasz_score(X_scaled, clusters)
db_score = davies_bouldin_score(X_scaled, clusters)
print(f"轮廓系数: {sil_score:.4f}")
print(f"Calinski-Harabasz指数: {ch_score:.2f}")
print(f"Davies-Bouldin指数: {db_score:.4f}")

# 3. PCA降维可视化
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
for i in range(5):
    mask = clusters == i
    axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c=colors[i], label=f'聚类 {i}', alpha=0.5, s=8)
axes[0].set_title('K-Means聚类结果 (PCA降维)')
axes[0].legend()
pos_colors = {'C': '#1f77b4', 'PF': '#ff7f0e', 'PG': '#2ca02c', 'SF': '#d62728', 'SG': '#9467bd'}
for pos in ['C', 'PF', 'PG', 'SF', 'SG']:
    mask = df['Pos'] == pos
    axes[1].scatter(X_pca[mask, 0], X_pca[mask, 1], c=pos_colors[pos], label=pos, alpha=0.5, s=8)
axes[1].set_title('真实位置分布 (PCA降维)')
axes[1].legend()
plt.tight_layout()
plt.savefig('exp2_pca.png', dpi=150)
plt.show()

# 聚类中心热力图
centers = scaler.inverse_transform(kmeans.cluster_centers_)
centers_df = pd.DataFrame(centers, columns=feature_cols)
key_features = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'PF', 'PTS']
centers_selected = centers_df[key_features]
centers_norm = (centers_selected - centers_selected.min()) / (centers_selected.max() - centers_selected.min())
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(centers_norm.T, annot=centers_selected.T.round(1), fmt='.1f', cmap='YlOrRd', ax=ax,
            xticklabels=[f'聚类{i}' for i in range(5)], yticklabels=key_features)
ax.set_title('K-Means聚类中心特征热力图')
plt.tight_layout()
plt.savefig('exp2_heatmap.png', dpi=150)
plt.show()
