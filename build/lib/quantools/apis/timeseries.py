import json

from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields
import numpy as np
import pandas as pd

from quantools.timeseries.generateTS import generateArma, fit, generateArima
from quantools.timeseries.nsTest import adfTest, trainFitArima

api = Namespace('timeseries', 'generate data')
# model the input data

#pricer end point
@api.route('/arima/predict')
class predictArma(Resource):
    @api.doc("generate time series of type : AR , MA, ARMA, ARIMA")
    @api.response(200, "Sucess")
    @api.expect(api.model("prediction of ARIMA model : p, d, q",
                          {"p":fields.Integer(min=0),
                           "d":fields.Integer(min=0),
                           "q":fields.Integer(min=0),
                           "train":fields.List(fields.Float),
                           "test" : fields.List(fields.Float)}))
    def post(self):
        """
            predict time series of type : AR, MA, ARMA, ARIMA
            :return time series
        """
        content = request.get_json()
        p = int(content["p"])
        d = int(content["d"])
        q = int(content["q"])
        train = np.asarray(content["train"])
        test = np.asarray(content["test"])
        data = trainFitArima(p,d,q,train,test)
        return jsonify(data)

@api.route('/arima/fit')
class fitArma(Resource):
     @api.doc("fit time series of type : AR , MA, ARMA")
     @api.response(200, "Sucess")
     @api.expect(api.model("fit data according to ARIMA : p,d,q",
                           {"data":fields.List(fields.Float),
                            "p":fields.Integer(min=0),
                            "d":fields.Integer(min=0),
                            "q":fields.Integer(min=0),
                           "trend":fields.String('nc')}))
     def post(self):
         """
         fit the paramater AR, MA and d by MLE
         :return: coefficient theta, phi, aic, bic
         """
         content = request.get_json()
         p = int(content["p"])
         d = int(content["d"])
         q = int(content["q"])
         trend = str(content["trend"])
         if trend=="":
             trend = 'nc'
         data = content["data"]
         result = fit(p,d,q,data, trend=trend)
         param = pd.DataFrame(result.params)[0].to_json()
         val = {"params":json.loads(param),"aic":result.aic,"bic":result.bic,"hqic":result.hqic}
         return jsonify(val)

@api.route('/arima/generate')
class generate(Resource):
    @api.doc("generate time series of type : ARIMA, ARMA, AR and MA")
    @api.response(200, "Sucess")
    @api.expect(api.model("Enter the parameter of the ARIMA model : p,d, q and samples",
                          {"p": fields.List(fields.Float),
                           "q": fields.List(fields.Float),
                           "d" : fields.Integer(min=0),
                           "samples": fields.Integer(min=0)}))
    def post(self):
        """
            generate time series of type : AR, MA, ARMA, ARIMA
            :return time series
        """
        content = request.get_json()
        p = np.asarray(content["p"])
        q = np.asarray(content["q"])
        d= int(content["d"])
        samples = int(content["samples"])
        if d==0:
            return pd.Series(generateArma(p, q, samples)).to_json(orient="values")

        data = generateArima(phi=p, theta=q,d=d,samples= samples)
        return jsonify(pd.Series(data.flatten(-1)).to_json(orient="values"))

@api.route('/istationnary')
class unitary(Resource):
     @api.doc("Augmented dickey-fuller test for non stationnary")
     @api.response(200, "Sucess")
     @api.expect(api.model("ADF test on the data",
                           {"data":fields.List(fields.Float)}))
     def post(self):
        """
            check stationnarity of the time series
            :return true is the time series is stationnary
        """
        content = request.get_json()
        data = content["data"]
        result = adfTest(data)
        return jsonify(result)

@api.route('/boxjenkins')
class BoxJenkins(Resource):
    @api.doc("empty api")
    @api.response(200, "Sucess")
    @api.expect(api.model("data to be estimated",
                          {"data": fields.List(fields.Float)}))
    def post(self):
        content = request.get_json()
        data = content["data"]
        return jsonify("mock api")