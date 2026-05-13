#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验1：贝叶斯分类
使用NBA球员赛季统计数据，基于高斯朴素贝叶斯分类器预测球员位置
数据集：NBA_Season_Stats.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler, LabelEncoder, label_binarize
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report,
                             roc_curve, auc)
import warnings

warnings.filterwarnings('ignore')

# ============================================
# 中文字体配置
# ============================================
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# ============================================
# 配置参数
# ============================================
DATA_PATH = 'NBA_Season_Stats.csv'  # 数据集路径
TEST_SIZE = 0.3  # 测试集比例
RANDOM_STATE = 42  # 随机种子
CV_FOLDS = 5  # 交叉验证折数

# 选择的特征列
FEATURE_COLS = ['Age', 'G', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%',
                '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

# 目标变量
TARGET_COL = 'Pos'


# ============================================
# 1. 数据加载与预处理
# ============================================
def load_and_preprocess_data(filepath):
    """
    加载数据并进行预处理

    参数:
        filepath: 数据集文件路径
    返回:
        X: 特征矩阵
        y: 标签向量
        label_encoder: 标签编码器
    """
    print("=" * 60)
    print("1. 数据加载与预处理")
    print("=" * 60)

    # 加载数据
    df = pd.read_csv(filepath)
    print(f"数据集原始形状: {df.shape}")

    # 查看目标变量分布
    print(f"\n目标变量 {TARGET_COL} 分布:")
    print(df[TARGET_COL].value_counts())

    # 提取特征和标签
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()

    # 处理缺失值 - 用中位数填充
    missing_before = X.isnull().sum().sum()
    X = X.fillna(X.median())
    missing_after = X.isnull().sum().sum()
    print(f"\n缺失值处理: {missing_before} -> {missing_after}")

    # 标签编码
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    print(f"\n标签编码对应关系:")
    for i, cls in enumerate(label_encoder.classes_):
        print(f"  {cls} -> {i}")

    return X, y_encoded, label_encoder


# ============================================
# 2. 数据集划分
# ============================================
def split_dataset(X, y):
    """
    将数据集划分为训练集和测试集

    参数:
        X: 特征矩阵
        y: 标签向量
    返回:
        X_train, X_test, y_train, y_test: 划分后的数据集
    """
    print("\n" + "=" * 60)
    print("2. 数据集划分")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"训练集样本数: {len(X_train)} ({len(X_train) / len(X) * 100:.1f}%)")
    print(f"测试集样本数: {len(X_test)} ({len(X_test) / len(X) * 100:.1f}%)")

    return X_train, X_test, y_train, y_test


# ============================================
# 3. 特征标准化
# ============================================
def scale_features(X_train, X_test):
    """
    对特征进行标准化处理

    参数:
        X_train: 训练集特征
        X_test: 测试集特征
    返回:
        X_train_scaled, X_test_scaled, scaler: 标准化后的特征和标准化器
    """
    print("\n" + "=" * 60)
    print("3. 特征标准化")
    print("=" * 60)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("特征标准化完成")
    print(f"训练集特征均值(前5个): {X_train_scaled.mean(axis=0)[:5]}")
    print(f"训练集特征标准差(前5个): {X_train_scaled.std(axis=0)[:5]}")

    return X_train_scaled, X_test_scaled, scaler


# ============================================
# 4. 模型训练
# ============================================
def train_gaussian_nb(X_train, y_train):
    """
    训练高斯朴素贝叶斯分类器

    参数:
        X_train: 训练集特征
        y_train: 训练集标签
    返回:
        gnb: 训练好的高斯朴素贝叶斯模型
    """
    print("\n" + "=" * 60)
    print("4. 高斯朴素贝叶斯模型训练")
    print("=" * 60)

    gnb = GaussianNB()
    gnb.fit(X_train, y_train)

    print("模型训练完成!")
    print(f"\n模型参数:")
    print(f"  类别数量: {len(gnb.classes_)}")
    print(f"  类别先验概率:")
    for i, cls in enumerate(gnb.classes_):
        print(f"    类别 {cls}: {gnb.class_prior_[i]:.6f}")

    return gnb


