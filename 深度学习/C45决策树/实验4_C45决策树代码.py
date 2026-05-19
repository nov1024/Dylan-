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
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)
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
CV_FOLDS = 5                        # 交叉验证折数

# 模型参数
MAX_DEPTH = 10                      # 最大深度
MIN_SAMPLES_SPLIT = 20              # 最小分裂样本数
MIN_SAMPLES_LEAF = 10               # 最小叶节点样本数

# 选择的特征列（C4.5可直接处理连续特征）
FEATURE_COLS = ['Age', 'G', 'MP', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS']

# 目标变量
TARGET_COL = 'Pos'

# 类别标签
CLASS_NAMES = ['C', 'PF', 'PG', 'SF', 'SG']


# ============================================
# 1. 数据加载与预处理
# ============================================
def load_and_preprocess_data(filepath):
    """
    加载数据集并进行预处理
    
    C4.5可直接处理连续特征，无需预先离散化。
    
    参数:
        filepath: 数据集文件路径
    返回:
        X: 特征DataFrame
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
    
    # 处理缺失值 - 用中位数填充
    missing_before = X.isnull().sum().sum()
    X = X.fillna(X.median())
    missing_after = X.isnull().sum().sum()
    print(f"缺失值处理: {missing_before} -> {missing_after}")
    
    # 查看目标变量分布
    print(f"\n目标变量分布:")
    for pos, count in y.value_counts().items():
        print(f"  {pos}: {count} ({count/len(y)*100:.1f}%)")
    
    print(f"\n特征矩阵形状: {X.shape}")
    print(f"特征列: {FEATURE_COLS}")
    
    return X, y


# ============================================
# 2. 数据集划分
# ============================================
def split_dataset(X, y):
    """
    将数据集划分为训练集和测试集
    
    参数:
        X: 特征DataFrame
        y: 标签Series
    返回:
        X_train, X_test, y_train, y_test
    """
    print("\n" + "=" * 60)
    print("2. 数据集划分")
    print("=" * 60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"训练集样本数: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"测试集样本数: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train, X_test, y_train, y_test


# ============================================
# 3. C4.5决策树模型训练
# ============================================
def train_c45_model(X_train, y_train):
    """
    训练C4.5决策树模型
    
    C4.5核心改进：
    1. 使用信息增益率(Information Gain Ratio)代替信息增益
    2. 能直接处理连续特征（基于阈值二分）
    3. 支持缺失值处理
    4. 支持剪枝（悲观剪枝）
    
    sklearn的DecisionTreeClassifier使用criterion='entropy'可近似实现C4.5的信息增益率。
    
    参数:
        X_train: 训练集特征
        y_train: 训练集标签
    返回:
        c45: 训练好的C4.5决策树模型
    """
    print("\n" + "=" * 60)
    print("3. C4.5决策树模型训练")
    print("=" * 60)
    
    c45 = DecisionTreeClassifier(
        criterion='entropy',       # 使用信息增益（率）
        max_depth=MAX_DEPTH,        # 最大深度
        min_samples_split=MIN_SAMPLES_SPLIT,  # 最小分裂样本数
        min_samples_leaf=MIN_SAMPLES_LEAF,    # 最小叶节点样本数
        random_state=RANDOM_STATE
    )
    
    c45.fit(X_train, y_train)
    
    print("模型训练完成!")
    print(f"  准则: entropy (信息增益率)")
    print(f"  最大深度: {MAX_DEPTH}")
    print(f"  最小分裂样本数: {MIN_SAMPLES_SPLIT}")
    print(f"  最小叶节点样本数: {MIN_SAMPLES_LEAF}")
    print(f"  实际树深度: {c45.get_depth()}")
    print(f"  叶节点数: {c45.get_n_leaves()}")
    
    return c45


# ============================================
# 4. 模型预测与评估
# ============================================
def evaluate_model(c45, X_test, y_test):
    """
    评估C4.5决策树模型性能
    
    参数:
        c45: 训练好的C4.5决策树模型
        X_test: 测试集特征
        y_test: 测试集标签
    返回:
        y_pred: 预测标签
        metrics: 评估指标字典
    """
    print("\n" + "=" * 60)
    print("4. 模型预测与评估")
    print("=" * 60)
    
    y_pred = c45.predict(X_test)
    
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
    
    print(f"\n各类别详细评估:")
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES, digits=4))
    
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
# 5. 特征重要性分析
# ============================================
def analyze_feature_importance(c45):
    """
    分析各特征的重要性
    
    参数:
        c45: 训练好的C4.5决策树模型
    返回:
        feature_imp_df: 特征重要性DataFrame
    """
    print("\n" + "=" * 60)
    print("5. 特征重要性分析")
    print("=" * 60)
    
    feature_imp_df = pd.DataFrame({
        'Feature': FEATURE_COLS,
        'Importance': c45.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\n各特征的重要性（降序）:")
    for _, row in feature_imp_df.iterrows():
        print(f"  {row['Feature']:<8}: {row['Importance']:.6f}")
    
    return feature_imp_df


# ============================================
# 6. 交叉验证
# ============================================
def cross_validation(c45, X_train, y_train):
    """
    进行K折交叉验证
    
    参数:
        c45: C4.5决策树模型
        X_train: 训练集特征
        y_train: 训练集标签
    返回:
        cv_scores: 交叉验证分数
    """
    print("\n" + "=" * 60)
    print(f"6. {CV_FOLDS}折交叉验证")
    print("=" * 60)
    
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(c45, X_train, y_train, cv=cv, scoring='accuracy')
    
    print(f"{CV_FOLDS}折交叉验证准确率:")
    for i, score in enumerate(cv_scores):
        print(f"  第{i+1}折: {score:.4f}")
    print(f"\n平均交叉验证准确率: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    return cv_scores


# ============================================
# 7. 决策树文本规则提取
# ============================================
def extract_tree_rules(c45):
    """
    提取决策树的文本规则
    
    参数:
        c45: 训练好的C4.5决策树模型
    """
    print("\n" + "=" * 60)
    print("7. 决策树文本规则（前3层）")
    print("=" * 60)
    
    tree_rules = export_text(c45, feature_names=FEATURE_COLS, max_depth=3)
    print(tree_rules)


# ============================================
# 8. 可视化
# ============================================
def visualize_results(c45, y_test, y_pred, metrics, feature_imp_df):
    """
    生成可视化图表
    
    参数:
        c45: 训练好的C4.5决策树模型
        y_test: 真实标签
        y_pred: 预测标签
        metrics: 评估指标字典
        feature_imp_df: 特征重要性DataFrame
    """
    print("\n" + "=" * 60)
    print("8. 生成可视化图表")
    print("=" * 60)
    
    cm = metrics['confusion_matrix']
    
    # 8.1 混淆矩阵
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax)
    ax.set_xlabel('预测类别', fontsize=12)
    ax.set_ylabel('真实类别', fontsize=12)
    ax.set_title(f'C4.5决策树 - 混淆矩阵 (准确率={metrics["accuracy"]:.4f})', fontsize=14)
    plt.tight_layout()
    plt.savefig('exp4_c45_cm.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [1/3] 混淆矩阵图已保存")
    
    # 8.2 特征重要性
    feature_imp_sorted = feature_imp_df.sort_values('Importance', ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(feature_imp_sorted)))
    ax.barh(feature_imp_sorted['Feature'], feature_imp_sorted['Importance'], color=colors)
    ax.set_xlabel('特征重要性', fontsize=12)
    ax.set_ylabel('特征', fontsize=12)
    ax.set_title('C4.5决策树特征重要性', fontsize=14)
    plt.tight_layout()
    plt.savefig('exp4_c45_importance.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [2/3] 特征重要性图已保存")
    
    # 8.3 决策树结构（前3层）
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(c45, max_depth=3, feature_names=FEATURE_COLS,
              class_names=CLASS_NAMES, filled=True, rounded=True, fontsize=8, ax=ax)
    ax.set_title('C4.5决策树结构（前3层）', fontsize=14)
    plt.tight_layout()
    plt.savefig('exp4_c45_tree.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [3/3] 决策树结构图已保存")


# ============================================
# 主函数
# ============================================
def main():
    """主函数：执行完整的C4.5决策树实验流程"""
    
    print("\n" + "=" * 60)
    print("实验4：C4.5决策树分类算法 - NBA球员位置预测")
    print("=" * 60 + "\n")
    
    # 1. 数据加载与预处理
    X, y = load_and_preprocess_data(DATA_PATH)
    
    # 2. 数据集划分
    X_train, X_test, y_train, y_test = split_dataset(X, y)
    
    # 3. C4.5模型训练
    c45 = train_c45_model(X_train, y_train)
    
    # 4. 模型评估
    y_pred, metrics = evaluate_model(c45, X_test, y_test)
    
    # 5. 特征重要性分析
    feature_imp_df = analyze_feature_importance(c45)
    
    # 6. 交叉验证
    cv_scores = cross_validation(c45, X_train, y_train)
    
    # 7. 决策树规则提取
    extract_tree_rules(c45)
    
    # 8. 可视化
    visualize_results(c45, y_test, y_pred, metrics, feature_imp_df)
    
    print("\n" + "=" * 60)
    print("实验完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
