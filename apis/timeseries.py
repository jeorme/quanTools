from flask import jsonify,request
from flask_restplus import Resource, fields, reqparse, Namespace
import numpy as np
import pandas as pd
import json

from timeseries.generateTS import generateArma, fit

api = Namespace('timeseries', 'generate data')
# model the input data

#pricer end point
@api.route('/generate/arma')
class generateTS(Resource):
    @api.doc("generate time series of type : AR , MA, ARMA")
    @api.response(200, "Sucess")
    @api.expect(api.model("Enter the parameter of the ARIMA model : p, q",
                          {"p":fields.List(fields.Float),
                           "q":fields.List(fields.Float),
                           "samples":fields.Integer(min=0)}))
    def post(self):
        content = request.get_json()
        p = np.asarray(content["p"])
        q = np.asarray(content["q"])
        samples = int(content["samples"])
        data = generateArma(p,q,samples)
        return jsonify(pd.Series(data).to_json(orient="values"))


@api.route('/fit/arima')
class fitTS(Resource):
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
