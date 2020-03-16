from datetime import datetime
import multiprocessing
from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields

from quantools.analyticsTools.analyticsTools import yearFraction, getBasis
from quantools.pricing.mathematicTools import bivariateCND

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



@api.route('/normalCdf')
class normalCDF(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input normal CDF",{"u" : fields.Float}))
    def post(self):
        """
        normal cdf
        :return: the normal cumulative distribution function
        """
        content = request.get_json()
        u = content["u"]
        cdf = normalCDF(u)
        # define model
        return jsonify({"normal cumulative":cdf})

@api.route('/biNormalCdf')
class biNormalCDF(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input bi normal CDF",{"x" : fields.Float,"y" : fields.Float,"rho" : fields.Float,}))
    def post(self):
        """
        normal cdf
        :return: the normal cumulative distribution function
        """
        content = request.get_json()
        x = content["x"]
        y = content["y"]
        rho = content["rho"]
        cdf = bivariateCND(x,y,rho)
        # define model
        return jsonify({"bi normal cumulative":cdf})

@api.route('/cpu')
class Cpu(Resource):
    @api.response(200,"SUCCESS")
    def post(self):
        return jsonify(multiprocessing.cpu_count())