import json

from flask import request, jsonify
from datetime import datetime
from flask_restplus import Namespace,Resource, fields
from quantools.analyticsTools.analyticsTools import yearFraction, getBasis
api = Namespace('analytics', 'Tools')

ressource_fields = api.model("year fraction input",{"startDate": fields.Date,"endDate": fields.Date,"basis" : fields.String})

@api.route('/yearFraction')
class yearFractionTools(Resource):
    @api.doc("compute the year fraction")
    @api.response(200,"Success")
    @api.expect(ressource_fields)
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

    @api.doc("retreive the list of the enum used for the year fraction")
    @api.response(200, "Success")
    def get(self):
        """
        get service to have the enum used for the basis
        :return: lit of basis enum
        """
        voc=getBasis()
        return jsonify(voc)



