def outputFxVolCalibrated(result,data):
    """
    output the calibrated fx vol in the proper format
    """
    output = {}
    for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
        output.update({"id":fxvol["id"],"date" : data["asOfDate"],"values":{}})
        indexExpiry = 0
        for expiry in fxvol["expiries"]:
            output["values"].update({"deltaConvention":expiry["deltaConvention"],"delivery":expiry["deliveryDate"],"atmIndex" : result[indexExpiry][0][len(result[indexExpiry][0])-1]})
            output["values"].update({"deltaCall":result[indexExpiry][0][0:5].tolist(),"deltaPut":result[indexExpiry][1][0:5].tolist(),"delta":result[indexExpiry][2][0:5].tolist(),"strike":result[indexExpiry][3][0:5].tolist(),"volatilityValues":result[indexExpiry][4][0:5].tolist()})
            indexExpiry = indexExpiry + 1
    return output