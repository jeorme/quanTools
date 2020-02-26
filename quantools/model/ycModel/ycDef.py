from flask_restful import fields
from flask_restplus import api
from marshmallow import Schema

from quantools.model.fxVolModel.dictionnary import Basis, InterpolationMethod
from quantools.model.ycModel.dictionnary import *


class interpolYC:
    method = fields.Nested(InterpolationMethod)
    variable = fields.Nested(ycVariable)


class ycDef(Schema):
    currencyId = fields.String()
    extrapolationAfterLastPoint = fields.Nested(interpolYC)
    extrapolationBeforeFirstPoint = fields.Nested(interpolYC)
    interpolation = fields.Nested(interpolYC)
    id = fields.String()
    zeroCouponBasis = fields.Nested(Basis)
    zeroCouponFormula = fields.Nested(zeroCouponFormula)
    maturities = fields.List(fields.String())


yieldCurveDef = {
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
        }
    ]
}
yieldCurveValues = {
    "yieldCurveValues": [
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
        }
    ]
}

