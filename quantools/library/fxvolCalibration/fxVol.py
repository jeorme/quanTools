import math
import numpy as np
from datetime import datetime
from scipy.stats import norm
from quantools.analyticsTools.analyticsTools import yearFraction
from quantools.library.utilities.classObject import OptionDesc
from quantools.library.utilities.interpolation import leeExtrapolation, getInterpolatedValue, cubicSplineInterpolation
from quantools.library.utilities.solver import newtonSolver1D, findRoot
from quantools.library.utilities.utilitiesAccessor import getIndexBefore, pointFloorIndex
from quantools.library.fxvolCalibration.yieldCurve import discountFactorFromDays


class FxExpiryfxVolInfo:
    def __init__(self,forwardStrike, premiumAdjustmentIndicator,
                       deltaConventionAdjustment, sqrtVolYearFraction,
                       dfDom,volId,interpolationMethod="LINEAR",
                       interpSpace = "strike", atmVol = 0.1 ):
        self.forwardStrike = forwardStrike
        self.premiumAdjustmentIndicator = premiumAdjustmentIndicator #+1 premium adjusted, 0 not premium adjusted
        self.deltaConventionAdjustment = deltaConventionAdjustment #see getDeltaConventionAdjustment
        self.sqrtYfExpiryAsOf = sqrtVolYearFraction #yf asOf-expiry
        self.dfDom  = dfDom
        self.interpMethod =interpolationMethod
        self.interpSpace = interpSpace
        self.atmVol = atmVol
        self.volId = volId

##utilisties

def getDeltaConventionAdjustment(smileConvention, df):
    if smileConvention == "SPOT":
        return df
    return 1

## display


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
        surface[6 + jump][strikeColumn] = 0 if strike == 0.0 else math.log(abs(strike / fxVolInfo.forwardStrike))

    lastColumn = surface.shape[1] - 1  # Cell were we store ATM index

    atmIndex = outputATMIndex(expirySmileCurve)
    for atmPos in range(7):
        surface[smileCounter * 7 + atmPos][lastColumn] = atmIndex


def outputATMIndex(expirySmileCurve):
    for j in range(expirySmileCurve.shape[1]):
        if expirySmileCurve[4][j] == 100: #ATM
            return j
    return 0

def getJacobianSize(nbStrikesByExpiry, isSmileBroker):
    if isSmileBroker:
        return (nbStrikesByExpiry - 1) / 2
    return 0

##utilities

def getDeltaFromParity(forwardStrike, premiumAdjustmentIndicator, deltaConventionAdjustment, deltaFrom, toCallOrPut, strike):
	deltaParityConstant = getPremiumAdjustedRatioFromIndicator(forwardStrike, premiumAdjustmentIndicator, strike) * deltaConventionAdjustment
	return toCallOrPut * (- abs(deltaFrom) + deltaParityConstant)

def getPremiumAdjustedRatioFromIndicator(forward, premiumAdjustmentIndicator, strike):
	return (premiumAdjustmentIndicator * strike + (1 - premiumAdjustmentIndicator) * forward) / forward

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
    return (math.log(abs(forward/ strike)) + 0.5 * bsStdDev * bsStdDev) / bsStdDev

def getPlusInfinityValue():
    return 1e306

## vol computation
def getFxAtmPoint(fxVolInfo, atmConvention,  outputFxSmile, fxSpot, calibrationInstruments):
    realizedStdDev = fxVolInfo.atmVol * fxVolInfo.sqrtYfExpiryAsOf
    currentLine = calibrationInstruments[0][0]
    calibrationInstruments[0][0] = currentLine + 1
    getFxAtmDeltaAndStrikeFromVol(fxVolInfo, realizedStdDev, atmConvention, fxSpot, outputFxSmile, currentLine)
    outputFxSmile[2][int(currentLine)] = fxVolInfo.atmVol
    outputFxSmile[4][int(currentLine)] = 100
    if calibrationInstruments.shape[0] > currentLine and calibrationInstruments.shape[1] > 5:
        calibrationInstruments[int(currentLine)][2] = 100
        calibrationInstruments[int(currentLine)][1] = 0
        calibrationInstruments[int(currentLine)][4] = outputFxSmile[3][int(currentLine)]
        calibrationInstruments[int(currentLine)][5] = fxVolInfo.atmVol #atm vol

