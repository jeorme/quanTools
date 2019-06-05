from datetime import datetime
import time
import json
from flask_restplus import Api, Resource, fields, reqparse
import ibm_boto3
from ibm_botocore.client import Config


def RepoPricer(notional,rate,paymentDate,startDate,endDate,curve,basis):
    yf = yearFrac(startDate,endDate,basis)
    df = getDf(curve,paymentDate)
    return yf*notional*rate*df

def RepoPricerJson(fileName):
    notional = 0
    rate = 0
    startDate = ""
    endDate = ""
    paymentDate = ""
    discountCurve=""
    basis = ""
    with open(fileName,'r') as file:
        data = json.load(file)
        notional = data["notional"]
        rate = data["fixedRate"]
        startDate = data["startDate"]
        endDate = data["endDate"]
        paymentDate = data["paymentDate"]
        curve = data["discountCurve"]
        basis = data["basis"]

    return RepoPricer(notional,rate,paymentDate,startDate,endDate,curve,basis)

def yearFrac(startDate,endDate,basis):
    nbDays = time.mktime(datetime.strptime(endDate, "%Y-%m-%d").timetuple()) -time.mktime(datetime.strptime(startDate, "%Y-%m-%d").timetuple())
    if basis=="ACT365":
        return nbDays/365
    elif basis == "ACT360":
        return nbDays / 360
    elif basis == "ACT364":
        return nbDays/364
    return nbDays/365

def getDf(curve,paymentDate):
    return 0.9

def RepoPricerData(tradeId):
    resource = ibm_boto3.resource('s3',
                                  ibm_api_key_id="emEo1VS5H2EOk51A80O_fy2VlwDjaAt0WUSEJueCPtKx",
                                  ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/72e640662b324e26b6e6c571a681ddf2:bc719890-69ba-4422-a180-4329f613e720::",
                                  ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                                  config=Config(signature_version='oauth'),
                                  endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud/")
    file = resource.Object("tradedataset",tradeId+".json").get()
    data = json.loads(file["Body"].read().decode("utf-8"))
    return RepoPricer(data["notional"], data["fixedRate"], data["paymentDate"], data["startDate"], data["endDate"], data["discountCurve"], data["basis"])
