taskContext= {
    "mode": "SYNC"
}

scenarioContext = [
    {
        "id": "scenario",
        "measureGroupIds": [
            "$id/PnLMeasureGroup"
        ],
        "outputCashflows": False,
        "outputPastCashflows": False,
        "payload": [
            {
                "base": {
                    "hestonParameters": {
                        "EUR_USD_VolSurf": {
                            "kappa": 3.283018753779074,
                            "rho": 0.3147129513266975,
                            "sigma": 0.49979513057536284,
                            "theta": 0.014938480129639073,
                            "v0": 0.021608999999999996
                        }
                    },
                    "fxRates": [
                        {
                            "currency1": "EUR",
                            "currency2": "USD",
                            "value": 1.1432
                        }
                    ],
                    "fxVolatilities": {
                        "EUR_USD_VolSurf": {
                            "smileAxis": "strike",
                            "values": {
                                "2016-07-05": {
                                    "atmValue": 0.0907,
                                    "delivery": "2016-07-13",
                                    "deltaConvention": "spot",
                                    "smileValues": [
                                        0.904317621609066,
                                        0.754317621609066,
                                        0.502158810804533,
                                        0.25,
                                        0.1
                                    ],
                                    "volatilityValues": [
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727
                                    ]
                                },
                                "2016-07-11": {
                                    "atmValue": 0.0905,
                                    "delivery": "2016-07-13",
                                    "deltaConvention": "spot",
                                    "smileValues": [
                                        0.904317621609066,
                                        0.754317621609066,
                                        0.502158810804533,
                                        0.25,
                                        0.1
                                    ],
                                    "volatilityValues": [
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727
                                    ]
                                },
                                "2016-08-04": {
                                    "atmValue": 0.0908,
                                    "delivery": "2016-08-06",
                                    "deltaConvention": "spot",
                                    "smileValues": [
                                        0.904317621609066,
                                        0.754317621609066,
                                        0.502158810804533,
                                        0.25,
                                        0.1
                                    ],
                                    "volatilityValues": [
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727
                                    ]
                                },
                                "2016-10-04": {
                                    "atmValue": 0.0909,
                                    "delivery": "2016-10-15",
                                    "deltaConvention": "spot",
                                    "smileValues": [
                                        0.904317621609066,
                                        0.754317621609066,
                                        0.502158810804533,
                                        0.25,
                                        0.1
                                    ],
                                    "volatilityValues": [
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727
                                    ]
                                },
                                "2019-07-04": {
                                    "atmValue": 0.091,
                                    "delivery": "2019-07-06",
                                    "deltaConvention": "spot",
                                    "smileValues": [
                                        0.904317621609066,
                                        0.754317621609066,
                                        0.502158810804533,
                                        0.25,
                                        0.1
                                    ],
                                    "volatilityValues": [
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727,
                                        0.09727
                                    ]
                                }
                            }
                        }
                    },
                    "yieldCurves": {
                        "EUROIS": {
                            "values": {
                                "2016-07-06": -0.4008000001,
                                "2016-07-11": -0.3462,
                                "2016-08-05": -0.3445,
                                "2016-09-05": -0.3539,
                                "2016-10-05": -0.3683,
                                "2017-01-05": -0.4059,
                                "2017-04-05": -0.4305,
                                "2017-07-05": -0.4509,
                                "2018-07-05": -0.5017,
                                "2019-07-05": -0.5197,
                                "2020-07-06": -0.5162,
                                "2021-07-05": -0.48,
                                "2022-07-05": -0.4117,
                                "2023-07-05": -0.32,
                                "2024-07-05": -0.2176,
                                "2025-07-07": -0.113,
                                "2026-07-06": -0.0105,
                                "2028-07-05": 0.1666,
                                "2031-07-07": 0.362,
                                "2036-07-07": 0.5223,
                                "2041-07-05": 0.5696,
                                "2046-07-05": 0.5823
                            },
                            "valuesType": "zeroCouponRate"
                        },
                        "USDOIS": {
                            "values": {
                                "2016-07-06": 0.4177,
                                "2016-07-12": 0.3999,
                                "2016-08-05": 0.386,
                                "2016-09-05": 0.3868,
                                "2016-10-05": 0.3845,
                                "2017-01-05": 0.3851,
                                "2017-04-05": 0.3907,
                                "2017-07-05": 0.3945,
                                "2018-07-05": 0.419,
                                "2019-07-05": 0.4738,
                                "2020-07-06": 0.5373,
                                "2021-07-05": 0.6059,
                                "2022-07-05": 0.6786,
                                "2023-07-05": 0.7521,
                                "2024-07-05": 0.8248,
                                "2025-07-07": 0.8941,
                                "2026-07-06": 0.9601,
                                "2028-07-05": 1.0774,
                                "2031-07-07": 1.2022,
                                "2036-07-07": 1.3322,
                                "2041-07-05": 1.3961,
                                "2046-07-05": 1.4349
                            },
                            "valuesType": "zeroCouponRate"
                        }
                    }
                },
                "simulations": []
            }
        ],
        "resultsByLeg": True
    }
]