def constructFXVolSurface(data):
    asOfDate = datetime.strptime(data["asOfDate"],"%Y-%m-%d")
    surfaces = []
    for fxVol in  data["marketDataDefinitions"]["fxVolatilities"]:
        expiryInput = fxVol["expiries"]
        expiryInputValue = data["marketData"]["fxVolatilityQuotes"][0]["quotes"]
        nbStrikesByExpiry = 2 * len(expiryInput[0]["butterflyQuoteIds"]) + 1
        surface = np.zeros((len(expiryInput) * 7, nbStrikesByExpiry + 1))
        nblines = 7 if fxVol["smileInterpolationMethod"] == "CUBIC_SPLINE" else 6
        expirySmileCurve = np.zeros((nblines, nbStrikesByExpiry))
        domCur = fxVol["domesticCurrencyId"]
        forCur = fxVol["foreignCurrencyId"]
        spotDate, underlyingSpotValue = getFxInput(fxVol["currencyPairId"],data["marketData"]["fxRates"])
        volatilityBasis = fxVol["basis"]
        ycValuesDom,ycDefDom = getYcInput(fxVol["domesticDiscountId"],data["marketData"]["yieldCurveValues"],data["marketDataDefinitions"]["yieldCurves"])
        ycValuesFor, ycDefFor = getYcInput(fxVol["foreignDiscountId"], data["marketData"]["yieldCurveValues"],
                                     data["marketDataDefinitions"]["yieldCurves"])
        domDisc = fxVol["foreignDiscountId"]
        smileCounter = 0
        premiumAdjustmentIndicator = fxVol["premiumAdjusted"] * 1.0
        isSmileBroker = fxVol["strategyConvention"] == "BROKER_STRANGLE"
        for smileLine in fxVol["expiries"]:
            deliveryDate = datetime.strptime(smileLine["deliveryDate"],"%Y-%m-%d")
            dfFor = discountFactorFromDays( ycValuesFor, ycDefFor,asOfDate, spotDate, deliveryDate)
            dfDom = discountFactorFromDays( ycValuesDom, ycDefDom,asOfDate, spotDate, deliveryDate)
            sqrtVolYearFraction = math.sqrt(yearFraction(asOfDate, datetime.strptime(smileLine["expiryDate"],"%Y-%m-%d"), volatilityBasis))
            forwardStrike = underlyingSpotValue * dfFor / dfDom
            fxVolInfo = FxExpiryfxVolInfo(forwardStrike, premiumAdjustmentIndicator,
                           getDeltaConventionAdjustment(smileLine["deltaConvention"], dfFor), sqrtVolYearFraction,
                           dfDom, fxVol["id"] ,fxVol["smileInterpolationMethod"],
                           fxVol["smileInterpolationVariable"])

            getExpirySmile(forCur, domCur, nbStrikesByExpiry, smileLine, fxVolInfo, pow(10,-6),
                        underlyingSpotValue, expirySmileCurve,isSmileBroker,data["marketData"])
            fxCalibrationResultsDisplay(smileCounter, fxVolInfo, expirySmileCurve, surface)
            ++smileCounter
        surfaces.append(surface)
    return surfaces

def getYcInput(ycId,values,definitions):
    outputDef = {}
    for ycDef in definitions:
        if ycId == ycDef["id"]:
            outputDef = ycDef
    for ycVal in values:
        if ycId == ycVal["id"]:
            return  ycVal["discountFactors"],outputDef
    return outputDef

def getFxInput(currencyPairId,fxRates):
    for fx in fxRates:
        if currencyPairId==fx["currencyPairId"]:
            return datetime.strptime(fx["spotDate"],"%Y-%m-%d"),fx["quoteValue"]

