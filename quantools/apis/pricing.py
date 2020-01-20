import json

from quantools.pricing.mathematicTools import *
from flask import request, jsonify
import numpy as np
import pandas as pd
from flask_restplus import Namespace,Resource, fields
api = Namespace('pricing', 'window barrier')

@api.route('/windowBarrier')
class Pricing(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("data",{"ForeignRate" : fields.Float,"DomesticRate" : fields.Float,"fixedAmount": fields.Float,
                                  "optionType" : fields.String,"cashPercent" : fields.String,"PaymentAt" : fields.String,
                                  "volatility" : fields.Float, "Spot" : fields.Float, "Strike" : fields.Float, "Time" : fields.Float,
                                  "timeToSettle" : fields.Float, "windowBarrierType" : fields.String,"Barrier1Level" : fields.Float,
                                  "Barrier1Rebate": fields.Float,"Barrier1Direction": fields.String,"Barrier1Activaition": fields.String,
                                  "Barrier2Level": fields.Float,
                                  "Barrier2Rebate": fields.Float, "Barrier2Direction": fields.String,
                                  "Barrier2Activaition": fields.String,
                                  "computePrimeOnly" : fields.Boolean,
                                  "hideTraces" : fields.Boolean
        }))
    def post(self):
        """
        pricing Window barrier
        :return: NPV (greeks are not supported right)
        """
        content = request.get_json()
        foreignRate = content["ForeignRate"]
        domesticRate = content["DomesticRate"]
        fixedAmount = content["fixedAmount"]
        # define model
        return jsonify({"total param":foreignRate})

@api.route('/normalCdf')
class normalCDF(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input",{"u" : fields.Float}))
    def post(self):
        """
        normal cdf
        :return: the normal cumulative distribution function
        """
        content = request.get_json()
        u = content["u"]
        cdf = normalCDF(u)
        # define model
        return jsonify({"normal cumulative":cdf})

@api.route('/biNormalCdf')
class biNormalCDF(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input",{"x" : fields.Float,"y" : fields.Float,"rho" : fields.Float,}))
    def post(self):
        """
        normal cdf
        :return: the normal cumulative distribution function
        """
        content = request.get_json()
        x = content["x"]
        y = content["y"]
        rho = content["rho"]
        cdf = bivariateCND(x,y,rho)
        # define model
        return jsonify({"bi normal cumulative":cdf})