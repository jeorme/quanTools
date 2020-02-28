from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from quantools.model.calibmodel.calibrationModel import mdDef, mdValues, outputFXVol

from quantools.model.heston.hestonModel import inputs_heston, input_md, hestonOutput
from quantools.model.pricing.lsvModel import reponse, scenarioContext, perimeter, taskContext

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


@api.route('/pricing/lsv')
class Lsv(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("lsv pricing", {"marketDataProviderId": fields.String(default="PE_STORE_MDP"),
  "marketDataSetId": fields.String(default="$id/DEFAULT"),"pricingConfigId" : fields.String(default="$id/DEFAULT-FXO"),
    "pricingMethod": fields.String(default="PRACTICAL"),
    "resultHandlerId": fields.String(default="Collector"),
                                          "pricingDates": fields.List(fields.String(default = "2016-07-05")),
                                          "scenarioContexts" : fields.Raw(example=scenarioContext,type="json"),
                                          "perimeter" : fields.Raw(example=perimeter,type="json"),
                                          "taskContext" : fields.Raw(example=taskContext,type="json")
    }))
    def post(self):
        """
        pricing lsv :mock
        :return: pricing result
        """

        # define model
        return jsonify(reponse)