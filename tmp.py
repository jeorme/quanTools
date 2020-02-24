import math
import numpy as np
from datetime import datetime
from scipy.stats import norm
from quantools.analyticsTools.analyticsTools import yearFraction

class FxExpiryfxVolInfo:
    def __init__(self,forwardStrike, premiumAdjustmentIndicator,
                       deltaConventionAdjustment, sqrtVolYearFraction,
                       dfDom, interpolationMethod="linear",
                       interpSpace = "strike", atmVol = 0.1):
        self.forwardStrike = forwardStrike
        self.premiumAdjustmentIndicator = premiumAdjustmentIndicator #+1 premium adjusted, 0 not premium adjusted
        self.deltaConventionAdjustment = deltaConventionAdjustment #see getDeltaConventionAdjustment
        self.sqrtYfExpiryAsOf = sqrtVolYearFraction #yf asOf-expiry
        self.dfDom  = dfDom
        self.interpMethod =interpolationMethod
        self.interpSpace = interpSpace
        self.atmVol = atmVol


def getDeltaConventionAdjustment(smileConvention, df):
    if smileConvention == "SPOT":
        return df
    return 1


def fxCalibrationResultsDisplay(smileCounter, fxVolInfo, expirySmileCurve, surface):
    jump = smileCounter * 7
    for strikeColumn in range(expirySmileCurve.shape[1]):
        delta = expirySmileCurve[3][strikeColumn]
        strike = expirySmileCurve[1][strikeColumn]
        deltaC = delta
        if deltaC <= 0:
            deltaC = getDeltaFromParity(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator,
                                        fxVolInfo.deltaConventionAdjustment, deltaC, 1, strike)
        surface[jump][strikeColumn] = deltaC
        deltaP = delta
        if deltaP >= 0:
            deltaP = getDeltaFromParity(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator,
                                        fxVolInfo.deltaConventionAdjustment, deltaP, -1, strike)
        surface[1 + jump][strikeColumn] = deltaP
        surface[2 + jump][strikeColumn] = delta
        surface[3 + jump][strikeColumn] = strike
        surface[4 + jump][strikeColumn] = expirySmileCurve[2][strikeColumn]
        surface[5 + jump][strikeColumn] = expirySmileCurve[5][strikeColumn]
        surface[6 + jump][strikeColumn] = 0 if strike == 0.0 else math.log(strike / fxVolInfo.forwardStrike)

    lastColumn = surface.shape[1] - 1  # Cell were we store ATM index

    atmIndex = outputATMIndex(expirySmileCurve)
    for atmPos in range(7):
        surface[smileCounter * 7 + atmPos][lastColumn] = atmIndex


def outputATMIndex(expirySmileCurve):
    for j in range(expirySmileCurve.shape[1]):
        if expirySmileCurve[4][j] == 100: #ATM
            return j
    return 0

def getDeltaFromParity(forwardStrike, premiumAdjustmentIndicator, deltaConventionAdjustment, deltaFrom, toCallOrPut, strike):
	deltaParityConstant = getPremiumAdjustedRatioFromIndicator(forwardStrike, premiumAdjustmentIndicator, strike) * deltaConventionAdjustment
	return toCallOrPut * (- abs(deltaFrom) + deltaParityConstant)

def getPremiumAdjustedRatioFromIndicator(forward, premiumAdjustmentIndicator, strike):
	return (premiumAdjustmentIndicator * strike + (1 - premiumAdjustmentIndicator) * forward) / forward

def getJacobianSize(nbStrikesByExpiry, isSmileBroker):
    if isSmileBroker:
        return (nbStrikesByExpiry - 1) / 2
    return 0

def getFxAtmPoint(fxVolInfo, atmConvention, recordIndexId, outputFxSmile, fxSpot, calibrationInstruments):
    realizedStdDev = fxVolInfo.atmVol * fxVolInfo.sqrtYfExpiryAsOf
    currentLine = calibrationInstruments[0][0]
    calibrationInstruments[0][0] = currentLine + 1
    getFxAtmDeltaAndStrikeFromVol(fxVolInfo, realizedStdDev, atmConvention, fxSpot, outputFxSmile, currentLine)
    outputFxSmile[2][int(currentLine)] = fxVolInfo.atmVol
    outputFxSmile[4][int(currentLine)] = recordIndexId
    if calibrationInstruments.shape[0] > currentLine and calibrationInstruments.shape[1] > 5:
        calibrationInstruments[int(currentLine)][2] = recordIndexId
        calibrationInstruments[int(currentLine)][1] = 0
        calibrationInstruments[int(currentLine)][4] = outputFxSmile[3][int(currentLine)]
        calibrationInstruments[int(currentLine)][5] = fxVolInfo.atmVol #atm vol

