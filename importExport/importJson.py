import json
from importExport import ApiHelper
with open("linkExtraction.json",'r') as outputfile:
    link = json.load(outputfile)
    outputfile.close()
    for item in link:
        print(ApiHelper.get(item["url"],item["output"]))
        print(ApiHelper.getPerId(item["url"],item["output"]))
