from datetime import datetime

from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields

from quantools.library.sabr.sabrInterpolation import sabrInterpolation
from quantools.model.ycModel.ycDef import yieldCurveDef, yieldCurveValues
from quantools.library.fxvolCalibration.yieldCurve import  computeDiscountFactor

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

@api.route('/sabrLogNormal')
class SABRLN(Resource):
    @api.response(200, "Success")
    @api.expect(api.model("input of the logNormal SABR interpolation", {"Forward":fields.Float(default=0.025), "shift":fields.Float(default=0.03), "time":fields.Float(default=1.), "VolAtm":fields.Float(default=0.0040),
                              "beta":fields.Float(default=0.5), "rho":fields.Float(default=-0.2), "volvol":fields.Float(default=0.30),"strike":fields.Float(default = 0.025)}))
    def post(self):
        """
               sabr log normal
               :return: the interpolated value
               """
        content = request.get_json()
        f = content["Forward"]
        shift = content["shift"]
        time = content["time"]
        v_atm_n = content["VolAtm"]
        beta = content["beta"]
        rho = content["rho"]
        volvol = content["volvol"]
        strike = content["strike"]
        # define model
        return jsonify({"vol logNormal": sabrInterpolation(f,shift,time,v_atm_n,beta,rho,volvol,strike,"LN")})

@api.route('/sabrNormal')
class SABRN(Resource):
    @api.response(200, "Success")
    @api.expect(api.model("input of the normal SABR interpolation", {"Forward":fields.Float(default=0.025), "shift":fields.Float(default=0.03), "time":fields.Float(default=1.), "VolAtm":fields.Float(default=0.0040),
                              "beta":fields.Float(default=0.5), "rho":fields.Float(default=-0.2), "volvol":fields.Float(default=0.30),"k":fields.Float(default = 0.025)}))
    def post(self):
        """
               sabr normal
               :return: the interpolated value
               """
        content = request.get_json()
        f = content["Forward"]
        shift = content["shift"]
        t = content["time"]
        v_atm_n = content["VolAtm"]
        beta = content["beta"]
        rho = content["rho"]
        volvol = content["volvol"]
        k = content["k"]
        # define model
        return jsonify({"vol normal": sabrInterpolation(f,shift,t,v_atm_n,beta,rho,volvol,k,"N")})