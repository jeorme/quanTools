from quantools import importExport as ApiHelper

urlPricingConfig = "https://fr1pslcmf05:8770/api/pricing/configs/"
urlRiskResolver = "https://fr1pslcmf05:8770/api/pricing/risk-factor-resolver-configs/"
urlFinDefSchemes = "https://fr1pslcmf05:8770/api/pricing/finite-difference-schemes-configs/"

def getPricingId(configName):
    urlConfig = "https://fr1pslcmf05:8770/api/pricing/configs"
    config = ApiHelper.get(urlConfig)
    for item in config:
        if (item['name']==configName):
            return item["id"]
    return "error"

def getPricingConfig(configName):
    url = urlPricingConfig+getPricingId(configName)
    pricingConfig = ApiHelper.get(url)
    return pricingConfig, ApiHelper.get(urlRiskResolver + pricingConfig['riskFactorResolverConfigId']), ApiHelper.get(urlFinDefSchemes + pricingConfig['finiteDifferenceSchemesConfigId']),

if __name__=="__main__":
    getPricingId("DEFAULT")
    pricingConfig,rr,finiteDef = getPricingConfig("DEFAULT")
    print(pricingConfig)
    print(rr)
    print(finiteDef)