# ============================================
# 5. 模型预测
# ============================================
def predict(gnb, X_test):
    """
    使用训练好的模型进行预测

    参数:
        gnb: 训练好的高斯朴素贝叶斯模型
        X_test: 测试集特征
    返回:
        y_pred: 预测标签
        y_prob: 预测概率
    """
    print("\n" + "=" * 60)
    print("5. 模型预测")
    print("=" * 60)

    y_pred = gnb.predict(X_test)
    y_prob = gnb.predict_proba(X_test)

    print(f"预测完成，共预测 {len(y_pred)} 个样本")

    return y_pred, y_prob


# ============================================
# 6. 模型评估
# ============================================
def evaluate_model(y_test, y_pred, y_prob, label_encoder):
    """
    评估模型性能

    参数:
        y_test: 真实标签
        y_pred: 预测标签
        y_prob: 预测概率
        label_encoder: 标签编码器
    返回:
        metrics: 评估指标字典
    """
    print("\n" + "=" * 60)
    print("6. 模型评估")
    print("=" * 60)

    # 计算各项评估指标
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    precision_weighted = precision_score(y_test, y_pred, average='weighted')
    recall_weighted = recall_score(y_test, y_pred, average='weighted')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')

    print(f"\n整体评估指标:")
    print(f"  准确率 (Accuracy): {accuracy:.4f}")
    print(f"  宏平均精确率 (Macro Precision): {precision_macro:.4f}")
    print(f"  宏平均召回率 (Macro Recall): {recall_macro:.4f}")
    print(f"  宏平均F1分数 (Macro F1): {f1_macro:.4f}")
    print(f"  加权平均精确率 (Weighted Precision): {precision_weighted:.4f}")
    print(f"  加权平均召回率 (Weighted Recall): {recall_weighted:.4f}")
    print(f"  加权平均F1分数 (Weighted F1): {f1_weighted:.4f}")

    # 详细分类报告
    print(f"\n各类别详细评估:")
    print("-" * 80)
    class_report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        digits=4
    )
    print(class_report)

    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n混淆矩阵:")
    print(f"{'':>5}", end="")
    for cls in label_encoder.classes_:
        print(f"{cls:>8}", end="")
    print()
    for i, cls in enumerate(label_encoder.classes_):
        print(f"{cls:>5}", end="")
        for j in range(len(label_encoder.classes_)):
            print(f"{cm[i][j]:>8}", end="")
        print()

    metrics = {
        'accuracy': accuracy,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'precision_weighted': precision_weighted,
        'recall_weighted': recall_weighted,
        'f1_weighted': f1_weighted,
        'confusion_matrix': cm,
        'classification_report': class_report
    }

    return metrics


