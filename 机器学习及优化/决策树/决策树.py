import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from math import log
import operator
import random
from random import randrange
from collections import Counter

#导入数据集
train_set=pd.read_csv('oldData/adult.data',header=None,names=['age','workclass','fnlwgt','education',
'education-num','marital-status',
'occupation','relationship','race',
'sex','capital-gain','capital-loss',
'hours-per-week','native-country','income'])
train_set.info()
print(train_set.describe())
test_set=pd.read_csv('oldData/adult.test',header=None,names=['age','workclass','fnlwgt','education',
'education-num','marital-status',
'occupation','relationship','race',
'sex','capital-gain','capital-loss',
'hours-per-week','native-country','income'])
test_set.info()
# print(test_set)

#处理缺失值将含有值' ?'的数据行去掉 注意问号前有一个空格,处理缺失值后数据的index 变成不是连续的
for i in train_set.columns:
    test_set=test_set[test_set[i]!=' ?']
    train_set=train_set[train_set[i]!=' ?']

#重新规划数据集的index
test_set.index=range(0,len(test_set))
train_set.index=range(0,len(train_set))
# print(train_set)
# print(test_set)

#删除fnlgwt 列,序号列
train_set.drop('fnlwgt',axis=1,inplace=True)
test_set.drop('fnlwgt',axis=1,inplace=True)

#Eductaion 和EduNum 特征相似,可以删除Education
train_set.drop(['education'],axis=1,inplace=True)
test_set.drop(['education'],axis=1,inplace=True)

num_cols = ['age', 'capital-gain', 'capital-loss', 'hours-per-week', 'education-num']
for col in num_cols:
    # errors='coerce' 会将无法转换的值转为 NaN，随后用 fillna(0) 填充，最后转为 int
    train_set[col] = pd.to_numeric(train_set[col], errors='coerce').fillna(0).astype(int)
    test_set[col] = pd.to_numeric(test_set[col], errors='coerce').fillna(0).astype(int)

#m,n 分别为训练集和测试集的行数
m=train_set.shape[0]
n=test_set.shape[0]

#1.将age 属性划分为0-25 25-50 50-75 75-100
age=np.copy(train_set['age'])
age_test=np.copy(test_set['age'])

def transform1(age,size):
    for i in range(size):
        if age[i]>=0 and age[i]<25:
            age[i]=0
        elif age[i]>=25 and age[i]<50:
            age[i]=1
        elif age[i]>=50 and age[i]<75:
            age[i]=2
        elif age[i]>=75:
            age[i]=3
    return age
age=transform1(age,m)
age_test=transform1(age_test,n)
train_set['age']=age
test_set['age']=age_test

#2.将capital-gain 属性 >0 的值都用1 替换 =0 的值都用0 替换
gain=np.copy(train_set['capital-gain'])
gain_test=np.copy(test_set['capital-gain'])

def transform2(gain,size):
    for i in range(size):
        if gain[i]==0:
            gain[i]=0
        elif gain[i]>0:
            gain[i]=1
    return gain
gain=transform2(gain,m)
gain_test=transform2(gain_test,n)
train_set['capital-gain']=gain
test_set['capital-gain']=gain_test
# print(train_set['capital-gain'])

#3.将captional-loss 属性划分为>0 =0 两类
loss=np.copy(train_set['capital-loss'])
loss_test=np.copy(test_set['capital-loss'])
loss=transform2(loss,m)
loss_test=transform1(loss_test,n)
train_set['capital-loss']=loss
test_set['capital-loss']=loss_test
# print(train_set['capital-loss'])

#4.将housr-per-week 划分为 <40 ==40 >40
hours=np.copy(train_set['hours-per-week'])
hours_test=np.copy(test_set['hours-per-week'])

def transform3(hours,size):
    for i in range(size):
        if hours[i] < 40:
            hours[i] = 0
        elif hours[i] == 40:
            hours[i] = 1
        elif hours[i] >40:
            hours[i]=2
    return hours