def getExpirySmile(foreignCurrency, domesticCurrency, nbStrikesByExpiry, smileLine, fxVolInfo, fxVolTolerance,fxSpot, expirySmileCurve, isSmileB,marketData):

    jacobianSize = getJacobianSize(nbStrikesByExpiry, isSmileB)
    calibrationInstruments = np.zeros((3 * int(jacobianSize) + 1, 7 * (jacobianSize > 0) + 1)) # getJacobianSize() for the smile constaints coming from broker smile

    if calibrationInstruments.shape[0] > nbStrikesByExpiry:
        calibrationInstruments[nbStrikesByExpiry][0] = nbStrikesByExpiry

    fxVolInfo.atmVol = getQuote(marketData["fxVolatilityQuotes"],fxVolInfo.volId,smileLine["atmQuoteId"])
    getFxAtmPoint(fxVolInfo, smileLine["atmConvention"], expirySmileCurve, fxSpot, calibrationInstruments)

    strategyRank = 0
    for i in range(len(smileLine["butterflyQuoteIds"])):
        strategyRank +=1
        getBSVolFromBfRr(strategyRank, foreignCurrency, domesticCurrency, fxVolInfo,smileLine["butterflyQuoteIds"][i],smileLine["riskReversalQuoteIds"][i],marketData["fxVolatilityQuotes"],expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)



    computeInterpSpaceParam(fxVolInfo, expirySmileCurve)
    nbStrikeInTheSmile = int(calibrationInstruments[0][0])
    expirySmileCurve.reshape(expirySmileCurve.shape[0], nbStrikeInTheSmile)
    insertionSortExpirySmileStrike(nbStrikeInTheSmile, expirySmileCurve)

    if isSmileB:
        jacRepo = np.zeros((int(jacobianSize + 3), int(jacobianSize))) # 2 for LU pivoting + 1 for f0 = fct() to solve
        effectiveProblemDimension = len(smileLine["butterflyQuoteIds"])
        idLineFromSmile = expirySmileCurve[4][:]
        for strikeColumn in range(nbStrikeInTheSmile):
            idIndex = idLineFromSmile[strikeColumn]
            for i in range(nbStrikeInTheSmile):
                IdConstraint = calibrationInstruments[i][2]
                if idIndex == IdConstraint:
                    calibrationInstruments[i][3] = strikeColumn
                    break
        fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, expirySmileCurve,jacRepo,nbStrikesByExpiry)
    else:
        computeInterpolationHelperParams(expirySmileCurve, fxVolInfo.interpMethod)

def getQuote(marketData,volId,quoteId):
    for fxVolQuote in marketData:
        if fxVolQuote["id"] == volId:
            for quote in fxVolQuote["quotes"]:
                if quoteId == quote["quoteId"]:
                    return quote["value"]
    return 0

def getBSVolFromBfRr(strategyRank, foreignCurrency, domesticCurrency, fxVolInfo, bfDef,rrDef,fxVol, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry):
    rr = getQuote(fxVol,fxVolInfo.volId,rrDef["quoteId"])
    bf = getQuote(fxVol,fxVolInfo.volId,bfDef["quoteId"])
    delta = rrDef["delta"]
    volMS = fxVolInfo.atmVol + bf

    ###issue in computation
    priceMs = getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategyRank, delta,
            volMS, rr, 1, 3, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)
    priceMs += getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, -strategyRank, delta,
            volMS,  -rr, -1, 4, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)

    constraintLine = int(calibrationInstruments[0][0]) #current available line index
    calibIntsLine = int(calibrationInstruments[nbStrikesByExpiry][0])
    calibrationInstruments[nbStrikesByExpiry][0] = calibIntsLine + 1 # next avalaible line index
    calibrationInstruments[constraintLine-1][6] = calibIntsLine  #index of fitting param line
    calibrationInstruments[constraintLine-2][6] = calibIntsLine #index of fitting param line
    calibrationInstruments[calibIntsLine][1] = 1 #constraint & callPut type of the first part of the strangle
    calibrationInstruments[calibIntsLine][2] =2
    calibrationInstruments[calibIntsLine][5] = priceMs #target market price
    calibrationInstruments[calibIntsLine][6] = bf #fx butterfly quote
    calibrationInstruments[calibIntsLine][7] = expirySmileCurve[3][constraintLine-2] #delta of the strategy

def getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategyRank, deltaValue, volMS, rr,callPutIndicator,
                                               strikeColumn, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry):

    volatility = volMS + 0.5 * rr #rr  is signed depending on the fact the we buy or sell the call/put
    getFxOtmPointFromCallPutQuote(fxVolInfo, volatility, strategyRank, deltaValue,callPutIndicator,expirySmileCurve , calibrationInstruments)
    constraintLine = int(calibrationInstruments[0][0])
    delta = expirySmileCurve[3][constraintLine -1]
    realizedStdDev = volMS* fxVolInfo.sqrtYfExpiryAsOf
    K_MS = computeStrikeFromDelta(callPutIndicator * abs(delta), realizedStdDev, fxVolInfo.forwardStrike, fxVolInfo.deltaConventionAdjustment, callPutIndicator, fxVolInfo.premiumAdjustmentIndicator)
    calibrationInstruments[int(calibrationInstruments[nbStrikesByExpiry][0])][strikeColumn] = K_MS
    calibrationInstruments[int(calibrationInstruments[0][0] - 1)][5] = fxVolInfo.atmVol + 0.5*rr
    return getBlackSpotPrice(fxVolInfo.forwardStrike, K_MS, realizedStdDev, fxVolInfo.dfDom, callPutIndicator)



