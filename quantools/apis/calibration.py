from flask import request
from flask_restplus import Namespace,Resource, fields

from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface
from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated
from quantools.model.calibmodel.calibrationModel import mdValues, mdDef
from quantools.model.heston.hestonModel import inputs_heston, input_md

api = Namespace('calibration', 'calibration service : heston, fx vol')


@api.route('/fxvol')
class FxVol(Resource):
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