hours=transform3(hours,m)
hours_test=transform3(hours_test,n)
train_set['hours-per-week']=hours
test_set['hours-per-week']=hours_test
# print(train_set['hours-per-week'])

#5.将Country 划分为USA not USA 两类
cty=np.copy(train_set['native-country'])
cty_test=np.copy(test_set['native-country'])

def transform4(cty,size): #多了个空格的问题
    for i in range(size):
        if cty[i] ==" United-States":
            cty[i] = 0
        elif cty[i] != " United-States":
            cty[i] = 1
    return cty
cty=transform4(cty,m)
cty_test=transform4(cty_test,n)
train_set['native-country']=cty
test_set['native-country']=cty_test
# print(train_set['native-country'])
# # print(train_set.info())
# print(train_set)

#6.将workclass 分为Freelance other Proprietor Private Government 五类
# print(train_set['workclass'].value_counts())
workclass=np.copy(train_set['workclass'])
workclass_test=np.copy(test_set['workclass'])

def transform6(workclass,size): #多了个空格的问题
    for i in range(size):
        if workclass[i]==" Federal-gov" or workclass[i]== " Local-gov" or workclass[i]== " State-gov":
            workclass[i] = " Government"
        elif workclass[i] == " Self-emp-not-inc" or workclass[i]==" Self-emp-inc":
            workclass[i] = " Proprietor"
    return workclass
cty=transform6(workclass,m)
cty_test=transform6(workclass_test,n)
train_set['workclass']=workclass
test_set['workclass']=workclass_test
# print(train_set['workclass'])
# print(train_set.info())
# print(train_set)
# print(train_set['workclass'].value_counts())

#7.将education-num 分为0-5:0 5-10:1 >=10:2
edu=np.copy(train_set['education-num'])
edu_test=np.copy(test_set['education-num'])

def transform5(edu,size): #多了个空格的问题
    for i in range(size):
        if edu[i] <5:
            edu[i] = 0
        elif edu[i]>=5 and edu[i]<10:
            edu[i] = 1
        elif edu[i]>=10:
            edu[i]=2
    return edu
edu=transform5(edu,m)
edu_test=transform5(edu_test,n)
train_set['education-num']=edu
test_set['education-num']=edu_test
# # print(train_set['education-num'])

#8.将maritial_status 分为两类married not-married
print(train_set['marital-status'].value_counts())
mari=np.copy(train_set['marital-status'])
mari_test=np.copy(test_set['marital-status'])

def transform8(mari,size): #多了个空格的问题
    for i in range(size):
        if mari[i]==" Divorced" or mari[i]==" Never-married" or mari[i]==" Separated" or mari[i]==" Widowed":
            mari[i]=" not-married"
        else:
            mari[i]=" married"
    return mari
mari=transform8(mari,m)
mari_test=transform8(mari_test,n)
train_set['marital-status']=mari
test_set['marital-status']=mari_test

#9.将occupation 分为High Med Low 三类
occu=np.copy(train_set['occupation'])
occu_test=np.copy(test_set['occupation'])

def transform9(occu,size): #多了个空格的问题
    for i in range(size):
        if occu[i]==" Prof-specialty" or occu[i]==" Exec-managerial":
            occu[i]=" High"
        elif occu[i]==" Tech-support" or occu[i]==" Transport-moving" or \
        occu[i]==" Protective-serv" or occu[i]==" Sales" or occu[i]==" Craft-repair" \
        or occu[i]==" Armed-Forces":
            occu[i]=" Med"
        else:
            occu[i]=" Low"
    return occu
occu=transform9(occu,m)
occu_test=transform9(occu_test,n)
train_set['occupation']=occu
test_set['occupation']=occu_test
# print(train_set.info())
# print(train_set)
# print(train_set['occupation'].value_counts())

#10.将relationship 分为Husband Other Wife
reship=np.copy(train_set['relationship'])
reship_test=np.copy(test_set['relationship'])

