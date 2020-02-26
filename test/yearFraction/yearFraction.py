from datetime import datetime
import unittest
import numpy as np

from quantools.analyticsTools.analyticsTools import yearFraction


class testYF(unittest.TestCase):
    """Test case utilisé pour tester la calibration d'une expiry et d'un surface"""
    def test_act360(self):
        """ACT/360"""
        yf = yearFraction(datetime.strptime("2012-02-25","%Y-%m-%d"),datetime.strptime("2013-01-13","%Y-%m-%d"),"ACT/360")
        np.testing.assert_equal(yf, 0.8972222222222223,err_msg="WARNING : regression ACT/360")
    def test_act365(self):
        """ACT/365"""
        yf = yearFraction(datetime.strptime("2012-02-25","%Y-%m-%d"),datetime.strptime("2013-01-13","%Y-%m-%d"),"ACT/365")
        np.testing.assert_equal(yf, 0.8849315068493151,err_msg="WARNING : regression ACT/365")

    def test_act365_equal(self):
        """ACT/365"""
        yf = yearFraction(datetime.strptime("2012-02-25", "%Y-%m-%d"), datetime.strptime("2012-02-25", "%Y-%m-%d"),
                          "ACT/365")
        np.testing.assert_equal(yf, 0.0, err_msg="WARNING : regression ACT/365 EQUAL")

    def test_act365_25(self):
        """ACT/365.25"""
        yf = yearFraction(datetime.strptime("2012-02-25", "%Y-%m-%d"), datetime.strptime("2013-01-13", "%Y-%m-%d"),
                          "ACT/365.25")
        np.testing.assert_equal(yf, 0.8843258042436687, err_msg="WARNING : regression ACT/365.25")

    def test_act366(self):
        """ACT/366"""
        yf = yearFraction(datetime.strptime("2012-02-25", "%Y-%m-%d"), datetime.strptime("2013-01-13", "%Y-%m-%d"),
                          "ACT/366")
        np.testing.assert_equal(yf, 0.8825136612021858, err_msg="WARNING : regression ACT/366")

    def test_30365(self):
        """ACT/366"""
        yf = yearFraction(datetime.strptime("2014-03-31", "%Y-%m-%d"), datetime.strptime("2015-01-13", "%Y-%m-%d"),
                          "30/365")
        np.testing.assert_equal(yf, 0.7753424657534247, err_msg="WARNING : regression 30/365")

    def test_30360(self):
        """ACT/366"""
        yf = yearFraction(datetime.strptime("2012-02-25", "%Y-%m-%d"), datetime.strptime("2013-01-01", "%Y-%m-%d"),
                          "30/360")
        np.testing.assert_equal(yf, 0.85, err_msg="WARNING : regression 30/360")

    def test_30E360(self):
        """ACT/366"""
        yf = yearFraction(datetime.strptime("2014-02-25", "%Y-%m-%d"), datetime.strptime("2015-01-13", "%Y-%m-%d"),
                          "30E/360")
        np.testing.assert_equal(yf, 0.8833333333333333, err_msg="WARNING : regression 30/360")
if __name__ == "__main__":
    unittest.main()
