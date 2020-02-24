import json
from fxVolGood import constructFXVolSurface
##parse the input

with open("CalibrationServiceInput.json","r") as file:
    data = json.load(file)
surface = constructFXVolSurface(data)
print(surface)