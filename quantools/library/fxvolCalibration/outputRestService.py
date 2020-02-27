def outputFxVolCalibrated(result,data):
    """
    output the calibrated fx vol in the proper format
    """
    output = {"fxVolatilitiesValues":[]}
    indexVol = 0
    for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
        output["fxVolatilitiesValues"].append({"id":fxvol["id"],"date" : data["asOfDate"],"values":{}})
        volValues = result[indexVol]
        jump =0
        for expiry in fxvol["expiries"]:
            output["fxVolatilitiesValues"][indexVol]["values"].update({expiry["expiryDate"]: {
                "deltaConvention":expiry["deltaConvention"],"delivery":expiry["deliveryDate"],"atmIndex" : volValues[0+jump][len(result[indexVol][0])-1],
                "deltaCalls": volValues[0][0:5].tolist(), "deltaPuts": volValues[1][0:5].tolist(),
                "strikes": volValues[3][0:5].tolist(),
                "volatilityValues": result[indexVol][4][0:5].tolist()
            }})
            jump = jump + 7
        indexVol = indexVol + 1
    return output