perimeter = {
    "trade": {
        "ids": [
            "Kplus1/FxOptionsDeals/1106"
        ]
    }
}
reponse = {
    "sessionId": "878",
    "entityCount": 1,
    "elapsedTimeMillis": 145,
    "errors": [],
    "pricingResults": {
        "2016-07-05": [
            {
                "entity": {
                    "id": "Kplus1/FxOptionsDeals/1106",
                    "versionId": "1"
                },
                "currencyId": "Kplus1/Currencies/247",
                "pricerId": {
                    "library": "FQPFXDerivative",
                    "pricingModel": "Black Scholes",
                    "numericalMethod": "Closed Formula"
                },
                "scenarios": [
                    {
                        "id": "scenario",
                        "entries": [
                            {
                                "id": "0",
                                "measures": {
                                    "FXD_Delta_Spot_Premium": -277036309.73167014,
                                    "FXD_Gamma": 817.8875901035444,
                                    "FXD_Vanna": 876.0687737421881,
                                    "FXD_Theta": 219155496.46936044,
                                    "FXD_Delta_Spot": -252937295.08776078,
                                    "FXD_Volga": 935.6826729016467,
                                    "FXD_Delta_Forward_Premium": -273197605.55621636,
                                    "FXD_Rho_Discount": -1300971.9172099773,
                                    "NPV": 27540004.978207212,
                                    "FXD_Vega": 2.888114888161042,
                                    "FXD_Delta_Forward": -249432514.60710174,
                                    "FXD_Rho_Foreign": 12048246.489347005,
                                    "FXD_Rho_Domestic": -13349218.406556979
                                },
                                "properties": {},
                                "cashFlows": [],
                                "legs": [
                                    {
                                        "id": "Premium",
                                        "currencyId": "Kplus1/Currencies/247",
                                        "measures": {
                                            "NPV": -9988.562709955124
                                        },
                                        "properties": {},
                                        "cashFlows": []
                                    },
                                    {
                                        "id": "Option",
                                        "currencyId": "Kplus1/Currencies/247",
                                        "measures": {
                                            "FXD_Delta_Spot_Premium": -277036309.73167014,
                                            "FXD_Gamma": 817.8875901035444,
                                            "FXD_Vanna": 876.0687737421881,
                                            "FXD_Theta": 219155496.46936044,
                                            "FXD_Delta_Spot": -252937295.08776078,
                                            "FXD_Volga": 935.6826729016467,
                                            "FXD_Delta_Forward_Premium": -273197605.55621636,
                                            "FXD_Rho_Discount": -1300971.9172099773,
                                            "NPV": 27549993.540917166,
                                            "FXD_Vega": 2.888114888161042,
                                            "FXD_Delta_Forward": -249432514.60710174,
                                            "FXD_Rho_Foreign": 12048246.489347005,
                                            "FXD_Rho_Domestic": -13349218.406556979
                                        },
                                        "properties": {},
                                        "cashFlows": []
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "attributes": {}
            }
        ]
    },
    "taskId": "null"
}
