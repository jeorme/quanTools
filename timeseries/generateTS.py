import numpy as np
import statsmodels.api as sm
import pandas as pd
from statsmodels.tsa.arima_process import arma_generate_sample
import matplotlib.pyplot as plt

def generateArma(p,q,sample):
    arparams = np.r_[1, -p]
    maparams = np.r_[1, q]
    return arma_generate_sample(arparams,maparams,sample)

def fit(data,p,d,q,log=False):
    return sm.tsa.ARMA(pd.DataFrame(data),order=(p,d,q)).fit(disp=log)


if __name__=="__main__":
    #global value :
    nobs = 10000

    #AR simulation and test
    arparams = np.array([.75, -.25,.5,-.1])
    sampleAR = generateArma(arparams,[1,0],nobs)
    fig = plt.plot(sampleAR)
    plt.show()
    #estimation
    ar20 = sm.tsa.ARMA(pd.DataFrame(sampleAR), order=(4,0)).fit(disp=False)
    print(ar20.params)
    print(ar20.aic, ar20.bic, ar20.hqic)
    ar11 = sm.tsa.ARMA(pd.DataFrame(sampleAR), order=(2,2)).fit(disp=False)
    print(ar11.params)
    print(ar11.aic, ar11.bic, ar11.hqic)
