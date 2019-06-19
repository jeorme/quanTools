from ibm_botocore.client import Config
import ibm_boto3
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense

from flask import request, jsonify
from flask_restplus import Resource, fields, reqparse, Namespace
from flask_cors import CORS
from flask_apispec.annotations import doc

# the app
api = Namespace('MOCK RNN', 'build RNN network for time series estimation')

@api.route('/rnn/mock')
class Buckets(Resource):
    @api.response(200,"Success")
    @api.expect(api.model("data",{"data" : fields.List(fields.Float)}))
    def post(self):
        """
        mock service for RNN
        :return: param of the NN
        """
        content = request.get_json()
        data = np.asarray(content["data"])
        # define model
        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(10, 10)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        model.summary
        return jsonify({"total param":model.count_params()})