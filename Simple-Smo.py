import numpy as np
from numpy import *
import pandas as pd
import random
from sklearn.datasets import load_iris
import matplotlib
import matplotlib.pyplot as plt

# 鸢尾花(iris)数据集
# 数据集内包含 3 类共 150 条记录，每类各 50 个数据，
# 每条记录都有 4 项特征：花萼长度、花萼宽度、花瓣长度、花瓣宽度，
# 可以通过这4个特征预测鸢尾花卉属于（iris-setosa, iris-versicolour, iris-virginica）中的哪一品种。
# 这里只取前100条记录，两项特征，两个类别。
def create_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['label'] = iris.target
    df.columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'label']
    data = np.array(df.iloc[:100, [0, 1, -1]])
    for i in range(len(data)):
        if data[i,-1] == 0:
            data[i,-1] = -1
     #print(data)
    return data[:,:2], data[:,-1]             #坐标  标签


# 用于调整大于H或小于L的alpha值
def clipAlpha(aj, H, L):
    if aj > H:
        aj = H
    if L > aj:
        aj = L
    return aj

def SMO(Input_data, Lable, C, toler, maxIter):  # 数据集、类别标签、常数C、容错率和退出前最大的循环次数
    dataMat = mat(Input_data)  # 将数据集用mat函数转换为矩阵
    labelMat = mat(Lable).transpose()  # 转置类别标签（使得类别标签向量的每行元素都和数据矩阵中的每一行一一对应）
    b = 0
    m, n = shape(dataMat)  # m是数据个数
    alphas = mat(zeros((m, 1)))  # 构建一个保存alpha的列矩阵，初始化为0
    iter = 0  # 建立一个iter变量（该变量存储在没有任何alpha改变的情况下遍历数据集的次数，当该变量达到输入值maxIter时，函数结束）
    while (iter < maxIter):  # 遍历数据集的次数小于输入的maxIter
        alphaPairsChanged = 0  # 用于记录alpha是否已经进行优化，先设为0
        for i in range(m):  # 顺序遍历整个集合
            gxi = float(multiply(alphas, labelMat).T * (dataMat[i, :] * dataMat.T).T) + b  # g(xi)=αi*yi*K(xi,x)+b 预测值
            Ei = gxi - float(labelMat[i])  # 计算误差，预测结果和真实结果的误差

            if ((labelMat[i] * Ei < -toler)&(alphas[i] < C)) or (
                    (labelMat[i] * Ei > toler)&(alphas[i] > 0)):  # 如果误差过大，那么对该数据实例对应的alpha值进行优化
                j = int(random.uniform(0, m))  # 随机选取alpha2
                gxj = float(multiply(alphas, labelMat).T * (dataMat[j, :] * dataMat.T).T) + b
                Ej = gxj - float(labelMat[j])  # 计算误差（同第一个alpha值的误差计算方法）
                alphaI_old = alphas[i].copy()  # 复制，为了稍后对新旧alpha值进行比较
                alphaJ_old = alphas[j].copy()
                # 保证alpha值在0与C之间
                if (labelMat[i] != labelMat[j]):  #y1==y2
                    L = max(0, alphas[j] - alphas[i])
                    H = min(C, C + alphas[j] - alphas[i])
                else:                             #y1!=y2
                    L = max(0, alphas[j] + alphas[i] - C)
                    H = min(C, alphas[j] + alphas[i])
                if L == H:
                    # print("L==H")
                    continue  # 本次循环结束，进入下一次for循环
                eta = 2.0 * dataMat[i, :] * dataMat[j, :].T - \
                      dataMat[i, :] * dataMat[i, :].T - dataMat[j, :] * dataMat[j, :].T  # alpha值的最优修改值
                if eta >= 0:
                    # print("eta >= 0")
                    continue

                alphas[j] -= labelMat[j] * (Ei - Ej) / eta  # 计算出新的alpha2,定理7.6
                alphas[j] = clipAlpha(alphas[j], H, L)  # 调用clipAlpha辅助函数以及L,H值对其进行调整

                if (abs(alphas[j] - alphaJ_old) < 0.00001):  # 检查alpha[j]是否有轻微改变，如果是的话，就退出for循环
                    # print("J not moving enough!")
                    continue
                alphas[i] += labelMat[j] * labelMat[i] * (alphaJ_old - alphas[j])  # 对alpha[i]进行同样的改变，改变大小一样方向相反

                # bi(new) = -Ei  - y1*K1i(alpha1(new)-alpha1(old))-y2*K2i(alpha2(new)-alpha2(old)) + b(old)
                b1 = -Ei - labelMat[i] * (alphas[i] - alphaI_old) * dataMat[i, :] * dataMat[i, :].T - \
                     labelMat[j] * (alphas[j] - alphaJ_old) * dataMat[i, :] * dataMat[j, :].T + b
                b2 = -Ej - labelMat[i] * (alphas[i] - alphaI_old) * dataMat[i, :] * dataMat[j, :].T - \
                     labelMat[j] * (alphas[j] - alphaJ_old) * dataMat[j, :] * dataMat[j, :].T + b
                if (0 < alphas[i]) and (C > alphas[i]):
                    b = b1
                elif (0 < alphas[j]) and (C > alphas[j]):
                    b = b2
                else:
                    b = (b1 + b2) / 2.0

                alphaPairsChanged += 1  # 当for循环运行到这一行，说明已经成功的改变了一对alpha值，同时让alphaPairsChanged加1
                # print("iter:%d i:%d,pairs changed %d" % (iter, i, alphaPairsChanged))
        # for循环结束后，检查alpha值是否做了更新
        if (alphaPairsChanged == 0):  # 如果没有，iter加1
            iter += 1  # 下面后回到while判断
        else:  # 如果有更新则iter设为0后继续运行程序
            iter = 0
        # print("iteration number: %d" % iter)
    return b, alphas  # （只有在所有数据集上遍历maxIter次，且不再发生任何alpha值修改之后，程序才会停止，并退出while循环）


