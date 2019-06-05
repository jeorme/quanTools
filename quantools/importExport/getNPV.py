from quantools.importExport import  unitary
import json

if __name__=="__main__":
    outputSpot = "C:\\Users\\jerom\\PycharmProjects\\JVP\\JVP\\importExport\\expectedResult\\FXSPOT\\fxSpot_npv.json"
    outputFXO = "C:\\Users\\jerom\\PycharmProjects\\JVP\\JVP\\importExport\\expectedResult\\FXO\\fxo_npv.json"
    outputFXFwd = "C:\\Users\\jerom\\PycharmProjects\\JVP\\JVP\\importExport\\expectedResult\\FXFWD\\fxFwd_npv.json"
    outputFXSwap = "C:\\Users\\jerom\\PycharmProjects\\JVP\\JVP\\importExport\\expectedResult\\FXSWAP\\fxSwap_npv.json"
    scenarioContexts =[

    {
      "id": "base",
      "measureGroupIds": [
        "NPV"
      ]
    }

]
    perimeterFXO = {"trade" : {"perimeterId": "ALL_FX_OPTION"}}
    perimeterFXSpot = {"trade" : {"perimeterId": "ALL_FX_SPOT"}}
    perimeterFXFWD = {"trade" : {"perimeterId": "ALL_FORWARD"}}
    perimeterFXSWAP = {"trade" : {"perimeterId": "ALL_FX_SWAP"}}
    resultFXO = unitary(aod="2016-07-04",referenceCurrency="$id/USD",perimeter=perimeterFXO, scenarioContexts = scenarioContexts)
    with open(outputFXO,'w') as file:
        json.dump(resultFXO,file)

    resultFXSpot = unitary(aod="2016-07-04",referenceCurrency="$id/USD",perimeter=perimeterFXSpot, scenarioContexts = scenarioContexts)
    with open(outputSpot,'w') as file:
        json.dump(resultFXSpot,file)

    resultFXFwd = unitary(aod="2016-07-04",referenceCurrency="$id/USD",perimeter=perimeterFXFWD, scenarioContexts = scenarioContexts)
    with open(outputFXFwd,'w') as file:
        json.dump(resultFXFwd,file)

    resultFXSwap = unitary(aod="2016-07-04", referenceCurrency="$id/USD", perimeter=perimeterFXSWAP,
                          scenarioContexts=scenarioContexts)
    with open(outputFXSwap, 'w') as file:
        json.dump(resultFXSwap, file)




