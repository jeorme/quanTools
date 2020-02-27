import json

from hestonHelper import calibrateHestonModel

with open("hestonInput.json","r") as file:
    data = json.load(file)

for input in data["inputs"]:
    id = input["volatilityName"]
    calibrateHestonModel(data["marketData"]["fxVolatilities"][id],data["marketData"]["yieldCurves"],data["marketData"]["fxRates"],data["calibrationDate"],input["parameters"])