def getFxOtmPointFromCallPutQuote(fxVolInfo, volatility, recordIndexId, delta,callPutIndicator, outputFxSmile,
                                  calibrationInstruments):

    realizedStdDev = volatility * fxVolInfo.sqrtYfExpiryAsOf
    currentLine = int(calibrationInstruments[0][0])
    calibrationInstruments[0][0] = currentLine + 1
    outputFxSmile[3][currentLine] = delta * callPutIndicator
    outputFxSmile[1][currentLine] = computeStrikeFromDelta(callPutIndicator * abs(delta), realizedStdDev, fxVolInfo.forwardStrike, fxVolInfo.deltaConventionAdjustment, callPutIndicator,  fxVolInfo.premiumAdjustmentIndicator)
    outputFxSmile[2][currentLine] = volatility
    outputFxSmile[4][currentLine] = recordIndexId

    if calibrationInstruments.shape[0] > currentLine and calibrationInstruments.shape[1] > 4:
        calibrationInstruments[currentLine][2] = recordIndexId # id
        calibrationInstruments[currentLine][1] = 1 if recordIndexId >0 else -1 # constraint
        calibrationInstruments[currentLine][4] = outputFxSmile[3][currentLine] # delta constraint


def computeStrikeFromDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
	if premiumAdjustmentIndicator == 1:
		return computeStrikeFromAdjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator)
	return computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator)

def getBlackSpotPrice(forwardValue, strikeValue, bsStdDev, df, flavor):
	return df * getBlackForwardPrice(forwardValue, strikeValue, bsStdDev, flavor)

def computeStrikeFromAdjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator):
	delta = callPutIndicator * abs(delta) / deltaConventionFactor
	option = OptionDesc(callPutIndicator, bsStdDev, delta)
	if callPutIndicator == -1:
		return forward * newtonSolver1D(delta, 1, 1e-8, 10, getPremiumAdjustedDeltaKernel, option, "unused", "unused")
	kMax = computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator) / forward
	kMin = findRoot(strikeFromMaximumAdjustedDelta, 0.1 * kMax, kMax, option)
	return forward * findRoot(getPremiumAdjustedDeltaKernelBrent, kMin, 5 * kMax, option)

def getPremiumAdjustedDeltaKernel(x, optionDefinition, optional1, optional2):
	return impliedStrikeFromDeltaPremiumAdjusted(x, optionDefinition.stdDeviation, optionDefinition.callPutIndicator)

def getPremiumAdjustedDeltaKernelBrent(x, optionDefinition):
	return impliedStrikeFromDeltaPremiumAdjusted(x, optionDefinition.stdDeviation, optionDefinition.callPutIndicator) - optionDefinition.delta


def strikeFromMaximumAdjustedDelta(x, option):
	bsStdDev = option.stdDeviation
	d2 = getBSCallPutPriceMinusDCoefficient(1, x, bsStdDev)
	return bsStdDev * norm.cdf(d2) - 1/math.sqrt(2*math.pi)  * math.exp(-0.5 * d2 * d2)

def impliedStrikeFromDeltaPremiumAdjusted(x, stdDeviation, callPutIndicator):
	bsDMinus = getBSCallPutPriceMinusDCoefficient(1, x, stdDeviation)
	return callPutIndicator * x * norm.cdf(callPutIndicator * bsDMinus)

def getBSCallPutPriceMinusDCoefficient(forward, strike, bsStdDev):
	if (strike == 0): # when strike is near zero, N(d1) is equal to 1
		return getPlusInfinityValue()
	return (math.log(abs(forward / strike)) - 0.5 * bsStdDev * bsStdDev) / bsStdDev




def computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator):
	return (forward * math.exp(-callPutIndicator * norm.ppf(callPutIndicator * delta / deltaConventionFactor) * bsStdDev + 0.5 * bsStdDev*bsStdDev))


