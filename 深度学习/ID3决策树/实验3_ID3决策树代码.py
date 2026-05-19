#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验3：ID3决策树分类算法
使用NBA球员赛季统计数据，基于ID3算法预测球员位置
数据集：NBA_Season_Stats.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)
from collections import Counter
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
TEST_SIZE = 0.3                     # 测试集比例
RANDOM_STATE = 42                   # 随机种子
N_BINS = 5                          # 等频分箱数
MAX_DEPTH = 8                       # 决策树最大深度
MIN_SAMPLES_SPLIT = 20              # 最小分裂样本数

# 选择的特征列
FEATURE_COLS = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS']

# 目标变量
TARGET_COL = 'Pos'


# ============================================
# ID3决策树核心数据结构
# ============================================
class ID3Node:
    """
    ID3决策树节点类
    
    属性:
        feature: 分裂特征的索引
        value: 分裂特征的名称
        label: 叶节点的类别标签（None表示非叶节点）
        children: 子节点字典 {特征值: 子节点}
    """
    def __init__(self, feature=None, value=None, label=None, children=None):
        self.feature = feature      # 分裂特征的列索引
        self.value = value          # 分裂特征的名称
        self.label = label          # 叶节点类别标签
        self.children = children or {}  # 子节点字典


class ID3Classifier:
    """
    ID3决策树分类器
    
    基于信息增益递归构建决策树，仅处理离散型特征。
    算法流程：
        1. 计算当前数据集的信息熵
        2. 对每个特征计算信息增益
        3. 选择信息增益最大的特征作为分裂节点
        4. 对每个特征值递归构建子树
    
    属性:
        max_depth: 最大树深度
        min_samples_split: 最小分裂样本数
        tree: 决策树根节点
        feature_names: 特征名称列表
        default_label: 默认类别标签（处理未见过的特征值）
    """
    
    def __init__(self, max_depth=None, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
        self.feature_names = None
        self.default_label = None
    
    @staticmethod
    def entropy(y):
        """
        计算信息熵 H(S) = -sum(p_i * log2(p_i))
        
        参数:
            y: 标签数组
        返回:
            信息熵值
        """
        counter = Counter(y)
        total = len(y)
        ent = 0.0
        for count in counter.values():
            p = count / total
            if p > 0:
                ent -= p * np.log2(p)
        return ent
    
    def information_gain(self, X_feature, y):
        """
        计算信息增益 IG(S, A) = H(S) - H(S|A)
        
        信息增益 = 父节点熵 - 加权平均子节点熵
        
        参数:
            X_feature: 某一特征的取值数组
            y: 标签数组
        返回:
            信息增益值
        """
        # 原始熵
        base_entropy = self.entropy(y)
        
        # 按特征值分组计算加权熵
        values = np.unique(X_feature)
        weighted_entropy = 0.0
        for v in values:
            mask = X_feature == v
            subset_y = y[mask]
            weight = len(subset_y) / len(y)
            weighted_entropy += weight * self.entropy(subset_y)
        
        return base_entropy - weighted_entropy
    
    def best_feature(self, X, y, feature_indices):
        """
        选择信息增益最大的特征作为分裂特征
        
        参数:
            X: 特征DataFrame
            y: 标签Series
            feature_indices: 可选特征的索引列表
        返回:
            best_feature: 最优特征的索引
            best_gain: 最大信息增益值
        """
        best_gain = -1
        best_feature = None
        
        for idx in feature_indices:
            gain = self.information_gain(X.iloc[:, idx].values, y.values)
            if gain > best_gain:
                best_gain = gain
                best_feature = idx
        
        return best_feature, best_gain
    
    def build_tree(self, X, y, feature_indices, depth=0):
        """
        递归构建决策树
        
        终止条件：
        - 所有样本属于同一类别
        - 没有可用特征
        - 达到最大深度
        - 样本数不足
        - 信息增益太小
        
        参数:
            X: 特征DataFrame
            y: 标签Series
            feature_indices: 可用特征的索引列表
            depth: 当前深度
        返回:
            决策树根节点
        """
        # 所有样本属于同一类别
        if len(np.unique(y)) == 1:
            return ID3Node(label=y.iloc[0])
        
        # 没有可用特征
        if len(feature_indices) == 0:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        
        # 达到最大深度
        if self.max_depth is not None and depth >= self.max_depth:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        
        # 样本数不足
        if len(y) < self.min_samples_split:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        
        # 选择最优特征
        best_idx, best_gain = self.best_feature(X, y, feature_indices)
        
        # 信息增益太小，停止分裂
        if best_gain < 1e-6:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        
        # 创建节点
        node = ID3Node(feature=best_idx, value=self.feature_names[best_idx])
        remaining_features = [i for i in feature_indices if i != best_idx]
        
        # 对每个特征值创建子树
        for fv in np.unique(X.iloc[:, best_idx]):
            mask = X.iloc[:, best_idx] == fv
            subset_X = X[mask].reset_index(drop=True)
            subset_y = y[mask].reset_index(drop=True)
            child = self.build_tree(subset_X, subset_y, remaining_features, depth + 1)
            node.children[fv] = child
        
        return node
    
    def fit(self, X, y, feature_names=None):
        """
        训练ID3决策树模型
        
        参数:
            X: 离散化后的特征DataFrame
            y: 标签Series
            feature_names: 特征名称列表
        返回:
            self
        """
        self.feature_names = feature_names or [f'特征{i}' for i in range(X.shape[1])]
        self.default_label = Counter(y).most_common(1)[0][0]
        feature_indices = list(range(X.shape[1]))
        self.tree = self.build_tree(X.reset_index(drop=True), y.reset_index(drop=True), feature_indices)
        return self
    
    def predict_single(self, x, node):
        """
        对单条样本进行预测
        
        参数:
            x: 单条特征数据
            node: 当前树节点
        返回:
            预测的类别标签
        """
        # 到达叶节点
        if node.label is not None:
            return node.label
        
        # 获取特征值
        feature_value = x[node.feature] if hasattr(x, '__getitem__') else x.iloc[node.feature]
        
        # 特征值在训练集中存在
        if feature_value in node.children:
            result = self.predict_single(x, node.children[feature_value])
            if result is not None:
                return result
        
        # 特征值未见过，返回子节点中最常见的标签
        child_labels = [child.label for child in node.children.values() if child.label is not None]
        if child_labels:
            return Counter(child_labels).most_common(1)[0][0]
        
        return self.default_label
    
    def predict(self, X):
        """
        批量预测
        
        参数:
            X: 特征DataFrame
        返回:
            预测标签列表
        """
        results = []
        for i in range(len(X)):
            pred = self.predict_single(X.iloc[i], self.tree)
            if pred is None:
                pred = self.default_label
            results.append(pred)
        return results


# ============================================
# 1. 数据加载与预处理
# ============================================
def load_and_preprocess_data(filepath):
    """
    加载数据并进行预处理
    
    参数:
        filepath: 数据集文件路径
    返回:
        X: 原始特征DataFrame
        X_discrete: 离散化后的特征DataFrame
        y: 标签Series
    """
    print("=" * 60)
    print("1. 数据加载与预处理")
    print("=" * 60)
    
    df = pd.read_csv(filepath)
    print(f"数据集原始形状: {df.shape}")
    
    # 提取特征和标签
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()
    
    # 处理缺失值
    missing_before = X.isnull().sum().sum()
    X = X.fillna(X.median())
    missing_after = X.isnull().sum().sum()
    print(f"缺失值处理: {missing_before} -> {missing_after}")
    
    # 连续特征离散化 - 等频分箱
    print(f"\n连续特征离散化（等频分箱，n_bins={N_BINS}）...")
    discretizer = KBinsDiscretizer(n_bins=N_BINS, encode='ordinal', strategy='quantile', subsample=None)
    X_discrete = discretizer.fit_transform(X)
    X_discrete = pd.DataFrame(X_discrete, columns=FEATURE_COLS)
    print(f"离散化完成，每个特征被划分为{N_BINS}个区间 (0-{N_BINS-1})")
    
    return X, X_discrete, y


# ============================================
# 2. 数据集划分
# ============================================
def split_dataset(X_discrete, y):
    """
    将数据集划分为训练集和测试集
    
    参数:
        X_discrete: 离散化后的特征DataFrame
        y: 标签Series
    返回:
        X_train, X_test, y_train, y_test
    """
    print("\n" + "=" * 60)
    print("2. 数据集划分")
    print("=" * 60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_discrete, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"训练集样本数: {len(X_train)} ({len(X_train)/len(X_discrete)*100:.1f}%)")
    print(f"测试集样本数: {len(X_test)} ({len(X_test)/len(X_discrete)*100:.1f}%)")
    
    # 类别分布
    print(f"\n训练集类别分布:")
    for pos, count in y_train.value_counts().items():
        print(f"  {pos}: {count}")
    
    return X_train, X_test, y_train, y_test


# ============================================
# 3. ID3决策树模型训练
# ============================================
def train_id3_model(X_train, y_train, feature_names):
    """
    训练ID3决策树模型
    
    参数:
        X_train: 训练集特征
        y_train: 训练集标签
        feature_names: 特征名称列表
    返回:
        id3: 训练好的ID3决策树分类器
    """
    print("\n" + "=" * 60)
    print("3. ID3决策树模型训练")
    print("=" * 60)
    
    id3 = ID3Classifier(max_depth=MAX_DEPTH, min_samples_split=MIN_SAMPLES_SPLIT)
    id3.fit(X_train, y_train, feature_names=feature_names)
    
    print("模型训练完成!")
    print(f"  最大深度: {MAX_DEPTH}")
    print(f"  最小分裂样本数: {MIN_SAMPLES_SPLIT}")
    
    return id3


# ============================================
# 4. 模型预测与评估
# ============================================
def evaluate_model(id3, X_test, y_test):
    """
    评估ID3决策树模型性能
    
    参数:
        id3: 训练好的ID3决策树分类器
        X_test: 测试集特征
        y_test: 测试集标签
    返回:
        y_pred: 预测标签
        metrics: 评估指标字典
    """
    print("\n" + "=" * 60)
    print("4. 模型预测与评估")
    print("=" * 60)
    
    y_pred = id3.predict(X_test)
    
    # 计算各项指标
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    
    print(f"\n整体评估指标:")
    print(f"  准确率 (Accuracy): {accuracy:.4f}")
    print(f"  宏平均精确率 (Macro Precision): {precision_macro:.4f}")
    print(f"  宏平均召回率 (Macro Recall): {recall_macro:.4f}")
    print(f"  宏平均F1分数 (Macro F1): {f1_macro:.4f}")
    
    print(f"\n分类报告:")
    print(classification_report(y_test, y_pred, digits=4))
    
    cm = confusion_matrix(y_test, y_pred)
    metrics = {
        'accuracy': accuracy,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'confusion_matrix': cm
    }
    
    return y_pred, metrics


# ============================================
# 5. 特征信息增益分析
# ============================================
def analyze_feature_importance(id3, X_train, y_train):
    """
    分析各特征的信息增益
    
    参数:
        id3: 训练好的ID3决策树分类器
        X_train: 训练集特征
        y_train: 训练集标签
    """
    print("\n" + "=" * 60)
    print("5. 特征信息增益分析")
    print("=" * 60)
    
    feature_gains = []
    for idx, fname in enumerate(FEATURE_COLS):
        gain = id3.information_gain(X_train.iloc[:, idx].values, y_train.values)
        feature_gains.append(gain)
    
    # 排序
    sorted_gains = sorted(zip(FEATURE_COLS, feature_gains), key=lambda x: x[1], reverse=True)
    print("\n各特征的信息增益（降序）:")
    for fname, gain in sorted_gains:
        print(f"  {fname:<8}: {gain:.6f}")
    
    return feature_gains


# ============================================
# 6. 可视化
# ============================================
def visualize_results(y_test, y_pred, metrics, feature_gains):
    """
    生成可视化图表
    
    参数:
        y_test: 真实标签
        y_pred: 预测标签
        metrics: 评估指标字典
        feature_gains: 各特征的信息增益列表
    """
    print("\n" + "=" * 60)
    print("6. 生成可视化图表")
    print("=" * 60)
    
    cm = metrics['confusion_matrix']
    
    # 6.1 混淆矩阵
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
                xticklabels=['C', 'PF', 'PG', 'SF', 'SG'],
                yticklabels=['C', 'PF', 'PG', 'SF', 'SG'], ax=ax)
    ax.set_xlabel('预测类别', fontsize=12)
    ax.set_ylabel('真实类别', fontsize=12)
    ax.set_title(f'ID3决策树 - 混淆矩阵 (准确率={metrics["accuracy"]:.4f})', fontsize=14)
    plt.tight_layout()
    plt.savefig('exp3_id3_cm.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [1/2] 混淆矩阵图已保存")
    
    # 6.2 特征信息增益
    feature_importance = pd.DataFrame({
        'Feature': FEATURE_COLS,
        'Information_Gain': feature_gains
    }).sort_values('Information_Gain', ascending=True)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(feature_importance)))
    ax.barh(feature_importance['Feature'], feature_importance['Information_Gain'], color=colors)
    ax.set_xlabel('信息增益', fontsize=12)
    ax.set_ylabel('特征', fontsize=12)
    ax.set_title('ID3特征信息增益', fontsize=14)
    plt.tight_layout()
    plt.savefig('exp3_id3_importance.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [2/2] 特征信息增益图已保存")


# ============================================
# 主函数
# ============================================
def main():
    """主函数：执行完整的ID3决策树实验流程"""
    
    print("\n" + "=" * 60)
    print("实验3：ID3决策树分类算法 - NBA球员位置预测")
    print("=" * 60 + "\n")
    
    # 1. 数据加载与预处理
    X, X_discrete, y = load_and_preprocess_data(DATA_PATH)
    
    # 2. 数据集划分
    X_train, X_test, y_train, y_test = split_dataset(X_discrete, y)
    
    # 3. ID3模型训练
    id3 = train_id3_model(X_train, y_train, FEATURE_COLS)
    
    # 4. 模型评估
    y_pred, metrics = evaluate_model(id3, X_test, y_test)
    
    # 5. 特征信息增益分析
    feature_gains = analyze_feature_importance(id3, X_train, y_train)
    
    # 6. 可视化
    visualize_results(y_test, y_pred, metrics, feature_gains)
    
    print("\n" + "=" * 60)
    print("实验完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
