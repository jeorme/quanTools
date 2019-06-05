from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import adfuller
from math import sqrt
import numpy as np
import pandas as pd
import json


def adfTest(data):
    result = adfuller(np.asarray(data))
    keys = []
    vals = []
    for key, value in result[4].items():
        keys.append(key)
        vals.append(value)
    isNs = result[1]<=0.05
    output = {
        "isStationnary" : 1.0*isNs,
        "ADF statistic": result[0],
        "p-value : ": result[1],
        "Critical": {
            "0.01": vals[0],
            "0.05": vals[1],
            "0.1": vals[2]
        }
    }
    return output

def trainFitArma(p,q,train,test):
    model = ARIMA(train, order=(p, 0, q))
    model_fit = model.fit(disp=0)
    param = pd.DataFrame(model_fit.params)[0].to_json()
    predictions = model_fit.forecast(steps=len(test))
    error = sqrt(mean_squared_error(test, predictions[0]))
    predic =   pd.DataFrame(predictions[0])[0].to_json()
    return {"params": json.loads(param), "aic": model_fit.aic, "bic": model_fit.bic, "hqic": model_fit.hqic,"error":error,"prediction":json.loads(predic)}

