import json

from heston.hestonGood import calibrateHestonModel

with open("hestonInput.json","r") as file:
    data = json.load(file)
val = calibrateHestonModel(data)

