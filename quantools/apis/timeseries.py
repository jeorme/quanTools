import json

from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields
import numpy as np
import pandas as pd

from quantools.timeseries.generateTS import generateArma, fit, generateArima
from quantools.timeseries.nsTest import adfTest, trainFitArma

api = Namespace('timeseries', 'generate data')
# model the input data

#pricer end point
@api.route('/arma/predict')
class predictArma(Resource):
    @api.doc("generate time series of type : AR , MA, ARMA")
    @api.response(200, "Sucess")
    @api.expect(api.model("prediction of ARMA model : p, q",
                          {"p":fields.Integer(min=0),
                           "q":fields.Integer(min=0),
                           "train":fields.List(fields.Float),
                           "test" : fields.List(fields.Float)}))
    def post(self):
        content = request.get_json()
        p = int(content["p"])
        q = int(content["q"])
        train = np.asarray(content["train"])
        test = np.asarray(content["test"])
        data = trainFitArma(p,q,train,test)
        return jsonify(data)

@api.route('/arma/fit/')
class fitArma(Resource):
     @api.doc("generate time series of type : AR , MA, ARMA")
     @api.response(200, "Sucess")
     @api.expect(api.model("fit data according to ARIMA : p,d,q",
                           {"data":fields.List(fields.Float),
                            "p":fields.Integer(min=0),
                            "d":fields.Integer(min=0),
                            "q":fields.Integer(min=0)}))
     def post(self):
         content = request.get_json()
         p = int(content["p"])
         d = int(content["d"])
         q = int(content["q"])
         data = content["data"]
         result = fit(p,d,q,data)
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
        content = request.get_json()
        p = np.asarray(content["p"])
        q = np.asarray(content["q"])
        d= int(content["d"])
        samples = int(content["samples"])
        if d==0:
            return pd.Series(generateArma(p, q, samples)).to_json(orient="values")

        data = generateArima(phi=p, theta=q,d=d,samples= samples)
        return jsonify(pd.Series(data.flatten(-1)).to_json(orient="values"))

@api.route('/ns-test/adf')
class unitary(Resource):
     @api.doc("Augmented dickey-fuller test for non stationnary")
     @api.response(200, "Sucess")
     @api.expect(api.model("fit data according to ARIMA : p,d,q",
                           {"data":fields.List(fields.Float)}))
     def post(self):
         content = request.get_json()
         data = content["data"]
         result = adfTest(data)
         return jsonify(result)
