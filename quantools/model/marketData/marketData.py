from flask_restful import fields
from marshmallow import Schema


class QuoteDelta(Schema):
    delta = fields.Float()
    quoteId = fields.String()

class Quote(Schema):
    value = fields.Float()
    quoteId = fields.String()

class fxRatesQuotes(Schema):
    currencyPairId = fields.String()
    quoteValue = fields.Float()
    spotDate = fields.String()

class yieldCurveValues(Schema):
    id = fields.String()
    discountFactors = fields.List(fields.Float())

class fxVolatilityQuotes(Schema):
    id = fields.String()
    quotes = fields.List(fields.Nested(Quote))