def getBlackForwardPrice(forwardValue, strikeValue, bsStdDev, flavor):
	if abs(bsStdDev)<pow(10,-14):
		return getVanillaIntrinsicValue(forwardValue, strikeValue, flavor)

	d1 = getBSCallPutPricePlusDCoefficient(forwardValue, strikeValue, bsStdDev)
	return  computeBlackFormula(flavor, forwardValue, strikeValue, norm.cdf(flavor * d1), bsStdDev, d1, 0, norm.cdf(flavor * (d1 - bsStdDev)))

def getVanillaIntrinsicValue(forwardRate, strike, flavor):
	return math.max(flavor * (forwardRate - strike), 0)

def computeBlackFormula(flavor, forwardRate, strike, cumulNormald1, volFactor, d1, stdNormald1, cumulNormald2):
	return flavor * (-strike * cumulNormald2 + forwardRate * cumulNormald1) # keep this formula order for instability result issue


def computeInterpSpaceParam(fxVolInfo, expirySmileCurve):
    for strikeColumn in range(expirySmileCurve.shape[1]):
        expirySmileCurve[0][strikeColumn] = computePointInterpSpaceParamFromDeltaOrStrike(fxVolInfo, expirySmileCurve[1][strikeColumn], expirySmileCurve[3][strikeColumn])

def computePointInterpSpaceParamFromDeltaOrStrike(fxVolInfo, strike, delta):
    if fxVolInfo.interpSpace == "DELTA_CALL" or fxVolInfo.interpSpace == "DELTA_PUT":
        callPutIndicator = -1 if fxVolInfo.interpSpace=="DELTA_PUT" else 1
        if callPutIndicator != 1 if delta>= 0 else -1:
            return getDeltaFromParity(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator, fxVolInfo.deltaConventionAdjustment, delta, callPutIndicator, strike)
        return delta
    if fxVolInfo.interpSpace == "strike":
        return strike
    if fxVolInfo.interpSpace == "logMoneyness":
        return math.log(strike / fxVolInfo.forwardStrike)

def insertionSortExpirySmileStrike(nbStrikeSmile, expirySmileCurve):
    for strikeColumn in range(nbStrikeSmile):
        for j in range(strikeColumn,0,-1):
            if expirySmileCurve[0][j] < expirySmileCurve[0][j-1]:
                reOrderingSmile(expirySmileCurve, j)

def reOrderingSmile(expirySmileCurve, j):
    exchange(expirySmileCurve, 0, j, j-1)
    exchange(expirySmileCurve, 1, j, j-1)
    exchange(expirySmileCurve, 2, j, j-1)
    exchange(expirySmileCurve, 3, j, j-1)
    exchange(expirySmileCurve, 4, j, j-1)

def exchange(expirySmileCurve, row, colIndex1, colIndex2):
    temp = expirySmileCurve[row][colIndex1]
    expirySmileCurve[row][colIndex1] = expirySmileCurve[row][colIndex2]
    expirySmileCurve[row][colIndex2] = temp

def computeInterpolationHelperParams(currentPoint, interpMethod):
    if interpMethod == "CUBIC_SPLINE":
        computeSecondDerivativeHelper(currentPoint[6][:], currentPoint[0][:], currentPoint[2][:], 0, 0, currentPoint[5][:])

def computeSecondDerivativeHelper(helper, points, values, lowerConstraint, upperConstraint, secondDerivative):
    secondDerivative[0] = lowerConstraint
    if len(values) < 3:
        for i in range(1,len(values)):
            secondDerivative[i] = lowerConstraint
        if len(secondDerivative) >= 2:
            secondDerivative[len(values) - 1] = upperConstraint
        return secondDerivative
    # tri - diagonal system with dominant diagonal solving
    helper[0] = lowerConstraint
    p0 = points[0]
    p1 = points[1]
    v0 = values[0]
    v1 = values[1]
    for i in range(1,len(values)-1):
        p2 = points[i + 1]
        v2 = values[i + 1]
        backwardDiff = p1 - p0
        forwardDiff = p2 - p1
        extendDiff = p2 - p0
        sig = backwardDiff / extendDiff
        p = sig * secondDerivative[i - 1] + 2.0
        secondDerivative[i] = (sig - 1.0) / p
        helper_i = (v2 - v1) / forwardDiff - (v1 - v0) / backwardDiff
        helper[i] = (6.0 * helper_i / extendDiff - sig * helper[i - 1]) / p
        p0 = p1
        p1 = p2
        v0 = v1
        v1 = v2
    secondDerivative[len(values) - 1] = upperConstraint
    for  k in range(len(values) - 2,0,-1):
        secondDerivative[k] = secondDerivative[k] * secondDerivative[k+1] + helper[k]
    return secondDerivative

