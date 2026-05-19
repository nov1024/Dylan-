#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验2：K-Means聚类算法
使用NBA球员赛季统计数据，对球员进行无监督聚类分析
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

# ============================================
# 中文字体配置（必须放在所有绘图代码之前）
# ============================================
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 配置参数
# ============================================
DATA_PATH = 'NBA_Season_Stats.csv'  # 数据集路径
RANDOM_STATE = 42                   # 随机种子
K_MIN = 2                           # 最小聚类数
K_MAX = 10                          # 最大聚类数
BEST_K = 5                          # 最佳聚类数

# 选择的特征列
FEATURE_COLS = ['Age', 'G', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%',
                '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']


# ============================================
# 1. 数据加载与预处理
# ============================================
def load_and_preprocess_data(filepath):
    """
    加载数据集并进行预处理
    
    参数:
        filepath: 数据集文件路径
    返回:
        X: 特征矩阵
        y_pos: 真实位置标签（用于后续对比）
        scaler: 标准化器
        X_scaled: 标准化后的特征矩阵
    """
    print("=" * 60)
    print("1. 数据加载与预处理")
    print("=" * 60)
    
    df = pd.read_csv(filepath)
    print(f"数据集原始形状: {df.shape}")
    
    # 提取特征和真实标签（真实标签仅用于聚类后对比，不参与聚类过程）
    X = df[FEATURE_COLS].copy()
    y_pos = df['Pos'].copy()
    
    # 处理缺失值 - 用中位数填充
    missing_before = X.isnull().sum().sum()
    X = X.fillna(X.median())
    missing_after = X.isnull().sum().sum()
    print(f"缺失值处理: {missing_before} -> {missing_after}")
    print(f"特征矩阵形状: {X.shape}")
    
    # 特征标准化（K-Means对特征的尺度敏感，必须标准化）
    print("\n特征标准化...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print(f"标准化后均值(前5个): {X_scaled.mean(axis=0)[:5]}")
    print(f"标准化后标准差(前5个): {X_scaled.std(axis=0)[:5]}")
    
    return X, y_pos, scaler, X_scaled


# ============================================
# 2. 肘部法则确定最佳聚类数K
# ============================================
def find_best_k(X_scaled, k_min=K_MIN, k_max=K_MAX):
    """
    使用肘部法则和轮廓系数法确定最佳聚类数
    
    参数:
        X_scaled: 标准化后的特征矩阵
        k_min: 最小聚类数
        k_max: 最大聚类数
    返回:
        inertias: 各K值的惯性列表
        silhouettes: 各K值的轮廓系数列表
    """
    print("\n" + "=" * 60)
    print("2. 肘部法则确定最佳聚类数K")
    print("=" * 60)
    
    inertias = []
    silhouettes = []
    K_range = range(k_min, k_max + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        sil = silhouette_score(X_scaled, kmeans.labels_)
        silhouettes.append(sil)
        print(f"  K={k}: 惯性={kmeans.inertia_:.2f}, 轮廓系数={sil:.4f}")
    
    return inertias, silhouettes, list(K_range)


def plot_elbow_method(inertias, silhouettes, K_range):
    """
    绘制肘部法则和轮廓系数法可视化图
    
    参数:
        inertias: 惯性列表
        silhouettes: 轮廓系数列表
        K_range: K值范围
    """
    print("\n绘制肘部法则和轮廓系数图...")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('聚类数 K', fontsize=12)
    axes[0].set_ylabel('惯性 (Inertia)', fontsize=12)
    axes[0].set_title('肘部法则', fontsize=14)
    axes[0].grid(True, alpha=0.3)
    axes[0].axvline(x=BEST_K, color='r', linestyle='--', label=f'K={BEST_K}')
    axes[0].legend()
    
    axes[1].plot(K_range, silhouettes, 'go-', linewidth=2, markersize=8)
    axes[1].set_xlabel('聚类数 K', fontsize=12)
    axes[1].set_ylabel('轮廓系数', fontsize=12)
    axes[1].set_title('轮廓系数法', fontsize=14)
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(x=BEST_K, color='r', linestyle='--', label=f'K={BEST_K}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('exp2_elbow.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("肘部法则图已保存")


# ============================================
# 3. K-Means聚类
# ============================================
def perform_kmeans(X_scaled, k=BEST_K):
    """
    执行K-Means聚类
    
    参数:
        X_scaled: 标准化后的特征矩阵
        k: 聚类数
    返回:
        kmeans: 训练好的KMeans模型
        clusters: 聚类标签
    """
    print("\n" + "=" * 60)
    print(f"3. K-Means聚类 (K={k})")
    print("=" * 60)
    
    kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    print(f"聚类完成，共{k}个聚类")
    print(f"各聚类样本数:")
    for i in range(k):
        count = (clusters == i).sum()
        print(f"  聚类 {i}: {count} 个样本 ({count/len(clusters)*100:.1f}%)")
    
    return kmeans, clusters


# ============================================
# 4. 聚类评估
# ============================================
def evaluate_clustering(X_scaled, clusters, kmeans):
    """
    评估聚类效果
    
    参数:
        X_scaled: 标准化后的特征矩阵
        clusters: 聚类标签
        kmeans: 训练好的KMeans模型
    """
    print("\n" + "=" * 60)
    print("4. 聚类评估")
    print("=" * 60)
    
    sil_score = silhouette_score(X_scaled, clusters)
    ch_score = calinski_harabasz_score(X_scaled, clusters)
    db_score = davies_bouldin_score(X_scaled, clusters)
    
    print(f"\n聚类评估指标:")
    print(f"  轮廓系数 (Silhouette Score): {sil_score:.4f}")
    print(f"  Calinski-Harabasz指数: {ch_score:.2f}")
    print(f"  Davies-Bouldin指数: {db_score:.4f}")
    
    # 聚类中心分析
    centers = kmeans.cluster_centers_
    print(f"\n聚类中心（标准化空间）的关键特征统计:")
    key_idx = [FEATURE_COLS.index(f) for f in ['PTS', 'AST', 'TRB', 'BLK', 'STL', 'MP']]
    for i in range(len(centers)):
        print(f"  聚类 {i}: PTS={centers[i][key_idx[0]]:.2f}, "
              f"AST={centers[i][key_idx[1]]:.2f}, TRB={centers[i][key_idx[2]]:.2f}, "
              f"BLK={centers[i][key_idx[3]]:.2f}, STL={centers[i][key_idx[4]]:.2f}, "
              f"MP={centers[i][key_idx[5]]:.2f}")


# ============================================
# 5. 聚类结果与真实标签对比
# ============================================
def compare_with_true_labels(clusters, y_pos):
    """
    将聚类结果与真实位置标签进行对比
    
    参数:
        clusters: 聚类标签
        y_pos: 真实位置标签
    """
    print("\n" + "=" * 60)
    print("5. 聚类结果与真实标签对比")
    print("=" * 60)
    
    comparison_df = pd.DataFrame({'Cluster': clusters, 'True_Pos': y_pos.values})
    cluster_pos_crosstab = pd.crosstab(comparison_df['Cluster'], comparison_df['True_Pos'])
    print("\n聚类与真实位置的交叉表:")
    print(cluster_pos_crosstab)
    
    print("\n各聚类的主要类别:")
    for i in range(BEST_K):
        cluster_mask = clusters == i
        cluster_size = cluster_mask.sum()
        pos_in_cluster = y_pos[cluster_mask].value_counts()
        dominant_pos = pos_in_cluster.index[0]
        dominant_pct = pos_in_cluster.iloc[0] / cluster_size * 100
        print(f"  聚类{i}: 样本数={cluster_size}, 主要类别={dominant_pos} ({dominant_pct:.1f}%)")


# ============================================
# 6. PCA降维可视化
# ============================================
def visualize_pca(X_scaled, clusters, y_pos):
    """
    使用PCA降维后可视化聚类结果
    
    参数:
        X_scaled: 标准化后的特征矩阵
        clusters: 聚类标签
        y_pos: 真实位置标签
    """
    print("\n" + "=" * 60)
    print("6. PCA降维可视化")
    print("=" * 60)
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 按聚类结果可视化
    for i in range(BEST_K):
        mask = clusters == i
        axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c=colors[i], 
                        label=f'聚类 {i}', alpha=0.5, s=8)
    axes[0].set_xlabel(f'第一主成分 ({pca.explained_variance_ratio_[0]:.2%})', fontsize=11)
    axes[0].set_ylabel(f'第二主成分 ({pca.explained_variance_ratio_[1]:.2%})', fontsize=11)
    axes[0].set_title('K-Means聚类结果 (PCA降维)', fontsize=13)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 按真实位置可视化
    pos_colors = {'C': '#1f77b4', 'PF': '#ff7f0e', 'PG': '#2ca02c', 'SF': '#d62728', 'SG': '#9467bd'}
    for pos in ['C', 'PF', 'PG', 'SF', 'SG']:
        mask = y_pos == pos
        axes[1].scatter(X_pca[mask, 0], X_pca[mask, 1], c=pos_colors[pos], 
                        label=pos, alpha=0.5, s=8)
    axes[1].set_xlabel(f'第一主成分 ({pca.explained_variance_ratio_[0]:.2%})', fontsize=11)
    axes[1].set_ylabel(f'第二主成分 ({pca.explained_variance_ratio_[1]:.2%})', fontsize=11)
    axes[1].set_title('真实位置分布 (PCA降维)', fontsize=13)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('exp2_pca.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("PCA可视化图已保存")


# ============================================
# 7. 聚类中心热力图
# ============================================
def plot_cluster_heatmap(kmeans, scaler):
    """
    绘制聚类中心特征热力图
    
    参数:
        kmeans: 训练好的KMeans模型
        scaler: 标准化器（用于反标准化）
    """
    print("\n" + "=" * 60)
    print("7. 聚类中心热力图")
    print("=" * 60)
    
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    centers_df = pd.DataFrame(centers, columns=FEATURE_COLS)
    key_features = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'PF', 'PTS']
    centers_selected = centers_df[key_features]
    
    # 标准化到0-1用于热力图
    centers_norm = (centers_selected - centers_selected.min()) / (centers_selected.max() - centers_selected.min())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(centers_norm.T, annot=centers_selected.T.round(1), fmt='.1f', cmap='YlOrRd', ax=ax,
                xticklabels=[f'聚类{i}' for i in range(BEST_K)], yticklabels=key_features)
    ax.set_title('K-Means聚类中心特征热力图', fontsize=14)
    ax.set_xlabel('聚类编号', fontsize=12)
    plt.tight_layout()
    plt.savefig('exp2_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("聚类中心热力图已保存")


# ============================================
# 主函数
# ============================================
def main():
    """主函数：执行完整的K-Means聚类实验流程"""
    
    print("\n" + "=" * 60)
    print("实验2：K-Means聚类算法 - NBA球员聚类分析")
    print("=" * 60 + "\n")
    
    # 1. 数据加载与预处理
    X, y_pos, scaler, X_scaled = load_and_preprocess_data(DATA_PATH)
    
    # 2. 肘部法则确定最佳K
    inertias, silhouettes, K_range = find_best_k(X_scaled)
    plot_elbow_method(inertias, silhouettes, K_range)
    
    # 3. K-Means聚类
    kmeans, clusters = perform_kmeans(X_scaled)
    
    # 4. 聚类评估
    evaluate_clustering(X_scaled, clusters, kmeans)
    
    # 5. 与真实标签对比
    compare_with_true_labels(clusters, y_pos)
    
    # 6. PCA降维可视化
    visualize_pca(X_scaled, clusters, y_pos)
    
    # 7. 聚类中心热力图
    plot_cluster_heatmap(kmeans, scaler)
    
    print("\n" + "=" * 60)
    print("实验完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
