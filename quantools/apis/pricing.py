from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields

from quantools.pricing.Option import OptionSchema, blackScholesPricer

api = Namespace('pricing', 'utilities ')


@api.route('/BlackScholes')
class PricingBS(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("data model blacks scholes pricing",{"domesticRate" : fields.Float,"strike": fields.Float,
                                  "optionType" : fields.String(default= "CALL"),"stockPrice" : fields.Float,"timeToMaturity" : fields.Float,
                                  "volatility" : fields.Float,"foreignRate":fields.Float(required = False)}))
    def post(self):
        """
        pricing of european call/put option with Black Scholes
        :return: NPV (greeks are not supported right)
        """
        content = OptionSchema().load(request.get_json())
        NPV = blackScholesPricer(stockPrice=content["stockPrice"],strike=content["strike"],domesticRate=content["domesticRate"],volatility=content["volatility"],timeToMaturity=content["timeToMaturity"])
        # define model
        return jsonify({"NPV" : NPV})

@api.route('/windowBarrier')
class Pricing(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("data model window barrier",{"ForeignRate" : fields.Float,"DomesticRate" : fields.Float,"fixedAmount": fields.Float,
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
        optionType = content["optionType"]
        Spot = content["Spot"]
        Strike = content["Strike"]
        Time = content["Time"]
        timeToSettle = content["timeToSettle"]
        timeToSettle = content["timeToSettle"]
        # define model
        return jsonify({"NPV":foreignRate})
