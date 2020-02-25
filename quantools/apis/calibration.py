from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields

from fxVolGood import constructFXVolSurface
from quantools.model.calibmodel.calibrationModel import calibrationSchema, MarketDataSchema, \
    MarketDataDefinitionsSchema, mdValues, mdDef
from quantools.model.marketData import marketData

api = Namespace('calibration', 'FX vol')


@api.route('/fxvol')
class FxoVol(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("example",{"asOfDate":fields.String,
    "marketDataDefinitions":fields.Raw(example=mdDef,type="json"),
          "marketData"   :   fields.Raw(example=mdValues,type="json")                      }))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """
        content = request.get_json()
        surface = constructFXVolSurface(content)
        # define model
        output =  {}
        index = 0
        for fxvol in content["marketDataDefinitions"]["fxVolatilities"]:
            output.update({fxvol["id"]:surface[index].tolist()})
            index=index+1
        return output

@api.route('/heston')
class Heston(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input of heston calibration",{"TBD" : fields.Float}))
    def post(self):
        """
        interpolation : expiry axis
        :return: the interpolated value
        """
        content = request.get_json()
        TBD = content["TBD"]
        # define model
        return jsonify({"TBD":TBD})