def transform7(reship,size): #多了个空格的问题
    for i in range(size):
        if reship[i]!=" Husband" and reship[i]!=" Wife":
            reship[i] = " Other"
    return reship
reship_test=transform7(reship_test,n)
reship=transform7(reship,m)
train_set['relationship']=reship
test_set['relationship']=reship_test
# print(train_set.info())
# print(train_set)
# print(train_set['relationship'].value_counts())

#11.将race 分为两类 White 和Other
race=np.copy(train_set['race'])
race_test=np.copy(test_set['race'])

def transform10(race,size): #多了个空格的问题
    for i in range(size):
        if race[i]!=" White":
            race[i] = " Other"
    return race
race=transform10(race,m)
race_test=transform10(race_test,n)
train_set['race']=race
test_set['race']=race_test

#对income 属性列(即标签列)进行标签编码
label_encoder=LabelEncoder()
train_set['income']=label_encoder.fit_transform(train_set['income'])
test_set['income'] = label_encoder.fit_transform(test_set['income'])

#将测试集转为列表,并将测试集上的标签列存储在y_test 中
y_test=test_set['income'].values.tolist()
y_train=train_set['income'].values.tolist()
# train_set = train_set.values.tolist()
test_set = test_set.values.tolist()
#-----------数据预处理完毕

#-----------------------决策树-----------------------#如果我把这些数据都转变为0,1,2,那么如果拿到一条新的测试数据,我就得先将它转成离散值的 形式,然后再进行决策树算法的判断
##创建数据集
def createDataSet():
    dataSet=train_set.values.tolist()
    featureName=['age','workclass','education-num','marital-status','occupation','relationship','race','sex',
    'capital-gain','capital-loss','hours-per-week','native-country','income']
    # 返回数据集和每个维度的名称
    return dataSet, featureName

##分割数据集
def splitDataSet(dataSet,axis,value):
    """ 按照给定特征划分数据集 :param axis:划分数据集的特征的维度 特征维度的名称 :param value:特征的值 :return: 符合该特征的所有实例(并且自动移除掉这维特征)
    """
    # 循环遍历dataSet 中的每一行数据
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reduceFeatVec = featVec[:axis] # 删除这一维特征
            reduceFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reduceFeatVec)
    return retDataSet

##计算训练数据集中的Y 随机变量的香农熵(信息熵)
def calcShannonEnt(dataSet):
    numEntries = len(dataSet) # 实例的个数
    labelCounts = {}
    for featVec in dataSet: # 遍历每个实例,统计标签的频次
        currentLabel = featVec[-1] # 表示最后一列
        # 当前标签不在labelCounts map 中,就让labelCounts 加入该标签
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] =0
        labelCounts[currentLabel] +=1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        shannonEnt -= prob * log(prob,2) # log base 2
    return shannonEnt

## 计算条件熵
def calcConditionalEntropy(dataSet,i,featList,uniqueVals):
    """ 计算x_i 给定的条件下,Y 的条件熵 :param dataSet: 数据集 :param i: 维度i :param featList: 数据集特征列表 :param unqiueVals: 数据集特征集合 该维度i 所有出现的值 :return: 条件熵
    """
    ce = 0.0
    for value in uniqueVals:
        subDataSet = splitDataSet(dataSet,i,value)
        prob = len(subDataSet) / float(len(dataSet)) # 极大似然估计概率
        ce += prob * calcShannonEnt(subDataSet) #∑pH(Y|X=xi) 条件熵的计算
    return ce

##计算信息增益
def calcInformationGain(dataSet,baseEntropy,i):
    """ :param dataSet: 数据集 :param baseEntropy: 数据集中Y 的信息熵 :param i: 特征维度i :return: 特征i 对数据集的信息增益g(dataSet | X_i)
    """
    featList = [example[i] for example in dataSet] # 第i 维特征列表
    uniqueVals = set(featList) # 换成集合- 集合中的每个元素不重复
    newEntropy = calcConditionalEntropy(dataSet,i,featList,uniqueVals)#计算条件熵,
    infoGain = baseEntropy - newEntropy # 信息增益= 信息熵- 条件熵
    return infoGain