def getCalibrationProblemDimension(smileLineStrategies):
    effectiveProblemDimension = 0
    for otmComponent  in smileLineStrategies.otm:
        effectiveProblemDimension = effectiveProblemDimension + 1

    return effectiveProblemDimension

def fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo,nbStrikesByExpiry):
    fitSmileForFxVolMarketWithMultiDimNewtonSolver(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo,nbStrikesByExpiry)

def fitSmileForFxVolMarketWithMultiDimNewtonSolver(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo,nbStrikesByExpiry):
    f0 = jacRepo[jacRepo.shape[0] - 1][:]
    for k in range(50):
        computeFxVolatilityNextGuess(calibrationPoint, f0, fxVolInfo, effectiveProblemDimension, calibrationInstruments,nbStrikesByExpiry)
        computeStrategiesSolverFunction(calibrationPoint, fxVolInfo, calibrationInstruments, f0,nbStrikesByExpiry)
        if getL1Norm(f0) <= fxVolTolerance:
            break

        if k == 0:
            computeStrategiesSolverJacobianFunction(effectiveProblemDimension, calibrationPoint, fxVolInfo, calibrationInstruments, f0, jacRepo,nbStrikesByExpiry)
            luDecompostionByCroutAlgorithm(effectiveProblemDimension, jacRepo, 1.0e-40)
        for i in range(effectiveProblemDimension):
            f0[i] = -f0[i]
        solveLinearSystemFromCroutLUDecomposition(effectiveProblemDimension, jacRepo, f0)
        if getL1Norm(f0) <= fxVolTolerance:
            break

def computeFxVolatilityNextGuess(currentPoint, incrementArray, commonInputs, effectiveProblemDimension, instrumentsToFit,nbStrikesByExpiry):
   for nextXi in range(effectiveProblemDimension):
        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + nextXi, incrementArray[nextXi], commonInputs, instrumentsToFit,nbStrikesByExpiry)
   computeInterpSpaceParam(commonInputs, currentPoint)
   computeInterpolationHelperParams(currentPoint, commonInputs.interpMethod)

def computeStrategiesSolverFunction(currentPoint, commonInputs, instrumentsToFit, fx,nbStrikesByExpiry):
    nextXi = 0
    for i in range(nbStrikesByExpiry,instrumentsToFit.shape[0]):
        instrumentLine = instrumentsToFit[i]
        callPutIndicator = instrumentLine[1] # also used to know if it is a repricing instrument
        if callPutIndicator != 0:
            fx[nextXi] = priceOneCalibrationInstrument(currentPoint, commonInputs, instrumentLine) - instrumentLine[5]
            nextXi +=1
    return fx

def priceOneCalibrationInstrument(calibrationPoint, commonInputs, instrumentLineToFit):
    callPutIndicator = instrumentLineToFit[1]
    delta = instrumentLineToFit[7]
    strike = instrumentLineToFit[3]
    interpSpaceVar = computePointInterpSpaceParamFromDeltaOrStrike(commonInputs, strike, delta)
    price = priceCallPutFromSmile(commonInputs.forwardStrike, commonInputs.dfDom, commonInputs.sqrtYfExpiryAsOf,
            commonInputs.interpMethod, calibrationPoint, strike, interpSpaceVar, callPutIndicator)
    strike = instrumentLineToFit[4]
    interpSpaceVar = computePointInterpSpaceParamFromDeltaOrStrike(commonInputs, strike, -delta)
    price += priceCallPutFromSmile(commonInputs.forwardStrike, commonInputs.dfDom, commonInputs.sqrtYfExpiryAsOf,
            commonInputs.interpMethod, calibrationPoint, instrumentLineToFit[4], interpSpaceVar, -callPutIndicator)
    return price

