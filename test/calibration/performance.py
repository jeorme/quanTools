import json

from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface
from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated

def calibService(fileName = "calibration_fqp.json"):
    with open(fileName, "r") as file:
        data = json.load(file)
    surface = constructFXVolSurface(data)
    return  outputFxVolCalibrated(surface, data)
if __name__ == "__main__":
    calibService()