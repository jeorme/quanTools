import functools
import json
import multiprocessing

from dateutil.parser import parse

from quantools.library.fxvolCalibration.fxVol import constructFXVolSurface, calib1FxVol
import unittest
import numpy as np
class calibOneExpiryOneVol(unittest.TestCase):

    """Test case utilisé pour tester la calibration d'une expiry et d'un surface"""

    def test_choice(self):
        """Test le calibration Broker Strangle"""
        with open("calibration_fqp.json", "r") as file:
            data = json.load(file)
        surface = constructFXVolSurface(data)
        for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
            print("test")
        with open("output_calibration_fqp.json", "r") as file:
            output = json.load(file)
        # Vérifie que 'elt' est dans 'liste'
        np.testing.assert_allclose(surface, output,err_msg="WARNING : regression",atol =1e-6)

    def test_choiceMC(self):
        """Test le calibration Broker Strangle"""
        with open("calibration_fqp.json", "r") as file:
            data = json.load(file)
        calib1FxVolMC = functools.partial(calib1FxVol, parse(data["asOfDate"]), data["marketData"],
                                          data["marketDataDefinitions"]["yieldCurves"])
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        surface = pool.starmap(calib1FxVolMC, zip(data["marketDataDefinitions"]["fxVolatilities"]))
        pool.close()
        pool.join()
        pool.terminate()
        # output result
        for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
            print("test")
        with open("output_calibration_fqp.json", "r") as file:
            output = json.load(file)
        # Vérifie que 'elt' est dans 'liste'
        np.testing.assert_allclose(surface, output, err_msg="WARNING : regression", atol=1e-6)

if __name__ == "__main__":
    unittest.main()