def priceCallPutFromSmile(forwardStrike, dfDom, sqrtYfExpiryAsOf, interpMethod, calibrationPoint, strike, interpSpaceVar, callPutIndicator):
    commonInput = initComonFxSmileInput(calibrationPoint, forwardStrike, sqrtYfExpiryAsOf)
    indexBefore = pointFloorIndex(commonInput.smileAxis, interpSpaceVar)

    vol = getVolatilityFromSmile(interpSpaceVar, commonInput, interpMethod, indexBefore)
    return getBlackSpotPrice(forwardStrike, strike, sqrtYfExpiryAsOf * vol, dfDom, callPutIndicator)

def initComonFxSmileInput(calibrationPoint, forwardStrike, sqrtVolYearFraction):
    commonInput = CommonFxSmileInputs()
    commonInput.volValues = calibrationPoint[2][:]
    commonInput.smileAxis = calibrationPoint[0][:]
    commonInput.secondDerivatives = calibrationPoint[5][:]
    commonInput.forwardStrike = forwardStrike
    commonInput.sqrtVolYearFraction = sqrtVolYearFraction
    return commonInput

class CommonFxSmileInputs:
    def __init__(self):
        self.smileAxis = np.zeros((1,2))
        self.volValues = np.zeros((1,2))
        self.secondDerivatives =  np.zeros((1,2))
        self.sqrtVolYearFraction = 0
        self.forwardStrike = 1
        self.userTargetPoint = 0
        self.volInterpolationMethod  = "LINEAR"
        self.volExtrapolBefore = "FLAT"
        self.volExtrapolAfter = "FLAT"
        self.smileConventionInput = "strike"
        self.deltaConvAdjInput = 1.0
        self.leeFactor = 1.0
        self.isPremiumInput = 0


def getVolatilityFromSmile(smilePoint, commonInput, volInterpolationMethod, indexBefore):
    volValues = commonInput.volValues
    curveLength = len(volValues)
    if curveLength == 1:
        return volValues[0]

    indexBefore = getVolIndexBefore(indexBefore, curveLength)
    smileAxis = commonInput.smileAxis

    if smileAxis[indexBefore] == smilePoint:
        return volValues[indexBefore]

    if smileAxis[indexBefore + 1] == smilePoint:
        return volValues[indexBefore + 1]

    if volInterpolationMethod == "CUBIC_SPLINE":
        secondDerivatives = commonInput.secondDerivatives
        return cubicSplineInterpolation(smilePoint, smileAxis[indexBefore], smileAxis[indexBefore + 1], volValues[indexBefore], volValues[indexBefore + 1], secondDerivatives[indexBefore], secondDerivatives[indexBefore + 1])

    if volInterpolationMethod == "lee":
        return leeExtrapolation(smileAxis, indexBefore, smilePoint, volValues, commonInput)

    return getInterpolatedValue(volInterpolationMethod, smilePoint, smileAxis[indexBefore], smileAxis[indexBefore+1], volValues[indexBefore], volValues[indexBefore+1])

def getVolIndexBefore(pointFloorIndex, listLength):
	if listLength <= 1:
		return 0
	if pointFloorIndex == listLength - 1:
		return pointFloorIndex - 1
	return getIndexBefore(pointFloorIndex, listLength)

def computeStrategiesSolverJacobianFunction(problemDimension, currentPoint, commonInputs, instrumentsToFit, fx, jacobian,nbStrikesByExpiry):
    for j in range(problemDimension):
        currentValue = instrumentsToFit[j + nbStrikesByExpiry][6]
        dx = 0.00001
        if currentValue != 0.0:
            dx *= abs(currentValue)
        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + j, dx, commonInputs, instrumentsToFit,nbStrikesByExpiry)
        computeInterpSpaceParam(commonInputs, currentPoint)
        computeInterpolationHelperParams(currentPoint, commonInputs.interpMethod)
        for i in range(problemDimension):
            instrumentLineToFit = instrumentsToFit[int(nbStrikesByExpiry + i)][:]
            diffPrice = priceOneCalibrationInstrument(currentPoint, commonInputs, instrumentLineToFit) - instrumentLineToFit[5]
            jacobian[i][j] = (diffPrice - fx[i]) / dx

        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + j, -dx, commonInputs, instrumentsToFit,nbStrikesByExpiry)

