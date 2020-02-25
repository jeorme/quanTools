import json
from fxVolGood import constructFXVolSurface
##parse the input

with open("calibration_fqp.json","r") as file:
    data = json.load(file)
surface = constructFXVolSurface(data)
print(surface)