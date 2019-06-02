from ibm_botocore.client import Config
import ibm_boto3


from flask import Flask, jsonify
from flask_restplus import Resource, fields, reqparse, Namespace
from flask_cors import CORS

# the app
api = Namespace('instrument', 'list of supported instrument : FX Cash / FXD OTC')

# the input data type here is Integer. You can change this to whatever works for your app.
# On Bluemix, get the port number from the environment variable PORT # When running this app on the local machine, default to 8080
model_input = api.model('Enter the FX spot trade:', {
            "buySell": fields.String,
            "domesticCurrency": fields.String,
            "domesticAmount": fields.Float,
            "foreignCurrency": fields.String,
            "foreignAmount": fields.Float,
            "maturityDate": fields.String
    })

# fx-spot end point
@api.route('/fx-spot')
class fxSpot(Resource):

    @api.response(200,"Success")
    def get(self):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_iapitance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        val = []
        buckets = resource.buckets.all()
        for bucket in buckets:
            bucketName = bucket.name
            objects = resource.Bucket(bucketName).objects.all()
            for object in objects:
                val.append({bucketName : object.key})

        return jsonify(val)

    @api.response(200, "Success",model_input)
    @api.expect(model_input)
    def post(self):
        pass

    #      parser = reqparse.RequestParser()
    #      parser.add_argument('notional', type=float)
    #      parser.add_argument('fixedRate', type=float)
    #      parser.add_argument('basis', type=str)
    #      parser.add_argument('paymentDate', type=str)
    #      parser.add_argument('startDate', type=str)
    #      parser.add_argument('endDate', type=str)
    #      parser.add_argument('discountCurve', type=str)
    #      parser.add_argument('name', type=str)
    #      args = parser.parse_args()
    #      tradeID = str(args["name"])
    #
    #      resource = ibm_boto3.resource('s3',
    #                                    ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
    #                                    ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
    #                                    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    #                                    config=Config(signature_version='oauth'),
    #                                    endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
    #      resource.Object("tradedataset", tradeID+".json").put(
    #          Body=str(args)
    #      )
    #      bucketName = "tradedataset"
    #      return jsonify(tradeID+" created in the bucket "+bucketName)

    @api.param("fileName","name.json")
    def delete(self):
         resource = ibm_boto3.resource('s3',
                                       ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                       ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                       ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                       config=Config(signature_version='oauth'),
                                       endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
         parser = reqparse.RequestParser()
         parser.add_argument('fileName', type=str)
         args = parser.parse_args()
         tradeID = str(args["fileName"])

         resource.Object("tradedataset", tradeID).delete()
         return tradeID + " deleted"