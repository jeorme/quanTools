import math
from scipy.stats import norm
from marshmallow import Schema, fields, post_load
from enum import Enum

class OptionType(Enum):
    CALL = "CALL"
    PUT = "PUT"
class OptionSchema(Schema):
    domesticRate = fields.Float()
    foreignRate = fields.Float()
    strike = fields.Float()
    optionType = fields.String()
    stockPrice = fields.Float()
    timeToMaturity= fields.Float()
    volatility= fields.Float()
    withGreeks= fields.Boolean()


def blackScholesPricer(stockPrice,strike,domesticRate,volatility,timeToMaturity,foreignRate = 0.0):
    d1 = (math.log(stockPrice/strike) + (domesticRate-foreignRate+volatility*volatility*.5)*timeToMaturity)/(volatility*math.sqrt(timeToMaturity))
    d2 = d1 -volatility*math.sqrt(timeToMaturity)
    return stockPrice * math.exp(-foreignRate*timeToMaturity) * norm.cdf(d1) - strike*math.exp(-domesticRate*timeToMaturity)*norm.cdf(d2)

