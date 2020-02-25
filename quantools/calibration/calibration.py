import json
from fxVolGood import constructFXVolSurface
##parse the input
if __name__ == "__main__":
    with open("CalibrationServiceInput.json","r") as file:
        data = json.load(file)
    surface = constructFXVolSurface(data)
    print(surface)