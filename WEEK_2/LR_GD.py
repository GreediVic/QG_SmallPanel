# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

class LRegression(object):

    def __init__(self):
        self.theta = None
        self.coef_ = None
        self.interception_ = None

    def Fit_gradients_get_theta(self, x_train, y_train):
        """
            采用梯度下降的方法
            计算出使得loss最小的theta
        """
        assert (x_train.shape[0] == y_train.shape[0])
        if not x_train.shape[0] == y_train.shape[0]:
            raise AssertionError('The shapes are not equal')

        def J(theta, x_b, y_train):
            try:
                return np.sum((y_train - x_b.dot(theta)).dot((y_train - x_b.dot(theta)).T)) / len(x_b)
            except:
                return float('inf')
            return float('inf')

        def alpha_J(theta, x_b, y_train):
            result = x_b.T.dot(x_b.dot(theta) - y_train)*2. / len(y_train)
            print(f"测试样例有：{len(y_train)} 个")
            return result
# 0.0000015655  9911 -------     #  00000156555
        # 0.0008722134506129464
        def gradients_get_theta(x_b, y_train, initial_theta, eta=0.1, n_iterations=100000, epsilon=1e-8):
            theta = np.mat(initial_theta).T
            for i in range(n_iterations):
                gradient = alpha_J(theta, x_b, y_train)
                last_theta = theta
                theta = theta - eta * gradient
                print(i, "-------")
                print(abs(J(theta, x_b, y_train) - J(last_theta, x_b, y_train)))
                print(gradient)
                if abs(J(theta, x_b, y_train) - J(last_theta, x_b, y_train)) < epsilon:
                    print(f"Find the best theta at {i} times ")
                    break
            return theta

        x_train = np.mat(x_train).T
        y_train = np.mat(y_train).T
        x_b = np.hstack([np.ones((len(x_train), 1)), x_train])  # 在x前边加上一列1,使预测函数可以在平面上自由移动
        initial_theta = np.random.rand(x_b.shape[1])
        self.theta = gradients_get_theta(x_b, y_train, initial_theta)
        self.coef_ = self.theta[1:]
        self.interception_ = self.theta[0]

        return self

    def Predict_GD(self, x_predict):
        """
            断言：是否先训练了模型
        """
        assert (self.interception_ is not None and self.coef_ is not None)
        if not (self.interception_ is not None and self.coef_ is not None):
            raise AssertionError('You have to use Fit_least_squares(self, x_train, y_train) first ')

        x_predict = np.mat(x_predict).T  # 转为矩阵
        assert (x_predict.shape[1] == len(self.coef_))  # 判断是否相同特征数
        if not (x_predict.shape[1] == len(self.coef_)):
            raise AssertionError('The feature number of x_predict Matrix should be equal to x_train')

        x_predicted = np.hstack([np.ones((len(x_predict), 1)), x_predict])

        return np.dot(x_predicted, self.theta)  # 返回预测值

    def R_score(self, x_train, y_train):
        """
            R方评价准确度
        """

        def R2_score(y_test, y_predict):
            """
                计算R^2   ( = 1-(RSS/TSS) )
            """
            y_bar = np.mean(y_test)
            rss = MSE_score(y_test, y_predict) * len(y_predict)
            tss = np.sum((y_test - y_bar).T.dot(y_test - y_bar))
            return 1 - rss / tss

        def MSE_score(y_test, y_predict):
            """
                计算误差平方和MSE
            """
            return np.sum((y_test - y_predict).T.dot((y_test - y_predict))) / len(y_predict)

        y_predict = self.Predict_GD(x_train)
        return R2_score(y_train, y_predict)

    def M_score(self, x_train, y_train):
        """
            MSE评价准确度
        """

        def MSE_score(y_test, y_predict):
            """
                计算误差平方和MSE
            """
            return np.sum((y_test - y_predict).T.dot((y_test - y_predict))) / len(y_predict)

        y_predict = self.Predict_GD(x_train)
        return MSE_score(y_train, y_predict)


if __name__ == '__main__':
    x_train = 2 * np.random.random(size=150)
    y_train = x_train * 3. + 4. + np.random.normal(size=150)
    lr = LRegression()
    lr.Fit_gradients_get_theta(x_train, y_train)
    pred_y = lr.Predict_GD(x_train)
    m = lr.M_score(x_train, y_train)
    r = lr.R_score(x_train, y_train)
    plt.figure(facecolor='w')
    plt.plot(x_train, pred_y, 'r-', linewidth=2, label=u'predict_value')
    plt.scatter(x_train, y_train, label=u'true_value')
    plt.legend(loc='lower right')
    plt.grid(b=True)
    plt.show()
    print("--------------------------")
    print("该算法尚未完善，想要放到github上边。作业是另一项(最小二乘法LR_LSM)")
