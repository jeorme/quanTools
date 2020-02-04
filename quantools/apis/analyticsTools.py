import json

from flask import request, jsonify
from datetime import datetime
from flask_restplus import Namespace,Resource, fields
from quantools.analyticsTools.analyticsTools import yearFraction
api = Namespace('analytics', 'Tools')

@api.route('/analytics/yearFraction')
class yearFractionTools(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input",{"startDate": fields.Date,"endDate": fields.Date,"basis" : fields.String
        }))
    def post(self):
        """
        yearFraction service
        :return: the yearFraction between two dates
        """
        content = request.get_json()
        startDate = datetime.strptime(content["startDate"],"%Y-%m-%d")
        endDate = datetime.strptime(content["endDate"],"%Y-%m-%d")
        basis = content["basis"]
        yf = yearFraction(startDate,endDate,basis)
        # define model
        return jsonify({"yearFraction":yf})

    @api.response(200, "Success")
    def get(self):
        """
        get service to have the enum used for the basis
        :return: lit of basis enum
        """
        voc=["ACT/365.FIXED","ACT/365.25","ACT/360","ACT/364"]
        return jsonify(voc)



