from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields, reqparse, inputs
import requests

from requests.auth import HTTPBasicAuth

api = Namespace('openData', 'wrapper of end point without autorization')
parserSearch = reqparse.RequestParser()
parserSearch.add_argument('address', type=inputs.regex(""),
                          help="address of the appartment",
                          default="42, West Mead", required=True)
parserSearch.add_argument('postcode', type=inputs.regex(""),
                          help="postcode of the appartment",
                          default="HA4 0TL", required=True)

parserLmkey = reqparse.RequestParser()
parserLmkey.add_argument('lmkey', type=inputs.natural,
                          help="lmkey of the appartment",
                          default="1827209002922020092007053442338480", required=True)

@api.route('/api/v1/domestic/search')
class search(Resource):
    @api.response(200,"Success")
    @api.expect(parserSearch)
    def get(self):
        """
        :return: the search of an appartment based on address and postcode
        """

        url = "https://epc.opendatacommunities.org/api/v1/domestic/search"
        user = "jerome.petit@outlook.com"
        password = "05f4c5ddf8648d226cc2d8486d60fd536d2ac79d"
        args = parserSearch.parse_args()
        address = args["address"]
        postcode = args["postcode"]
        response = requests.get(url, auth=HTTPBasicAuth(user, password),params = {"address" : address,"postcode" : postcode},headers={"Accept":"application/json"})
        return response.json()

@api.route('/api/v1/domestic/certificate/{lmkey}')
class certificate(Resource):
    @api.response(200,"Success")
    @api.expect(parserLmkey)
    def get(self):
        """
        :return: the search of an appartment based on address and postcode
        """

        url = "https://epc.opendatacommunities.org/api/v1/domestic/certificate/{}"
        user = "jerome.petit@outlook.com"
        password = "05f4c5ddf8648d226cc2d8486d60fd536d2ac79d"
        args = parserLmkey.parse_args()
        lmkey = args["lmkey"]
        response = requests.get(url.format(lmkey), auth=HTTPBasicAuth(user, password),headers={"Accept":"application/json"})
        return response.json()

@api.route('/api/v1/domestic/recommendations/{lmkey}')
class recommendations(Resource):
    @api.response(200,"Success")
    @api.expect(parserLmkey)
    def get(self):
        """
        :return: the search of an appartment based on address and postcode
        """

        url = "https://epc.opendatacommunities.org/api/v1/domestic/recommendations/{}"
        user = "jerome.petit@outlook.com"
        password = "05f4c5ddf8648d226cc2d8486d60fd536d2ac79d"
        args = parserLmkey.parse_args()
        lmkey = args["lmkey"]
        response = requests.get(url.format(lmkey), auth=HTTPBasicAuth(user, password),headers={"Accept":"application/json"})
        return response.json()