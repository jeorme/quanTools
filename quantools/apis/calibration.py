from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields

from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface
from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated
from quantools.model.calibmodel.calibrationModel import mdValues, mdDef
from quantools.model.heston.hestonModel import inputs_heston, input_md, hestonOutput

api = Namespace('calibration', 'FX vol')


@api.route('/fxvol')
class FxoVol(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("fx vol calibration",{"asOfDate":fields.String(default="2011-02-02"),
    "marketDataDefinitions":fields.Raw(example=mdDef,type="json"),
          "marketData"   :   fields.Raw(example=mdValues,type="json")
                                     }))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """
        content = request.get_json()
        surface = constructFXVolSurface(content)
        # define model
        output =  outputFxVolCalibrated(surface, content)
        return output

@api.route('/heston')
class Heston(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("heston calibration", {"calibrationDate": fields.String(default="2016-07-05"),
                                      "marketDataSet": fields.String(default="DEFAULT"),
                                      "marketDataProvider" : fields.String("PE_STORE_MDP"),
                                      "inputs" : fields.Raw(example=inputs_heston, type="json"),
                                      "marketData": fields.Raw(example=input_md, type="json")
                                      }))
    def post(self):
        """
        Heston calibration mock
        :return: the expoected output of the calibration heston
        """

        # define model
        return jsonify({"calibrationResults":hestonOutput})