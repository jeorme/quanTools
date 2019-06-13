from ibm_botocore.client import Config
import ibm_boto3


from flask import Flask, jsonify
from flask_restplus import Resource, fields, reqparse, Namespace
from flask_cors import CORS

# the app
api = Namespace('bucket', 'handle the bucket : add / delete buckets')

# fx-spot end point
@api.route('/')
class Buckets(Resource):
    @api.doc("return all the buckets name")
    @api.response(200,"Success")
    def get(self):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        val = []
        buckets = resource.buckets.all()
        for bucket in buckets:
            val.append( bucket.name)

        return jsonify(val)

@api.route('/<id>')
class Bucket(Resource):
    @api.doc('create a bucket')
    @api.response(200, "Success : bucket created")
    def post(self,id):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        val = resource.create_bucket(Bucket=id)
        return jsonify("bucket "+val.name+" created")

    @api.doc('delete a bucket')
    @api.response(200, "Success : bucket deleted")
    def delete(self,id):
        resource = ibm_boto3.resource('s3',
                                     ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                     ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                     ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                     config=Config(signature_version='oauth'),
                                     endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        val = resource.Bucket(id).delete()
        return jsonify(jsonify(val).status)