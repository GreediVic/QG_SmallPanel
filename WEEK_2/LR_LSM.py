# -*- coding:utf-8 -*-

import numpy as np
from sklearn.datasets import load_boston

"""
    导入numpy的包用于计算和处理
    和sklearn.datasets波士顿房价
"""


class LRegression(object):

    def __init__(self):
        """
            初始化模型
            _w:系数(权重)
            coef_:相关系数
            interception_: = 截距
        """
        self._w = None
        self.interception_ = None
        self.coef_ = None

    def Fit_least_squares(self, x_train, y_train):
        """
            采用最小二乘的方法
            计算出各特征值的权重
            相应将w。确定为截距
            后面的全部w都为系数集合（权重）
        """
        assert (x_train.shape[0] == y_train.shape[0])
        if not x_train.shape[0] == y_train.shape[0]:
            raise AssertionError('The shapes are not the same')

        # 特征值矩阵的转置与本身点积后的逆再与特征值的转置点积再与训练集的目标值点积
        x_train = np.mat(x_train)
        y_train = np.mat(y_train)
        x_b = np.mat(np.hstack([np.ones((len(x_train), 1)), x_train]))  # 在x前边加上一列1,使预测函数可以在平面上自由移动
        # try:根据公式计算各类系数：
        self._w = np.mat((x_b.T.dot(x_b))).I \
            .dot(x_b.T).dot(y_train)
        self.coef_ = self._w[1:]
        self.interception_ = self._w[0]
        # except Exception as reason:  # 可能是奇异阵 不可逆()
        #     print(f"WRONG!,its a {reason}")

        return self

    def Predict_least_squares(self, x_test):
        """
            断言：是否先训练了模型
        """
        assert (self.interception_ is not None and self.coef_ is not None)
        if not (self.interception_ is not None and self.coef_ is not None):
            raise AssertionError('You have to use Fit_least_squares(self, x_train, y_train) first ')

        x_test = np.mat(x_test)  # 转为矩阵
        assert (x_test.shape[1] == len(self.coef_))  # 判断是否拥有相同特征数
        if not (x_test.shape[1] == len(self.coef_)):
            raise AssertionError('The feature number of x_predict Matrix should be equal to x_train')

        x_predicted = np.hstack([np.ones((len(x_test), 1)), x_test])
        return np.dot(x_predicted, self._w)  # 返回预测值

    def R_score(self, x_train, y_train):
        """
            R方评价准确度
        """

        def R2_score(y_test, y_predict):
            """
                计算R^2   ( = 1-(RSS/TSS) )
            """
            y_bar = np.mean(y_test)  # 求y均值
            rss = MSE_score(y_test, y_predict) * len(y_predict)  # 误差平方和
            tss = np.sum((y_test - y_bar).T.dot(y_test - y_bar))  # 总离差平方和
            return 1 - rss / tss  # 得到R**2

        def MSE_score(y_test, y_predict):
            """
                计算误差平方和MSE/样本数值
            """
            return np.sum((y_test - y_predict).T.dot((y_test - y_predict))) / len(y_predict)
        y_predict = self.Predict_least_squares(x_train)
        return R2_score(y_train, y_predict)

    def M_score(self, x_train, y_train):
        """
            MSE评价准确度
        """
        def MSE_score(y_test, y_predict):
            """
                计算误差平方和MSE/样本数值
            """
            return np.sum((y_test - y_predict).T.dot((y_test - y_predict))) / len(y_predict)
        y_predict = self.Predict_least_squares(x_train)
        return MSE_score(y_train, y_predict)


if __name__ == '__main__':
    boston = load_boston()
    x_train = np.mat(boston['data'])  # (506, 13)
    y_train = np.mat(boston['target']).T  # 原本方向是这样的(1, 506) 使用的y应该与x的方向一致
    lr = LRegression()
    lr.Fit_least_squares(x_train, y_train)
    pred_y = lr.Predict_least_squares(x_train)
    m = lr.M_score(x_train, y_train)
    r = lr.R_score(x_train, y_train)
    print("--------------------------")
    print("这是均方差：", m)
    print("这是R方：", r)
