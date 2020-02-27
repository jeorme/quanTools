from marshmallow import Schema, fields

from quantools.model.fxVolModel.FxVolModel import FxVolatilitiesDef
from quantools.model.marketData.marketData import fxRatesQuotes, yieldCurveValues, fxVolatilityQuotes
from quantools.model.ycModel import ycDef


class MarketDataDefinitionsSchema(Schema):
    fxVolatilities = fields.List(fields.Nested(FxVolatilitiesDef,many=True))
    yieldCurves = fields.List(fields.Nested(ycDef,many=True))


class MarketDataSchema(Schema):
    fxRates = fields.List(fields.Nested(fxRatesQuotes,many=True))
    yieldCurveValues = fields.List(fields.Nested(yieldCurveValues,many=True))
    fxVolatilityQuotes = fields.List(fields.Nested(fxVolatilityQuotes,many=True))


class calibrationSchema(Schema):
    asOfDate = fields.String()
    marketDataDefinitions = fields.Nested(MarketDataDefinitionsSchema,many=True)
    marketData = fields.Nested(MarketDataSchema,many=True)


mdDef = {
      "fxVolatilities": [
      {
        "basis": "ACT/365",
        "smileAxis": [
          "DELTA_CALL",
          "DELTA_PUT"
        ],
        "butterflyStrategy": "STRANGLE",
        "calibrationType": "MID",
        "currencyPairId": "EUR/GBP",
        "id": "EURGBP_Volatility",
        "domesticCurrencyId": "GBP",
        "domesticDiscountId": "gbpDiscount",
        "expiries": [
          {
            "atmConvention": "FORWARD",
            "atmQuoteId": "FX_ATM_CALL_VOL_2M",
            "butterflyQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_BF25_VOL_1M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_BF10_VOL_1M"
              }
            ],
            "deliveryDate": "2011-04-13",
            "deltaConvention": "FORWARD",
            "expiryDate": "2011-04-11",
            "riskReversalQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_RR25_VOL_1M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_RR10_VOL_1M"
              }
            ]
          },
          {
            "atmConvention": "FORWARD",
            "atmQuoteId": "FX_ATM_CALL_VOL_3M",
            "butterflyQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_BF25_VOL_3M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_BF10_VOL_3M"
              }
            ],
            "deliveryDate": "2011-05-13",
            "deltaConvention": "FORWARD",
            "expiryDate": "2011-05-11",
            "riskReversalQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_RR25_VOL_3M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_RR10_VOL_3M"
              }
            ]
          }
        ],
        "expiryExtrapolationMethod": "FLAT",
        "expiryInterpolationMethod": "FLAT",
        "expiryInterpolationVariable": "TIME_WEIGHTED_TOTAL_VARIANCE",
        "foreignCurrencyId": "EUR",
        "foreignDiscountId": "eurDiscount",
        "fxEvents": {},
        "premiumAdjusted": True,
        "smileExtrapolationMethod": "CUBIC_SPLINE",
        "smileInterpolationMethod": "CUBIC_SPLINE",
        "smileInterpolationVariable": "DELTA_CALL",
        "strategyConvention": "BROKER_STRANGLE",
        "surfaceType": "BF_RR"
      },
      {
        "basis": "ACT/365",
        "butterflyStrategy": "STRANGLE",
        "calibrationType": "MID",
        "currencyPairId": "EUR/USD",
        "id": "EURUSD_Volatility",
        "domesticCurrencyId": "USD",
         "smileAxis": [
          "STRIKE",
          "DELTA_PUT"
        ],
        "domesticDiscountId": "usdDiscount",
        "expiries": [
          {
            "atmConvention": "FORWARD",
            "atmQuoteId": "FX_ATM_CALL_VOL_6M",
            "butterflyQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_BF25_VOL_6M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_BF10_VOL_6M"
              }
            ],
            "deliveryDate": "2011-10-13",
            "deltaConvention": "FORWARD",
            "expiryDate": "2011-10-11",
            "riskReversalQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_RR25_VOL_6M"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_RR10_VOL_6M"
              }
            ]
          },
          {
            "atmConvention": "FORWARD",
            "atmQuoteId": "FX_ATM_CALL_VOL_1Y",
            "butterflyQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_BF25_VOL_1Y"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_BF10_VOL_1Y"
              }
            ],
            "deliveryDate": "2012-05-13",
            "deltaConvention": "FORWARD",
            "expiryDate": "2012-05-11",
            "riskReversalQuoteIds": [
              {
                "delta": 0.25,
                "quoteId": "FX_RR25_VOL_1Y"
              },
              {
                "delta": 0.1,
                "quoteId": "FX_RR10_VOL_1Y"
              }
            ]
          }
        ],
        "expiryExtrapolationMethod": "FLAT",
        "expiryInterpolationMethod": "FLAT",
        "expiryInterpolationVariable": "TIME_WEIGHTED_TOTAL_VARIANCE",
        "foreignCurrencyId": "EUR",
        "foreignDiscountId": "eurDiscount",
        "fxEvents": {},
        "premiumAdjusted": True,
        "smileExtrapolationMethod": "CUBIC_SPLINE",
        "smileInterpolationMethod": "CUBIC_SPLINE",
        "smileInterpolationVariable": "DELTA_CALL",
        "strategyConvention": "BROKER_STRANGLE",
        "surfaceType": "BF_RR"
      }
    ],
    "yieldCurves": [
      {
        "currencyId": "EUR",
        "extrapolationAfterLastPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "extrapolationBeforeFirstPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "interpolation": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "maturities": [
          "2011-02-03",
          "2011-02-11",
          "2011-02-18",
          "2011-02-25",
          "2011-03-04",
          "2011-04-04",
          "2011-05-04",
          "2011-06-07",
          "2011-07-06",
          "2011-08-05",
          "2011-10-16",
          "2012-01-18",
          "2013-01-21"
        ],
        "id": "eurDiscount",
        "zeroCouponBasis": "ACT/365",
        "zeroCouponFormula": "EXPONENTIAL"
      },
      {
        "currencyId": "GBP",
        "extrapolationAfterLastPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "extrapolationBeforeFirstPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "interpolation": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "maturities": [
          "2011-02-03",
          "2011-02-11",
          "2011-02-18",
          "2011-02-25",
          "2011-03-04",
          "2011-04-04",
          "2011-05-04",
          "2011-06-07",
          "2011-07-06",
          "2011-08-05",
          "2011-10-16",
          "2012-01-18",
          "2013-01-21"
        ],
        "id": "gbpDiscount",
        "zeroCouponBasis": "ACT/365",
        "zeroCouponFormula": "EXPONENTIAL"
      },
      {
        "currencyId": "USD",
        "extrapolationAfterLastPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "extrapolationBeforeFirstPoint": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "interpolation": {
          "method": "LINEAR",
          "variable": "ZERO_COUPON_RATE"
        },
        "maturities": [
          "2011-02-03",
          "2011-02-11",
          "2011-02-18",
          "2011-02-25",
          "2011-03-04",
          "2011-04-04",
          "2011-05-04",
          "2011-06-07",
          "2011-07-06",
          "2011-08-05",
          "2011-10-16",
          "2012-01-18",
          "2013-01-21"
        ],
        "id": "usdDiscount",
        "zeroCouponBasis": "ACT/365",
        "zeroCouponFormula": "EXPONENTIAL"
      }
    ]
}
mdValues = {
    "yieldCurveValues": [
        {
            "id": "gbpDiscount",
            "discountFactors": [
                0.99993056,
                0.997889771,
                0.997000815,
                0.996196287,
                0.995032935,
                0.994527591,
                0.99347771,
                0.992808052,
                0.99154019,
                0.990635849,
                0.971947201,
                0.96914137,
                0.820255591
            ]
        },
        {
            "id": "eurDiscount",
            "discountFactors": [
                0.9999902779,
                0.9999847224,
                0.9999417527,
                0.9998952873,
                0.9998480099,
                0.9997647742,
                0.9995274386,
                0.9992303035,
                0.9642335076,
                0.9440648339,
                0.9206156551,
                0.8947970522,
                0.8674010426
            ]
        },
        {
            "id": "usdDiscount",
            "discountFactors": [
                0.9999902779,
                0.9999847224,
                0.9999417527,
                0.9998952873,
                0.9998480099,
                0.9997647742,
                0.9995274386,
                0.9992303035,
                0.9642335076,
                0.9440648339,
                0.9206156551,
                0.8947970522,
                0.8674010426
            ]
        }
    ],
    "fxRates": [
        {
            "currencyPairId": "EUR/GBP",
            "quoteValue": 0.8566,
            "spotDate": "2011-02-04"
        },
        {
            "currencyPairId": "EUR/USD",
            "quoteValue": 1.12,
            "spotDate": "2011-02-04"
        }
    ],
    "fxVolatilityQuotes": [
        {
            "id": "EURGBP_Volatility",
            "quotes": [
                {
                    "quoteId": "FX_RR10_VOL_1M",
                    "value": 0.0015
                },
                {
                    "quoteId": "FX_RR25_VOL_1M",
                    "value": 0.001
                },
                {
                    "quoteId": "FX_BF10_VOL_1M",
                    "value": 0.00575
                },
                {
                    "quoteId": "FX_BF25_VOL_1M",
                    "value": 0.002
                },
                {
                    "quoteId": "FX_ATM_CALL_VOL_2M",
                    "value": 0.097
                },
                {
                    "quoteId": "FX_RR10_VOL_3M",
                    "value": 0.002
                },
                {
                    "quoteId": "FX_RR25_VOL_3M",
                    "value": 0.0015
                },
                {
                    "quoteId": "FX_BF10_VOL_3M",
                    "value": 0.00675
                },
                {
                    "quoteId": "FX_BF25_VOL_3M",
                    "value": 0.003
                },
                {
                    "quoteId": "FX_ATM_CALL_VOL_3M",
                    "value": 0.107
                }
            ]
        },
        {
            "id": "EURUSD_Volatility",
            "quotes": [
                {
                    "quoteId": "FX_RR10_VOL_6M",
                    "value": 0.0015
                },
                {
                    "quoteId": "FX_RR25_VOL_6M",
                    "value": 0.001
                },
                {
                    "quoteId": "FX_BF10_VOL_6M",
                    "value": 0.00575
                },
                {
                    "quoteId": "FX_BF25_VOL_6M",
                    "value": 0.002
                },
                {
                    "quoteId": "FX_ATM_CALL_VOL_6M",
                    "value": 0.097
                },
                {
                    "quoteId": "FX_RR10_VOL_1Y",
                    "value": 0.002
                },
                {
                    "quoteId": "FX_RR25_VOL_1Y",
                    "value": 0.0015
                },
                {
                    "quoteId": "FX_BF10_VOL_1Y",
                    "value": 0.00675
                },
                {
                    "quoteId": "FX_BF25_VOL_1Y",
                    "value": 0.003
                },
                {
                    "quoteId": "FX_ATM_CALL_VOL_1Y",
                    "value": 0.107
                }
            ]
        }
    ]
}

