import json
from quantools.library.fxvolCalibration.fxVolGood import constructFXVolSurface
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

if __name__ == "__main__":
    unittest.main()
