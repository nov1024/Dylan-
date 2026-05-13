import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

# 加载数据
try:
    train_df = pd.read_csv('Sample_train.csv')
    test_df = pd.read_csv('test_noLabel.csv')
except FileNotFoundError:
    print("错误：未找到 'Sample_train.csv' 或 'test_noLabel.csv' 文件。")
    # 假设文件已加载

# 打印训练数据信息
print("--- 训练集 (Sample_train.csv) 原始信息 ---")
train_df.info()

# 打印数据前5行
print("\n--- 原始数据 (前5行) ---")
print(train_df.head())
# 1. 分离 Label 标签
y_train = train_df['Label']
# 2. 移除训练集的 Label
train_df = train_df.drop('Label', axis=1)

# 3. 记录训练集和测试集的 ID，用于后续区分
train_ids = train_df['ID']
test_ids = test_df['ID']

# 4. 合并数据
print(f"合并前: 训练集 {train_df.shape}, 测试集 {test_df.shape}")
combined_df = pd.concat([train_df, test_df], axis=0, ignore_index=True)
print(f"合并后: {combined_df.shape}")

# 5. 数据清洗：移除无关列 (在 2.1.2 节中已分析)
irrelevant_cols = ['ID', 'EmployeeNumber', 'Over18', 'StandardHours']
combined_df = combined_df.drop(columns=irrelevant_cols)

print(f"移除无关列后: {combined_df.shape}")
# 1. 识别不同类型的特征
# 二元类别特征 (Binary)
binary_cols = ['Gender', 'OverTime']

# 名义类别特征 (Nominal) - 需要 One-Hot 编码
nominal_cols = ['BusinessTravel', 'Department', 'EducationField', 'JobRole', 'MaritalStatus']

# 2. 处理二元特征 (Label Encoding)
le = LabelEncoder()
for col in binary_cols:
    combined_df[col] = le.fit_transform(combined_df[col])
    # 示例: 'Male' -> 1, 'Female' -> 0; 'Yes' -> 1, 'No' -> 0

print("--- 二元特征编码后 (Gender, OverTime) ---")
print(combined_df[['Gender', 'OverTime']].head())

# 3. 处理名义特征 (One-Hot Encoding)
print(f"\n独热编码前形状: {combined_df.shape}")
combined_df = pd.get_dummies(combined_df, columns=nominal_cols, drop_first=False)
print(f"独热编码后形状: {combined_df.shape}")
# 1. 识别所有数值特征
# (原始的数值列 + 编码后的二元列)
# 独热编码生成的列已经是0/1，不需要缩放
numerical_cols = [
    'Age', 'DistanceFromHome', 'Education', 'EnvironmentSatisfaction',
    'Gender', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
    'MonthlyIncome', 'NumCompaniesWorked', 'OverTime', 'PercentSalaryHike',
    'PerformanceRating', 'RelationshipSatisfaction', 'StockOptionLevel',
    'TotalWorkingYears', 'TrainingTimesLastYear', 'WorkLifeBalance',
    'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
    'YearsWithCurrManager'
]

print(f"--- 缩放前 (Age, MonthlyIncome) ---")
print(combined_df[['Age', 'MonthlyIncome']].describe())

# 2. 初始化 StandardScaler
scaler = StandardScaler()

# 3. 关键：只在训练集数据上 (前1100行) 'fit' (计算均值和标准差)
# 这样可以防止测试集的信息 "泄露" 到训练过程中
scaler.fit(combined_df.loc[:len(train_ids)-1, numerical_cols])

# 4. 在 'combined_df' (训练集+测试集) 上 'transform'
combined_df[numerical_cols] = scaler.transform(combined_df[numerical_cols])

print(f"\n--- 缩放后 (Age, MonthlyIncome) ---")
print(combined_df[['Age', 'MonthlyIncome']].describe())
# 1. 分离数据
X_train_processed = combined_df.iloc[:len(train_ids)]
X_test_processed = combined_df.iloc[len(train_ids):]

# 2. 检查形状是否正确
print(f"处理后的训练集 X_train: {X_train_processed.shape}")
print(f"处理后的训练集 y_train: {y_train.shape}")
print(f"处理后的测试集 X_test: {X_test_processed.shape}")

# 3. 展示处理后的最终数据
print("\n--- 最终处理完毕的训练集 (前5行) ---")
print(X_train_processed.head())