import functools
from dateutil.parser import parse


import json
import multiprocessing
import timeit

from quantools.library.fxvolCalibration.outputRestService import outputFxVolCalibrated
from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface, calib1FxVol, calib1FxVol1expiry

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

    def calibMC(fileName):
        with open(fileName, "r") as file:
            data = json.load(file)
        start_json = timeit.default_timer()
        calib1FxVolMC = functools.partial(calib1FxVol, parse(data["asOfDate"]), data["marketData"],
                                          data["marketDataDefinitions"]["yieldCurves"])
        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        surface = pool.starmap(calib1FxVolMC, zip(data["marketDataDefinitions"]["fxVolatilities"]))
        pool.close()
        pool.join()
        pool.terminate()
        output = outputFxVolCalibrated(surface, data)
        end_json = timeit.default_timer()
        print("time : " + str(end_json - start_json))
        return output

    start_json = timeit.default_timer()
    calib("severalFxVol.json")
    end_json = timeit.default_timer()
    print("classical : "+str(end_json(start_json)))

    calibMC("severalFxVol.json")