outputFXVol ={
  "fxVolatilitiesValues": [
    {
      "id": "EURGBP_Volatility",
      "date": "2011-02-02",
      "values": {
        "2011-04-11": {
          "deltaConvention": "FORWARD",
          "delivery": "2011-04-13",
          "atmIndex": 2,
          "volatilityValues": [
            0.10349005019935864,
            0.09949414275728799,
            0.097,
            0.09849414275728799,
            0.10199005019935864
          ],
          "deltaCalls": [
            0.1,
            0.25,
            0.49164919948130553,
            0.7217910192931705,
            0.8455673043083362
          ],
          "deltaPuts": [
            -0.9594029447437192,
            -0.7794422364602638,
            -0.5083508005186945,
            -0.25,
            -0.1
          ]
        },
        "2011-05-11": {
          "deltaConvention": "FORWARD",
          "delivery": "2011-05-13",
          "atmIndex": 2,
          "volatilityValues": [
            0.10349005019935864,
            0.09949414275728799,
            0.097,
            0.09849414275728799,
            0.10199005019935864
          ],
          "deltaCalls": [
            0.1,
            0.25,
            0.49164919948130553,
            0.7217910192931705,
            0.8455673043083362
          ],
          "deltaPuts": [
            -0.9594029447437192,
            -0.7794422364602638,
            -0.5083508005186945,
            -0.25,
            -0.1
          ]
        }
      }
    },
    {
      "id": "EURUSD_Volatility",
      "date": "2011-02-02",
      "values": {
        "2011-10-11": {
          "deltaConvention": "FORWARD",
          "delivery": "2011-10-13",
          "atmIndex": 2,
          "volatilityValues": [
            0.10348644761221995,
            0.0994897821735788,
            0.097,
            0.0984897821735788,
            0.10198644761221995
          ],
          "strikes": [
            1.2523321784199555,
            1.1842960340084072,
            1.12,
            1.0602198869231518,
            1.0066091451573194
          ],
          "deltaPuts": [
            -1.018153730732103,
            -0.807407173221792,
            -0.516040768147848,
            -0.25,
            -0.1
          ]
        },
        "2012-05-11": {
          "deltaConvention": "FORWARD",
          "delivery": "2012-05-13",
          "atmIndex": 2,
          "volatilityValues": [
            0.10348644761221995,
            0.0994897821735788,
            0.097,
            0.0984897821735788,
            0.10198644761221995
          ],
          "strikes": [
            1.2523321784199555,
            1.1842960340084072,
            1.12,
            1.0602198869231518,
            1.0066091451573194
          ],
          "deltaPuts": [
            -1.018153730732103,
            -0.807407173221792,
            -0.516040768147848,
            -0.25,
            -0.1
          ]
        }
      }
    }
  ]
}