def getFxAtmDeltaAndStrikeFromVol(fxVolInfo, realizedStdDev, atmConvention, fxSpot, fxResults, currentLine):
    strike = getAtmStrike(atmConvention, fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator, realizedStdDev, fxSpot)
    fxResults[1][int(currentLine)] = strike
    fxResults[3][int(currentLine)] = computeDeltaFromStrike(strike, realizedStdDev, fxVolInfo.forwardStrike,
            fxVolInfo.deltaConventionAdjustment, 1.0,  fxVolInfo.premiumAdjustmentIndicator)

def getAtmStrike(atmStrikeQuotation, forwardStrike, premiumAdjustmentIndicator, realizedStdDev, underlyingSpotValue):
    if atmStrikeQuotation == "SPOT":
        return underlyingSpotValue
    if atmStrikeQuotation == "FORWARD":
        return forwardStrike
    if atmStrikeQuotation=="DELTA_NEUTRAL_STRADDLE":
        return getAtmStrikeDeltaNeutralStraddle(forwardStrike, premiumAdjustmentIndicator, realizedStdDev)

def getAtmStrikeDeltaNeutralStraddle(forwardStrike, premiumAdjustmentIndicator, realizedStdDev):
    return forwardStrike * math.exp((-2 * premiumAdjustmentIndicator + 1) * 0.5 * realizedStdDev * realizedStdDev)

def computeDeltaFromStrike(strike, bsStdDev, forward, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
    return callPutIndicator * deltaConventionFactor * getPremiumAdjustedRatioFromIndicator(forward, premiumAdjustmentIndicator, strike) * norm.cdf(callPutIndicator * (getBSCallPutPricePlusDCoefficient(forward, strike, bsStdDev) - premiumAdjustmentIndicator * bsStdDev))

def getBSCallPutPricePlusDCoefficient(forward, strike, bsStdDev):
    if strike == 0: # when strike is near zero, N(d1) is equal to 1
        return getPlusInfinityValue()
    return (math.log(forward/ strike) + 0.5 * bsStdDev * bsStdDev) / bsStdDev

def getPlusInfinityValue():
    return 1e306


def getInstrumentTypeEnum(instrumentType):
    if instrumentType=="call":
        return 1
    if instrumentType=="put":
        return -1
    if instrumentType=="strangle":
        return 2
    if instrumentType== "butterfly":
        return 3
    return 0



def getBSVolFromBfRr(strategyRank, foreignCurrency, domesticCurrency, fxVolInfo, strategy, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry):
    rr = data0D("FX_VOL", [strategy.riskReversal.instrumentName, foreignCurrency, domesticCurrency], calculationDate())
    rr *= strategy.riskReversal.instruments[0].direction
    bf = data0D("FX_VOL", [strategy.butterfly.instrumentName, foreignCurrency, domesticCurrency], calculationDate())
    volMS = fxVolInfo.atmVol + bf
    callPutIndicator = strategy.riskReversal.instruments[0].instrumentType
    priceMs = getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategy, strategyRank, strategy.riskReversal.instruments[0],
            volMS, rr, callPutIndicator, 3, expirySmileCurve, calibrationInstruments)
    priceMs += getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategy, -strategyRank, strategy.riskReversal.instruments[1],
            volMS,  -rr, -callPutIndicator, 4, expirySmileCurve, calibrationInstruments)
    if strategy.butterfly.strategyConvention.target == "price":
        constraintLine = calibrationInstruments[0][0] #current available line index
        calibIntsLine = calibrationInstruments[nbStrikesByExpiry][0]
        calibrationInstruments[nbStrikesByExpiry][0] = calibIntsLine + 1 # next avalaible line index
        calibrationInstruments[constraintLine-1][6] = calibIntsLine  #index of fitting param line
        calibrationInstruments[constraintLine-2][6] = calibIntsLine #index of fitting param line
        calibrationInstruments[calibIntsLine][1] = callPutIndicator #constraint & callPut type of the first part of the strangle
        calibrationInstruments[calibIntsLine][2] = getInstrumentTypeEnum (strategy.butterfly.strategyConvention.type) #fx instrument type
        calibrationInstruments[calibIntsLine][5] = priceMs #target market price
        calibrationInstruments[calibIntsLine][6] = bf #fx butterfly quote
        calibrationInstruments[calibIntsLine][7] = expirySmileCurve[3][constraintLine-2] #delta of the strategy




