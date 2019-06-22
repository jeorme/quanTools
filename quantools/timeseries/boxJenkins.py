import numpy as np
from statsmodels.tsa.stattools import adfuller, acf

from quantools.timeseries.generateTS import generateArma


def difference(dataset,order=1):
    """
    transform a data into difference of order one
    :param dataset:
    :param order of the difference
    :return: the difference data
    """
    diff = list()
    for i in range(order, len(dataset)):
        value = dataset[i] - dataset[i - order]
        diff.append(value)
    return np.array(diff)

def estimateD(data,maxD=5,log=True,tol=0.01):
    """
    estimate the parameter D with non unitary test ADF
    :param data:
    :param maxD to stop the algo
    :return: the value of d
    """
    tmp = data
    for d in range(maxD):
        if log:
            print("ADF test result : "+str(adfuller(np.asarray(tmp))))
        if adfuller(np.asarray(tmp))[1] < tol:
            return d
        tmp = difference(tmp, 1)
    return d

def estimateP(data,maxP=20,log=False,tol=0.01):
    acfVal = acf(data,nlags=maxP)
    return None

def estimateQ(data,maxP=20,log=False,tol=0.01):
    acfVal = acf(data,nlags=maxP)
    return None

def boxjenkins(data, log=False):
    """
    box jenkins algo
    :param data:
    :param log: boolean : true if we want the log False otherwise
    :return: the parameter of the ARIMA model : AR coef MA coef and d
    """
    #step 1 determine the coefficient d by performing diff till stationnary
    #max d= 5
    MAX_D = 5
    MAX_P = 20
    MAX_Q = 20
    d = estimateD(data,maxD=MAX_D,log=log)
    p = estimateP(data,maxP=MAX_P,log=log)
    p = estimateQ(data,maxP=MAX_P,log=log)

if __name__=="__main__":
    data = generateArma(np.array([0]), np.array([.1]), 100)
    print(estimateD(data))