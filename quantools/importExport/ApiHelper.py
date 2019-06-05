import requests
import json
import urllib3

from quantools.importExport.ConfigHelper import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#helper
def get(url,marketFile=None):
    """REST CALL : GET"""
    reponse = requests.get(url, verify=False)
    if (reponse.ok):
        val = reponse.json()
    else:
        status = reponse.raise_for_status()
        val = "error : " + status
    reponse.close()
    if marketFile is None:
        return val
    with open(marketFile, "w") as outfile:
        json.dump(val, outfile)
    return "printed in the file : "+marketFile


def delete(url ):
    """REST CALL : DELETE"""
    reponse = requests.delete(url,verify=False)
    if (reponse.ok):
        val = "data deleted"
    else:
        status = reponse.raise_for_status()
        val = "error : " + status
    reponse.close()
    return val

def put(url, json):
    """REST CALL : PUT"""
    reponse = requests.put(url, json=json, verify=False)
    if (reponse.ok):
        val = "build"
    else:
        status = reponse.raise_for_status()
        val = "error : " + status
    reponse.close()
    return val

def post(url, json):
    """REST CALL : POST"""
    reponse = requests.post(url, json=json, verify=False,headers={'Connection':'close'})
    if(reponse.ok):
        if(reponse.status_code==201):
            val = reponse.headers._store['location'][1]
        else:
            val= reponse.json()
    elif(reponse.status_code==400):
        val= reponse.text
    else:
        status = reponse.raise_for_status()
        val =  "error : " + status
    reponse.close()
    return val

def getPerId(url,file):
    rep = file.replace(".json",'/')
    label = "id"
    dict = {}
    if rep == "marketSet/" or rep == "fxvolquotes/" or rep == "yieldcurvequotes/" or rep=="fxrates/":
        label = "name"
    with open(file,'r') as inputfile:
        jsonfile = json.load(inputfile)
        inputfile.close()
    for item in jsonfile:
        val = rep+item[label].replace('/','_')+".json"
        val = val.replace("$id_","")
        if(rep == "fxrates/"):
            reponse = requests.get(url+"/"+item["id"], verify=False)
            if (reponse.ok):
                jsonNode = reponse.json()
            else:
                status = reponse.raise_for_status()
                jsonNode = "error : " + status
            reponse.close()
            if item[label] in dict.keys():
                dict[item[label]].append(jsonNode)
            else:
                dict[item[label]] = [jsonNode]
        else:
            print(get(url+"/"+item["id"],val))

    for key, values in dict.items():
        with open(rep+key.replace('/','_')+".json", "w") as outfile:
            json.dump(values, outfile)
            outfile.close()
    return "end of saving : "+rep

# use the API unitary price to price a FXO with the corresponding measures
# we use the input defined by FCP and use the FCP pricer
# since the API is not defined we use the generic pricer and we set by default the non used parameter
#global varaible
url_fcp_swagger = "https://fr1pslcmf05:8770/api/"
url_pricing_config = "https://fr1pslcmf05:8770/api/pricing/configs"
url_result_handler ="https://fr1pslcmf05:8770/api/pricing/report/result/Pricing"
configName="DEFAULT"
pricingMethod="THEORETICAL"
marketDataSetId="$id/DEFAULT"
marketDataProviderId="PE_STORE_MDP"
resultHandlerConfigId=None
resultHandlerId="Collector"
## serivice
def unitary(aod,referenceCurrency,scenarioContexts,perimeter,configName =configName, pricingMethod = pricingMethod,marketDataSetId = marketDataSetId,marketDataProviderId=marketDataProviderId,resultHandlerId = resultHandlerId,resultHandlerConfigId=resultHandlerConfigId):
    unitary_price = {}
    unitary_price["asOfDate"] = aod
    unitary_price["referenceCurrency"] = referenceCurrency
    unitary_price["pricingMethod"] = pricingMethod
    unitary_price["marketDataSetId"] = marketDataSetId
    unitary_price["resultHandlerId"] = resultHandlerId
    unitary_price["resultHandlerConfigId"] = resultHandlerConfigId
    unitary_price["marketDataProviderId"] = marketDataProviderId
    unitary_price["pricingConfigId"] = getPricingId(configName)
    unitary_price["perimeter"] = perimeter
    unitary_price["scenarioContexts"] = scenarioContexts
    url_price = url_fcp_swagger + "pricing/price/"
    reponse = post(url=url_price, json=unitary_price)
    return reponse["pricingResults"]

if __name__=="__main__":
    pass