def constructFXVolSurface(data):
    asOfDate = datetime.strptime(data["asOfDate"],"%Y-%m-%d")
    expiryInput = data["marketDataDefinitions"]["fxVolatilities"][0]["expiries"]
    expiryInputValue = data["marketData"]["fxVolatilityQuotes"][0]["quotes"]
    nbStrikesByExpiry = 2 * len(expiryInput[0]["butterflyQuoteIds"]) + 1
    surface = np.zeros((len(expiryInput) * 7, nbStrikesByExpiry + 1))
    nblines = 7 if data["marketDataDefinitions"]["fxVolatilities"][0]["smileInterpolationMethod"] == "CUBIC_SPLINE" else 6
    expirySmileCurve = np.zeros((nblines, nbStrikesByExpiry))
    domCur = data["marketDataDefinitions"]["fxVolatilities"][0]["domesticCurrencyId"]
    forCur = data["marketDataDefinitions"]["fxVolatilities"][0]["foreignCurrencyId"]
    spotDate = data["marketData"]["fxRates"][0]["spotDate"]
    volatilityBasis = data["marketDataDefinitions"]["fxVolatilities"][0]["basis"]
    underlyingSpotValue =  data["marketData"]["fxRates"][0]["quoteValue"]
    forDisc =data["marketDataDefinitions"]["fxVolatilities"][0]["domesticDiscountId"]
    domDisc = data["marketDataDefinitions"]["fxVolatilities"][0]["foreignDiscountId"]
    smileCounter = 0
    premiumAdjustmentIndicator = data["marketDataDefinitions"]["fxVolatilities"][0]["premiumAdjusted"] * 1.0
    isSmileBroker =data["marketDataDefinitions"]["fxVolatilities"][0]["strategyConvention"] == "BROKER_STRANGLE"
    for smileLine in expiryInput:
        nbDaysDeliveryDate = smileLine["deliveryDate"]
        dfFor = 0.95 #discountFactorFromDays(forDisc, spotDate, nbDaysDeliveryDate)
        dfDom = 0.96 #discountFactorFromDays(domDisc, spotDate, nbDaysDeliveryDate)
        sqrtVolYearFraction = math.sqrt(yearFraction(asOfDate, datetime.strptime(smileLine["expiryDate"],"%Y-%m-%d"), volatilityBasis))
        forwardStrike = underlyingSpotValue * dfFor / dfDom
        fxVolInfo = FxExpiryfxVolInfo(forwardStrike, premiumAdjustmentIndicator,
                       getDeltaConventionAdjustment(smileLine["deltaConvention"], dfFor), sqrtVolYearFraction,
                       dfDom, data["marketDataDefinitions"]["fxVolatilities"][0]["smileInterpolationMethod"],
                       data["marketDataDefinitions"]["fxVolatilities"][0]["smileInterpolationVariable"], 0.10)
        getExpirySmile(forCur, domCur, nbStrikesByExpiry, data, fxVolInfo, pow(10,-6),
                    underlyingSpotValue, expirySmileCurve,isSmileBroker)
        fxCalibrationResultsDisplay(smileCounter, fxVolInfo, expirySmileCurve, surface)
        ++smileCounter

    return surface


def getExpirySmile(foreignCurrency, domesticCurrency, nbStrikesByExpiry, data, fxVolInfo, fxVolTolerance,fxSpot, expirySmileCurve,isSmileB):
    jacobianSize = getJacobianSize(nbStrikesByExpiry, isSmileB)
    calibrationInstruments = np.zeros((3 * int(jacobianSize) + 1, int(7.0 * (jacobianSize > 0) + 1))) # getJacobianSize() for the smile constaints coming from broker smile

    fxVolInfo.atmVol = data["marketData"]["fxVolatilityQuotes"][0]["quotes"][2]["value"]
    getFxAtmPoint(fxVolInfo, data["marketDataDefinitions"]["fxVolatilities"][0]["expiries"][0]["atmConvention"], 100, expirySmileCurve, fxSpot, calibrationInstruments)

    # strategyRank = 0
    for otmComponent  in smileStrategies.otm:
         getBSVolFromBfRr(recordIndexId, foreignCurrency, domesticCurrency, fxVolInfo, otmRecord, outputFxSmile, calibrationInstruments,nbStrikesByExpiry)

    computeInterpSpaceParam(fxVolInfo, expirySmileCurve)
    nbStrikeInTheSmile = calibrationInstruments[0][0]
    resize(expirySmileCurve, expirySmileCurve.shape[0], nbStrikeInTheSmile)
    # insertionSortExpirySmileStrike(nbStrikeInTheSmile, expirySmileCurve)
    #
    # if isSmileB:
    #     jacRepo = matrix(jacobianSize + 3, jacobianSize, 0.0) # 2 for LU pivoting + 1 for f0 = fct() to solve
    #     effectiveProblemDimension = getCalibrationProblemDimension(smileStrategies, isOtmDefined)
    #     idLineFromSmile = matrixLine(expirySmileCurve, 4)
    #     for strikeColumn =0; strikeColumn < nbStrikeInTheSmile; strikeColumn ++:
    #         idIndex = idLineFromSmile[strikeColumn]
    #         for i = 0;i < nbStrikeInTheSmile;i ++:
    #             IdConstraint = calibrationInstruments[i][2]
    #                 if idIndex == IdConstraint:
    #                     calibrationInstruments[i][3] = strikeColumn
    #                     break
    #     fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, expirySmileCurve,jacRepo)
    #
    # else:
    #     computeInterpolationHelperParams(expirySmileCurve, fxVolInfo.interpMethod)