def luDecompostionByCroutAlgorithm(systemDimension, inAoutLu, TINY):

    #scalingArray stores the implicit scaling of each row.
    #Loop over rows to get the implicit scaling information.
    for i in range(systemDimension):
        big = 0
        for j in range(systemDimension):
            temp = abs(inAoutLu[i][j])
            if temp > big:
                big = temp

        if big == 0.0:
            print("Singular matrix in LUDecompostionByCroutAlgorithm")
            return 0.0
        #No nonzero largest element.
        inAoutLu[systemDimension+1][i]=1.0/big #Save the scaling.

    # This is the outermost kij loop.
    imax = 0
    for k in range(systemDimension):
        big = 0 # Initialize for the search for largest pivot element.
        for i in range(systemDimension):
            temp=  inAoutLu[systemDimension+1][i]*abs(inAoutLu[i][k])
            if (temp > big):# Is the figure of merit for the pivot better than
                big = temp #the best
                imax=i


        if k != imax:
            for j in range(systemDimension):
                temp=inAoutLu[imax][j]
                inAoutLu[imax][j]=inAoutLu[k][j]
                inAoutLu[k][j]=temp

            inAoutLu[systemDimension+1][imax]= inAoutLu[systemDimension+1][k] #Also interchange the scale factor.

        inAoutLu[systemDimension][k]=imax
        if (inAoutLu[k][k] == 0.0):
            inAoutLu[k][k]=TINY

        #If the pivot element is zero, the matrix is singular (at least to the precision of the
        #algorithm). For some applications on singular matrices, it is desirable to substitute
        # TINY for zero.
        for i in range(k+1,systemDimension):
            temp=inAoutLu[i][k] / inAoutLu[k][k] #Divide by the pivot element.
            for j in range(k+1,systemDimension): #Innermost loop: reduce remaining submatrix.
                inAoutLu[i][j] -= temp*inAoutLu[k][j]

def getL1Norm(x):
    maxVal = 0
    for i in range(len(x)):
        maxVal = max(maxVal, abs(x[i]))
    return maxVal

def solveLinearSystemFromCroutLUDecomposition(systemDimension, lu, secondMemberAndResult):
    ii = 0
    for i in range(systemDimension):
        #When ii is set to a positive value, it will become the
        #index of the first nonvanishing element of b. We now do the forward substitution. The
        #only new wrinkle is to unscramble the permutationas we go.
        ip = int(lu[systemDimension][i])
        sum = secondMemberAndResult[ip]
        secondMemberAndResult[ip] = secondMemberAndResult[i]
        if ii != 0:
            for j in range(ii-1, i):
                sum -= lu[i][j] * secondMemberAndResult[j]
        if sum != 0.0: #A nonzero element was encountered, so from now on we
            ii = i+1 #will have to do the sums in the loop above.

        secondMemberAndResult[i]=sum

    for i in range(systemDimension-1,-1,-1):#Now we do the backsubstitution,
        sum=secondMemberAndResult[i]
        for j in range(i+1, systemDimension):
            sum -= lu[i][j] * secondMemberAndResult[j]
        secondMemberAndResult[i] =sum / lu[i][i] #Store a component of the solution vector X.

def updateSolvingPointOneCoordinate(currentPoint, parameterIndex, incrementValue, commonInputs, instrumentsToFit,nbStrikesByExpiry):
    instrumentsToFit[parameterIndex][6] += incrementValue
    for i in range(nbStrikesByExpiry):
        constraintLine = instrumentsToFit[i][:]
        fittingParamIndex = constraintLine[6]
        if fittingParamIndex == parameterIndex:
            updateOneSmileAxisElement(currentPoint, commonInputs, constraintLine, instrumentsToFit)

def updateOneSmileAxisElement(calibrationPoint, commonInputs, constraintLine, instrumentsToFit):
    callPutIndicator = constraintLine[1] #used also to determine if it is a fitting instrument
    if callPutIndicator != 0: #to be repriced
        vol = constraintLine[5] #atmPlusHalfSignedRiskReversal
        indexLineOfFittingParam = int(constraintLine[6])
        vol += instrumentsToFit[indexLineOfFittingParam][6]  #add bf
        strikeColumnIndexInTheSmile = int(constraintLine[3])
        deltaConstraint = constraintLine[4]
        calibrationPoint[1][ strikeColumnIndexInTheSmile] = computeStrikeFromDelta(callPutIndicator * abs(deltaConstraint), vol * commonInputs.sqrtYfExpiryAsOf,
                commonInputs.forwardStrike, commonInputs.deltaConventionAdjustment, callPutIndicator, commonInputs.premiumAdjustmentIndicator)

        calibrationPoint[2][strikeColumnIndexInTheSmile] = vol
