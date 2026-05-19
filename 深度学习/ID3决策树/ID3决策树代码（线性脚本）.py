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
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ID3决策树节点
class ID3Node:
    def __init__(self, feature=None, value=None, label=None, children=None):
        self.feature = feature
        self.value = value
        self.label = label
        self.children = children or {}

# ID3决策树分类器
class ID3Classifier:
    def __init__(self, max_depth=None, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
        self.feature_names = None
        self.default_label = None

    @staticmethod
    def entropy(y):
        counter = Counter(y)
        total = len(y)
        ent = 0.0
        for count in counter.values():
            p = count / total
            if p > 0:
                ent -= p * np.log2(p)
        return ent

    def information_gain(self, X_feature, y):
        base_entropy = self.entropy(y)
        values = np.unique(X_feature)
        weighted_entropy = 0.0
        for v in values:
            mask = X_feature == v
            subset_y = y[mask]
            weight = len(subset_y) / len(y)
            weighted_entropy += weight * self.entropy(subset_y)
        return base_entropy - weighted_entropy

    def best_feature(self, X, y, feature_indices):
        best_gain = -1
        best_feature = None
        for idx in feature_indices:
            gain = self.information_gain(X.iloc[:, idx].values, y.values)
            if gain > best_gain:
                best_gain = gain
                best_feature = idx
        return best_feature, best_gain

    def build_tree(self, X, y, feature_indices, depth=0):
        if len(np.unique(y)) == 1:
            return ID3Node(label=y.iloc[0])
        if len(feature_indices) == 0:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        if self.max_depth is not None and depth >= self.max_depth:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        if len(y) < self.min_samples_split:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        best_idx, best_gain = self.best_feature(X, y, feature_indices)
        if best_gain < 1e-6:
            return ID3Node(label=Counter(y).most_common(1)[0][0])
        node = ID3Node(feature=best_idx)
        remaining_features = [i for i in feature_indices if i != best_idx]
        for fv in np.unique(X.iloc[:, best_idx]):
            mask = X.iloc[:, best_idx] == fv
            subset_X = X[mask].reset_index(drop=True)
            subset_y = y[mask].reset_index(drop=True)
            child = self.build_tree(subset_X, subset_y, remaining_features, depth + 1)
            node.children[fv] = child
        return node

    def fit(self, X, y, feature_names=None):
        self.feature_names = feature_names or [f'特征{i}' for i in range(X.shape[1])]
        self.default_label = Counter(y).most_common(1)[0][0]
        feature_indices = list(range(X.shape[1]))
        self.tree = self.build_tree(X.reset_index(drop=True), y.reset_index(drop=True), feature_indices)
        return self

    def predict_single(self, x, node):
        if node.label is not None:
            return node.label
        feature_value = x[node.feature] if hasattr(x, '__getitem__') else x.iloc[node.feature]
        if feature_value in node.children:
            result = self.predict_single(x, node.children[feature_value])
            if result is not None:
                return result
        child_labels = [child.label for child in node.children.values() if child.label is not None]
        if child_labels:
            return Counter(child_labels).most_common(1)[0][0]
        return self.default_label

    def predict(self, X):
        results = []
        for i in range(len(X)):
            pred = self.predict_single(X.iloc[i], self.tree)
            if pred is None:
                pred = self.default_label
            results.append(pred)
        return results


# 加载数据
df = pd.read_csv('NBA_Season_Stats.csv')
feature_cols = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS']
X = df[feature_cols].copy()
y = df['Pos'].copy()
X = X.fillna(X.median())

# 连续特征离散化
discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile', subsample=None)
X_discrete = discretizer.fit_transform(X)
X_discrete = pd.DataFrame(X_discrete, columns=feature_cols)

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(
    X_discrete, y, test_size=0.3, random_state=42, stratify=y
)

# 训练ID3模型
id3 = ID3Classifier(max_depth=8, min_samples_split=20)
id3.fit(X_train, y_train, feature_names=feature_cols)
y_pred = id3.predict(X_test)

# 评估
accuracy = accuracy_score(y_test, y_pred)
print(f"ID3准确率: {accuracy:.4f}")
print(classification_report(y_test, y_pred, digits=4))

# 可视化
fig, ax = plt.subplots(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=['C', 'PF', 'PG', 'SF', 'SG'],
            yticklabels=['C', 'PF', 'PG', 'SF', 'SG'], ax=ax)
ax.set_title(f'ID3决策树 - 混淆矩阵 (准确率={accuracy:.4f})')
plt.tight_layout()
plt.savefig('exp3_id3_cm.png', dpi=150)
plt.show()

# 特征信息增益
feature_gains = []
for idx, fname in enumerate(feature_cols):
    gain = id3.information_gain(X_train.iloc[:, idx].values, y_train.values)
    feature_gains.append(gain)
feature_importance = pd.DataFrame({'Feature': feature_cols, 'Information_Gain': feature_gains})
feature_importance = feature_importance.sort_values('Information_Gain', ascending=True)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(feature_importance['Feature'], feature_importance['Information_Gain'], color='steelblue')
ax.set_xlabel('信息增益')
ax.set_title('ID3特征信息增益')
plt.tight_layout()
plt.savefig('exp3_id3_importance.png', dpi=150)
plt.show()
