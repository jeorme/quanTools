from flask_restplus import fields, api
from marshmallow import Schema

from quantools.model.fxVolModel.dictionnary import *
from quantools.model.marketData.marketData import Quote


class expiries(Schema):
    atmConvention = fields.Nested(InterpolationMethod)
    atmQuoteId = fields.String()
    butterflyQuoteIds = fields.List(fields.Nested(Quote))
    deliveryDate = fields.String()
    deltaConvention = fields.Nested(deltaConvention)
    expiryDate = fields.String()
    riskReversalQuoteIds = fields.List(fields.Nested(Quote))


class FxVolatilitiesDef(Schema):
    basis = fields.Nested(Basis)
    butterflyStrategy = fields.Nested(butterflyStrategy)
    calibrationType = fields.Nested(calibrationType)
    currencyPairId = fields.String()
    id = fields.String()
    domesticCurrencyId = fields.String()
    domesticDiscountId = fields.String()
    expiries = fields.Nested(expiries)
    expiryExtrapolationMethod = fields.Nested(InterpolationMethod)
    expiryInterpolationMethod = fields.Nested(InterpolationMethod)
    expiryInterpolationVariable = fields.Nested(SmileInterpolationVariable)
    foreignCurrencyId = fields.String()
    foreignDiscountId = fields.String()
    premiumAdjusted = fields.Boolean()
    smileExtrapolationMethod = fields.Nested(InterpolationMethod)
    smileInterpolationMethod = fields.Nested(InterpolationMethod)
    smileInterpolationVariable = fields.Nested(expiryInterpolationVariable)
    strategyConvention = fields.Nested(StrategyConvention)
    surfaceType = fields.Nested(SurfaceType)
    smileAxis = fields.Nested(SmileInterpolationVariable)
