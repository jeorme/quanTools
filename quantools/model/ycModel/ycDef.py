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