## 选择最好的数据特征划分,返回最佳特征对应的维度index
def chooseBestFeatureToSplitByID3(dataSet):
    numFeatures = len(dataSet[0]) -1 # 最后一列是分类 特征维度的数量
    baseEntropy = calcShannonEnt(dataSet) #返回整个数据集的信息熵
    bestInfoGain = 0.0
    bestFeature = -2 #用来记录信息增益最大的特征的索引值,注意不要用-1,若是bestInfoGain 一 直没有变化,进行划分的就是分类列了
    for i in range(numFeatures): # 遍历所有维度特征
        infoGain = calcInformationGain(dataSet,baseEntropy,i) #返回具体特征的信息增益
        # print(infoGain)
        if(infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature # 返回最佳特征对应的维度

#计算classList 中出现次数最多的元素
def majorityCnt(classList):
    classCount = {}
    for vote in classList: #统计classList 中每个元素出现的次数
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.items(), key = operator.itemgetter(1), reverse = True) #根据字 典的值降序排序
    return sortedClassCount[0][0] #返回classList中出现次数最多的元素

#创建决策树
def createTree(dataSet,featureName,chooseBestFeatureToSplitFunc = chooseBestFeatureToSplitByID3):
    """ 创建决策树 :param dataSet: 数据集 :param featureName: 数据集每一维的名称 :return: 决策树
    """
    classList = [example[-1] for example in dataSet] # 类别列表
    if classList.count(classList[0]) == len(classList): # 统计属于列别classList[0]的个数
        return classList[0] # 当类别完全相同则停止继续划分
    if len(dataSet[0]) ==1: # 当只有一个特征的时候,遍历所有实例返回出现次数最多的类别 即特 征为类别时
        return majorityCnt(classList) # 返回类别标签
    bestFeat = chooseBestFeatureToSplitFunc(dataSet)#最佳特征对应的索引
    bestFeatLabel = featureName[bestFeat] #最佳特征的名称
    myTree ={bestFeatLabel:{}} # map 结构,且key 为featureLabel
    del (featureName[bestFeat]) # 找到需要分类(最佳特征)的特征子集
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = featureName[:] # 复制操作将最佳特征删除后的featureName
        #递归调用createTree函数
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet,bestFeat,value),subLabels)
    return myTree

# 测试决策树的构建
dataSet,featureName = createDataSet()
#创建决策树
myTree = createTree(dataSet,featureName)
# print(myTree)
# print(test_set[0])

def classify(inputTree,featLabels,testVec):
    #字典中的第一个键firstStr
    firstStr = list(inputTree.keys())[0]
    secondDict = inputTree[firstStr]
    #在featLabels 找到该键对应在测试集上的属性列index
    featIndex = featLabels.index(firstStr)
    #测试数据中该属性列的具体值
    key = testVec[featIndex]
    #当该值不在字典中存在时,用该键firstStr 的存在的其他值替换该值,用其他存在值的分类结 果代替
    if key not in secondDict:
        key=list(secondDict.keys())[0]
    valueOfFeat = secondDict[key]
    if isinstance(valueOfFeat, dict):
        classLabel = classify(valueOfFeat, featLabels, testVec)
    else:
        classLabel = valueOfFeat
    return classLabel

featLabels=['age','workclass','education-num','marital-status','occupation','relationship','race','sex',
'capital-gain','capital-loss','hours-per-week','native-country','income']
featLabels_train=['age','workclass','education-num','marital-status','occupation','relationship','race','sex',
'capital-gain','capital-loss','hours-per-week','native-country','income']
classList=[] #用来装预测分类结果
classList_train=[] #用来装训练集上的预测分类结果

for i in range(len(test_set)):
    classLabel = classify(myTree, featLabels, test_set[i])
    classList.append(classLabel)

