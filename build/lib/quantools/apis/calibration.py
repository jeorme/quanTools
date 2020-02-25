import json

from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields
api = Namespace('calibration', 'FX vol')

@api.route('/calibration/fxvol')
class FxoVol(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input",{"TBD": fields.String
        }))
    def post(self):
        """
        interpolation : smile axis
        :return: the interpolated value
        """
        content = request.get_json()
        TBD = content["TBD"]

        # define model
        return jsonify({"TBD":TBD})

@api.route('/calibration/heston')
class Heston(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input",{"TBD" : fields.Float}))
    def post(self):
        """
        interpolation : expiry axis
        :return: the interpolated value
        """
        content = request.get_json()
        TBD = content["TBD"]
        # define model
        return jsonify({"TBD":TBD})