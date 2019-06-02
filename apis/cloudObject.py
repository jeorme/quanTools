import json
import os

from ibm_botocore.client import Config
import ibm_boto3


from flask import Flask, jsonify
from flask_restplus import Resource, fields, reqparse, Namespace
from flask_cors import CORS

# the app
api = Namespace('cloud-object', 'add cloud object into a bucket')

# fx-spot end point
@api.route('/')
class Objects(Resource):
    @api.doc("get the cloud object in a given bucket")
    @api.response(200,"Success")
    @api.param("bucket", "name of the bucket")
    def get(self):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        parser = reqparse.RequestParser()
        parser.add_argument('bucket', type=str)
        args = parser.parse_args()
        id = str(args["bucket"])
        val = []
        objects = resource.Bucket(id).objects.all()
        for obj in objects:
            val.append({"key": obj.key, "tag": obj.e_tag, "bucket": obj.bucket_name})

        return jsonify(val)


@api.route('/<id>')
@api.response(404, 'Cat not found')
class Object(Resource):
    @api.doc('get object by id and bucket')
    @api.param("bucket", "name of the bucket")
    def get(self,id):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        parser = reqparse.RequestParser()
        parser.add_argument('bucket', type=str)
        args = parser.parse_args()
        bucket = str(args["bucket"])
        val = []
        resource.Object(bucket,id).download_file("/tmp/"+id)
        data={}
        with open("/tmp/"+id,"r") as file:
            data = json.load(file)
            file.close()
        os.remove("/tmp/"+id)
        return jsonify(data)

    @api.doc('get object by id and bucket')
    @api.param("bucket", "name of the bucket")
    def delete(self, id):
        resource = ibm_boto3.resource('s3',
                                      ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                      ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                      ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                      config=Config(signature_version='oauth'),
                                      endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
        parser = reqparse.RequestParser()
        parser.add_argument('bucket', type=str)
        args = parser.parse_args()
        resource.Object(str(args["bucket"]), id).delete()

        return jsonify(id+" deleted")