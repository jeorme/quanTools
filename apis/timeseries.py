from ibm_botocore.client import Config
import ibm_boto3


from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields, reqparse, Namespace
from flask_cors import CORS

import os


api = Namespace('timeseries', 'tools for timeseries analysis and forecasting')
# model the input data

#pricer end point
@api.route('/data')
class timeseries(Resource):
    @api.response(200,"Sucess")
    @api.doc("return all the data series stored")
    def get(self):
        pass

    @api.response(200, "Sucess")
    def post(self):
        pass

    @api.response(200, "Sucess")
    def put(self):
        pass

    @api.response(200, "Sucess")
    def delete(self):
        pass
