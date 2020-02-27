from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from quantools.model.calibmodel.calibrationModel import mdDef, mdValues, outputFXVol

from quantools.model.heston.hestonModel import inputs_heston, input_md, hestonOutput

api = Namespace('mock', 'input / output of the various service')

@api.route('/calibration/heston')
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
        :return: heston parameters
        """

        # define model
        return jsonify({"calibrationResults":hestonOutput})


@api.route('/calibration/fxvol')
class fxVol(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("fx vol calibration", {"asOfDate": fields.String(default="2011-02-02"),
                                                 "marketDataDefinitions": fields.Raw(example=mdDef, type="json"),
                                                 "marketData": fields.Raw(example=mdValues, type="json")
                                                 }))
    def post(self):
        """
        FX vol calibration mock
        :return: calibrated fx vol
        """

        # define model
        return jsonify(outputFXVol)