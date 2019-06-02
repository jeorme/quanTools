from ibm_botocore.client import Config
import ibm_boto3


from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields, reqparse, Namespace
from flask_cors import CORS

import os


api = Namespace('pricer', 'pricer of trade')
# model the input data
model_input = api.model('Enter the repo trade:', { "name" : fields.String
                                                   })

#pricer end point
@api.route('/price')
class price(Resource):
    @api.response(200, "Success", model_input)
    @api.expect(model_input)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('notional', type=float)
        parser.add_argument('fixedRate', type=float)
        parser.add_argument('basis', type=str)
        parser.add_argument('paymentDate', type=str)
        parser.add_argument('startDate', type=str)
        parser.add_argument('endDate', type=str)
        parser.add_argument('discountCurve', type=str)
        parser.add_argument('name', type=str)
        args = parser.parse_args()
        tradeID = str(args["name"])
        if tradeID == "None":
            notional = float(args["notional"])
            rate = float(args["fixedRate"])
            basis = str(args["basis"])
            paymentDate = str(args["paymentDate"])
            startDate = str(args["startDate"])
            endDate = str(args["endDate"])
            discountCurve = str(args["discountCurve"])
            npv = RepoPricer(notional, rate, paymentDate, startDate, endDate, discountCurve, basis)
        else:
            npv = RepoPricerData(tradeID)

        return jsonify({"npv": npv})