dataArr, labelArr = create_data()
# 测试
b, alphas = SMO(dataArr, labelArr, 0.6, 0.0001, 100)
# print(b)
# print(alphas[alphas > 0])  # 观察元素大于0的
shape(alphas[alphas > 0])  # 得到支持向量的个数

# for i in range(100):
#     if alphas[i] > 0.0:
#         print("简单版支持向量为:", dataArr[i], labelArr[i])

def calculate_Ws(alphas, dataArr, Labels):
    X = mat(dataArr)
    labelMat = mat(Labels).transpose()  #处理数据集标签
    m, n = shape(X)
    w = zeros((n, 1))
    for i in range(m):
        w += multiply(alphas[i] * labelMat[i], X[i, :].T)    # w = Σ(α*y*x)
    return w

ws = calculate_Ws(alphas, dataArr, labelArr)
print("Ws",ws)

fig = plt.figure()
ax = fig.add_subplot(111)
plt.title('Support Vectors Marked')
plt.scatter(dataArr[labelArr==-1,0],dataArr[labelArr==-1,1],color='coral')
plt.scatter(dataArr[labelArr==1,0],dataArr[labelArr==1,1],color='paleturquoise')

for i in range(100):      #画出支持向量
    if alphas[i] > 0.0:
        plt.scatter(dataArr[i, 0], dataArr[i, 1], marker='s',edgecolors='black',color='None',linewidths=1)

w0 = ws[0]
w1 = ws[1]
x = arange(3, 8, 0.1)
y = ((-w0 * x - b) / w1)
#print(y)
y = y.reshape(-1,1)
ax.plot(x, y,linewidth=2,color ='cornflowerblue')
# ax.axis([3, 8, 1, 5])
plt.show()