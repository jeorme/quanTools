import json

from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated
from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface



if __name__ == "__main__":
    import line_profiler
    #@profile
    def calib(fileName):
        """Test le calibration Broker Strangle"""
        with open(fileName, "r") as file:
            data = json.load(file)
        surface = constructFXVolSurface(data)
        output = outputFxVolCalibrated(surface, data)
        return output


    calib("../calibration/calibration_fqp.json")