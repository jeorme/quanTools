from enum import Enum


class zeroCouponFormula(Enum):
    EXPONENTIAL = "EXPONENTIAL"
    SIMPLE = "SIMPLE"
    COMPOUND = "COMPOUND"

class ycVariable(Enum):
    DISCOUNT_FACTOR = "DISCOUNT_FACTOR"
    ZERO_COUPON_RATE = "ZERO_COUPON_RATE"
