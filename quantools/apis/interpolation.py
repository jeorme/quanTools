from datetime import datetime

from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields

from quantools.model.ycModel.ycDef import yieldCurveDef, yieldCurveValues
from yieldCurve import  computeDiscountFactor

api = Namespace('interpolation', 'marketData : FX Vol, Yield Curve')

@api.route('/YC/unitary')
class InterpolationYC(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("interpolation of the yield curve",{"asOfDate":fields.String,"date":fields.String,
    "marketDataDefinitions":fields.Raw(example=yieldCurveDef,type="json"),
          "marketData"   :   fields.Raw(example=yieldCurveValues,type="json")
                                     }))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """
        content = request.get_json()
        values = content["marketData"]["yieldCurveValues"][0]["discountFactors"]
        definition = content["marketDataDefinitions"]["yieldCurves"][0]
        asOf = datetime.strptime(content["asOfDate"],"%Y-%m-%d")
        date = datetime.strptime(content["date"],"%Y-%m-%d")
        df = computeDiscountFactor(values,definition , asOf ,date)
        # define model
        return jsonify({"discountFactors":df})

@api.route('/expiry')
class Expiry(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input of expiry interpolation",{"TBD" : fields.Float}))
    def post(self):
        """
        interpolation : expiry axis
        :return: the interpolated value
        """
        content = request.get_json()
        TBD = content["TBD"]
        # define model
        return jsonify({"TBD":TBD})