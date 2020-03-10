from datetime import datetime
import line_profiler
from quantools.analyticsTools.analyticsTools import yearFraction


"""Test le calibration Broker Strangle"""
#with open("calibration_fqp.json", "r") as file:
#    data = json.load(file)
#surface = constructFXVolSurface(data)
#print(surface)

yf = yearFraction(datetime.strptime("2012-02-25","%Y-%m-%d"),datetime.strptime("2013-01-13","%Y-%m-%d"),"ACT/360")