# ============================================
# 7. 交叉验证
# ============================================
def cross_validation(gnb, X_train, y_train):
    """
    进行K折交叉验证

    参数:
        gnb: 高斯朴素贝叶斯模型
        X_train: 训练集特征
        y_train: 训练集标签
    返回:
        cv_scores: 交叉验证分数
    """
    print("\n" + "=" * 60)
    print(f"7. {CV_FOLDS}折交叉验证")
    print("=" * 60)

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(gnb, X_train, y_train, cv=cv, scoring='accuracy')

    print(f"{CV_FOLDS}折交叉验证准确率:")
    for i, score in enumerate(cv_scores):
        print(f"  第{i + 1}折: {score:.4f}")
    print(f"\n平均交叉验证准确率: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    return cv_scores


# ============================================
# 8. 可视化分析
# ============================================
def visualize_results(y_test, y_pred, y_prob, label_encoder, metrics, output_dir='./'):
    """
    生成可视化图表

    参数:
        y_test: 真实标签
        y_pred: 预测标签
        y_prob: 预测概率
        label_encoder: 标签编码器
        metrics: 评估指标字典
        output_dir: 输出目录
    """
    print("\n" + "=" * 60)
    print("8. 生成可视化图表")
    print("=" * 60)

    import os
    os.makedirs(output_dir, exist_ok=True)

    cm = metrics['confusion_matrix']
    classes = label_encoder.classes_
    n_classes = len(classes)

    # 8.1 混淆矩阵热力图
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes, ax=ax, annot_kws={"size": 14})
    ax.set_xlabel('预测类别', fontsize=14)
    ax.set_ylabel('真实类别', fontsize=14)
    ax.set_title('贝叶斯分类 - 混淆矩阵', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  [1/4] 混淆矩阵图已保存")

    # 8.2 各类别评估指标柱状图
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    class_precision = precision_score(y_test, y_pred, average=None)
    class_recall = recall_score(y_test, y_pred, average=None)
    class_f1 = f1_score(y_test, y_pred, average=None)

    x = np.arange(n_classes)
    width = 0.6

    bars1 = axes[0].bar(x, class_precision, width, color='steelblue', edgecolor='navy')
    axes[0].set_xlabel('球员位置', fontsize=12)
    axes[0].set_ylabel('精确率 (Precision)', fontsize=12)
    axes[0].set_title('各类别精确率', fontsize=14)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(classes, fontsize=11)
    axes[0].set_ylim(0, 1)
    for bar in bars1:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.3f}', ha='center', va='bottom', fontsize=10)

    bars2 = axes[1].bar(x, class_recall, width, color='coral', edgecolor='darkred')
    axes[1].set_xlabel('球员位置', fontsize=12)
    axes[1].set_ylabel('召回率 (Recall)', fontsize=12)
    axes[1].set_title('各类别召回率', fontsize=14)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(classes, fontsize=11)
    axes[1].set_ylim(0, 1)
    for bar in bars2:
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.3f}', ha='center', va='bottom', fontsize=10)

    bars3 = axes[2].bar(x, class_f1, width, color='mediumseagreen', edgecolor='darkgreen')
    axes[2].set_xlabel('球员位置', fontsize=12)
    axes[2].set_ylabel('F1分数', fontsize=12)
    axes[2].set_title('各类别F1分数', fontsize=14)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(classes, fontsize=11)
    axes[2].set_ylim(0, 1)
    for bar in bars3:
        height = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'class_metrics.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  [2/4] 各类别评估指标图已保存")

    # 8.3 ROC曲线
    y_test_binarized = label_binarize(y_test, classes=range(n_classes))
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_binarized[:, i], y_prob[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    fig, ax = plt.subplots(figsize=(10, 8))
    colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, color in zip(range(n_classes), colors_list):
        ax.plot(fpr[i], tpr[i], color=color, lw=2,
                label=f'{classes[i]} (AUC = {roc_auc[i]:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1.5)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('假正例率 (False Positive Rate)', fontsize=13)
    ax.set_ylabel('真正例率 (True Positive Rate)', fontsize=13)
    ax.set_title('多类别ROC曲线', fontsize=15)
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'roc_curve.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  [3/4] ROC曲线已保存")

    # 8.4 预测概率分布图
    fig, axes = plt.subplots(1, n_classes, figsize=(4 * n_classes, 4))

    for i, cls in enumerate(classes):
        mask = y_test == i
        probs = y_prob[mask, i]

        axes[i].hist(probs, bins=30, color=colors_list[i], edgecolor='black', alpha=0.7)
        axes[i].set_xlabel('预测概率', fontsize=11)
        axes[i].set_ylabel('样本数', fontsize=11)
        axes[i].set_title(f'{cls} - 预测概率分布', fontsize=12)
        axes[i].set_xlim(0, 1)
        axes[i].axvline(np.mean(probs), color='red', linestyle='--',
                        label=f'均值: {np.mean(probs):.3f}')
        axes[i].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'probability_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  [4/4] 预测概率分布图已保存")


# ============================================
# 主函数
# ============================================
def main():
    """主函数：执行完整的贝叶斯分类实验流程"""

    print("\n" + "=" * 60)
    print("实验1：贝叶斯分类 - NBA球员位置预测")
    print("=" * 60 + "\n")

    # 1. 数据加载与预处理
    X, y, label_encoder = load_and_preprocess_data(DATA_PATH)

    # 2. 数据集划分
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    # 3. 特征标准化
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)

    # 4. 模型训练
    gnb = train_gaussian_nb(X_train_scaled, y_train)

    # 5. 模型预测
    y_pred, y_prob = predict(gnb, X_test_scaled)

    # 6. 模型评估
    metrics = evaluate_model(y_test, y_pred, y_prob, label_encoder)

    # 7. 交叉验证
    cv_scores = cross_validation(gnb, X_train_scaled, y_train)

    # 8. 可视化
    visualize_results(y_test, y_pred, y_prob, label_encoder, metrics, output_dir='./output')

    print("\n" + "=" * 60)
    print("实验完成!")
    print("=" * 60)

    return gnb, metrics, label_encoder


if __name__ == '__main__':
    main()