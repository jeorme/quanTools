def outputFxVolCalibrated(result,data):
    """
    output the calibrated fx vol in the proper format
    """
    output = {"fxVolatilitiesValues":[]}
    indexVol = 0
    for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
        output["fxVolatilitiesValues"].append({"id":fxvol["id"],"date" : data["asOfDate"],"values":{}})
        smileAxis = fxvol["smileAxis"]
        dictionnary = {"DELTA_CALL" : [0,"deltaCalls"], "DELTA_PUT" : [1,"deltaPuts"], "STRIKE":[3,"strikes"],"DELTA":[2,"deltas"],"LOG_MONEYNESS":[6,"logMoneyness"]}
        volValues = result[indexVol]
        jump =0
        for expiry in fxvol["expiries"]:
            output["fxVolatilitiesValues"][indexVol]["values"].update({expiry["expiryDate"]: {
                "deltaConvention":expiry["deltaConvention"],"delivery":expiry["deliveryDate"],"atmIndex" : volValues[0+jump][len(result[indexVol][0])-1],
            "volatilityValues": result[indexVol][4][0:5].tolist()}})
            for axis in smileAxis:
                output["fxVolatilitiesValues"][indexVol]["values"][expiry["expiryDate"]].update({dictionnary[axis][1]: volValues[dictionnary[axis][0]][0:5].tolist()})
            jump = jump + 7
        indexVol = indexVol + 1
    return output