from enum import Enum

class Basis(Enum):
    ACT365 = "ACT/365"
    ACT360 = "ACT360"
    ACT364 = "ACT/364"
    ACT366 = "ACT/366"
    ACT365_25 = "ACT/365.25"

class SurfaceType(Enum):
    BF_RR = "BF_RR"

class StrategyConvention(Enum):
    BROKER_STRANGLE = "BROKER_STRANGLE"
    SMILE_STRANGLE = "SMILE_STRANGLE"

class SmileInterpolationVariable(Enum):
    DELTA_CALL = "DELTA_CALL"
    DELTA_PUT = "DELTA_PUT"
    STRIKE = "STRIKE"
    LOGMONEYNESS = "LOGMONEYNESS"

class InterpolationMethod(Enum):
    CUBIC_SPLINE = "CUBIC_SPLINE"
    LINEAR = "LINEAR"
    FLAT = "FLAT"

class expiryInterpolationVariable(Enum):
    TIME_WEIGHTED_TOTAL_VARIANCE = "TIME_WEIGHTED_TOTAL_VARIANCE"
    TOTAL_VARIANCE = "TOTAL_VARIANCE"
    VOLATILITY = "VOLATILITY"
    VARIANCE = "VARIANCE"

class calibrationType(Enum):
    MID = "MID"
    BID = "BID"
    ASK = "ASK"
    BID_ASK = "BID/ASK"

class butterflyStrategy(Enum):
    STRANGLE = "STRANGLE"

class atmConvention(Enum):
    FORWARD = "FORWARD"
    SPOT = "SPOT"
    DNS = "DELT_NEUTRAL_STRADDLE"

class deltaConvention(Enum):
    SPOT = "SPOT"
    FORWARD = "FORWARD"