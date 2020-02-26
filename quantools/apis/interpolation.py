from flask import request, jsonify
from flask_restplus import Namespace,Resource, fields
api = Namespace('interpolation', 'FX vol')

@api.route('/smile')
class Interpolation(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input of smile interpolation",{"TBD": fields.String
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

@api.route('/expiry')
class Expiry(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("input of expiry interpolation",{"TBD" : fields.Float}))
    def post(self):
        """
        interpolation : expiry axis
        :return: the interpolated value
        """
        content = request.get_json()
        TBD = content["TBD"]
        # define model
        return jsonify({"TBD":TBD})