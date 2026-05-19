#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验4：C4.5决策树分类算法
使用NBA球员赛季统计数据，基于C4.5算法预测球员位置
数据集：NBA_Season_Stats.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
df = pd.read_csv('NBA_Season_Stats.csv')
feature_cols = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS']
X = df[feature_cols].copy()
y = df['Pos'].copy()
X = X.fillna(X.median())

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 训练C4.5决策树（使用entropy准则）
c45 = DecisionTreeClassifier(
    criterion='entropy', max_depth=10, min_samples_split=20,
    min_samples_leaf=10, random_state=42
)
c45.fit(X_train, y_train)

# 预测
y_pred = c45.predict(X_test)

# 评估
accuracy = accuracy_score(y_test, y_pred)
print(f"C4.5准确率: {accuracy:.4f}")
print(classification_report(y_test, y_pred, digits=4))

# 1. 混淆矩阵
fig, ax = plt.subplots(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
            xticklabels=['C', 'PF', 'PG', 'SF', 'SG'],
            yticklabels=['C', 'PF', 'PG', 'SF', 'SG'], ax=ax)
ax.set_title(f'C4.5决策树 - 混淆矩阵 (准确率={accuracy:.4f})')
plt.tight_layout()
plt.savefig('exp4_c45_cm.png', dpi=150)
plt.show()

# 2. 特征重要性
feature_imp = pd.DataFrame({'Feature': feature_cols, 'Importance': c45.feature_importances_})
feature_imp = feature_imp.sort_values('Importance', ascending=True)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(feature_imp['Feature'], feature_imp['Importance'], color='coral')
ax.set_xlabel('特征重要性')
ax.set_title('C4.5决策树特征重要性')
plt.tight_layout()
plt.savefig('exp4_c45_importance.png', dpi=150)
plt.show()

# 3. 决策树结构（前3层）
fig, ax = plt.subplots(figsize=(20, 10))
plot_tree(c45, max_depth=3, feature_names=feature_cols,
          class_names=['C', 'PF', 'PG', 'SF', 'SG'],
          filled=True, rounded=True, fontsize=8, ax=ax)
ax.set_title('C4.5决策树结构（前3层）')
plt.tight_layout()
plt.savefig('exp4_c45_tree.png', dpi=150)
plt.show()
