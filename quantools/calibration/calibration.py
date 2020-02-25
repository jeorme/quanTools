import json
from quantools.library.fxvolCalibration.fxVolGood import constructFXVolSurface
import unittest

class calibOneExpiryOneVol(unittest.TestCase):

    """Test case utilisé pour tester la calibration d'une expiry et d'un surface"""

    def test_choice(self):
        """Test le fonctionnement de la fonction 'random.choice'."""
        with open("calibration_fqp.json", "r") as file:
            data = json.load(file)
        surface = constructFXVolSurface(data)
        with open("calibration_fqp.json", "r") as file:
            output = json.load("output_calibration_fqp.json")
        # Vérifie que 'elt' est dans 'liste'
        self.assertEqual(surface, output)

if __name__ == "__main__":
    unittest.main()