for i in range(len(dataSet)):
    #计算训练集上的准确率
    classLabel_train = classify(myTree, featLabels_train, dataSet[i])
    classList_train.append(classLabel_train)

correct_num=0
for i in range(n):
    # y_test[i].replace('.',"")
    # print(y_test[i])
    if(classList[i]==y_test[i]):
        correct_num+=1
rate=correct_num/n
print('决策树准确率:',rate)

#计算准确率
correct_num_train=0
for i in range(m):
    if(classList_train[i]==y_train[i]):
        correct_num_train+=1
rate_train=correct_num_train/m
print('决策树训练集上准确率:',rate_train)

#计算AUC 值
from sklearn.metrics import roc_auc_score
auc_score=roc_auc_score(y_test,classList)
print('决策树AUC 值:',auc_score)

n_features = 8 #特征属性个数
#---------------------------- 随机森林的创建
n_trees = 10 #子决策树个数

# 随机构造数据子集
def get_subsample(dataSet):
    subdataSet = []
    lenSubdata = len(dataSet)
    while len(subdataSet) < lenSubdata:
        index = randrange(len(dataSet) - 1)
        subdataSet.append(dataSet[index])
    return subdataSet

#随机n_features 个特征
def get_subfeature(featLabels,n_features):
    subFeature=[]
    subFeatIndex=random.sample(range(0,len(featLabels)-1),n_features)
    for i in range(len(subFeatIndex)):
        subFeature.append(featLabels[subFeatIndex[i]])
    subFeature.append('income')
    subFeatIndex.append(12)
    return subFeature,subFeatIndex

#从数据子集中选出随机的n_features,构成最终进行决策树构建的数据集
def generateDataSet(dataSet,featLabels,n_features):
    subdataSet=get_subsample(dataSet)
    subFeature,subFeatIndex=get_subfeature(featLabels,n_features)
    print(subFeature,subFeatIndex)
    final_subData=[]
    for i in range(len(subdataSet)):
        row_list = []
        for j in range(n_features+1):
            row_list.append(subdataSet[i][subFeatIndex[j]])
        final_subData.append(row_list)
    return final_subData,subFeature

#构建随机森林,用TreeList 来存储
TreeList=[]
def RandomForest(dataSet,n_trees):
    for i in range(n_trees):
        final_subData,subFeature=generateDataSet(dataSet,featLabels,n_features)
        myTree=createTree(final_subData,subFeature)
        print(myTree)
        TreeList.append(myTree)
    return TreeList

RandomForest(dataSet,n_trees)
# print(len(TreeList))

#predList 用来装每条测试集上的数据在各个子决策树上的分类结果,列表中的每个元素代表某条数 据在各个子决策树上的分类结果
predList=[]
def cal(TreeList):
    for j in range(len(test_set)):
        #classList1 用来装某条数据集在各个子决策树上的分类结果
        classList1=[]
        for i in range(len(TreeList)):
            #调用classify函数判断在子决策树上的分类
            classLabel1 = classify(TreeList[i], featLabels, test_set[j])
            # print(classLabel,i)
            classList1.append(classLabel1)
        predList.append(classList1)
cal(TreeList)
# print(len(predList))

#true_pred 用来装每条数据的最终分类结果
true_pred=[]
collection_words_list=[]
for i in range(len(test_set)):
    #调用Counter 计算某条数据在各子决策树的分类结果中,票数统计情况,按照票数从高到低排 列分类结果
    collection_words_list.append(Counter(predList[i]))
    #取第一个分类结果,即票数最高的分类结果
    true_pred.append(list(collection_words_list[i].keys())[0])
# print(true_pred)

#计算准确率
correct_num1=0
for i in range(n):
    if(true_pred[i]==y_test[i]):
        correct_num1+=1
rate1=correct_num1/n
print('随机森林准确率为:',rate1)

#计算AUC 值
auc_score1=roc_auc_score(y_test,true_pred)
print('随机森林AUC值:',auc_score1)