import math
import numpy as np
from datetime import datetime
from scipy.stats import norm
from quantools.analyticsTools.analyticsTools import yearFraction


### class definition

class FxExpiryfxVolInfo:
    def __init__(self,forwardStrike, premiumAdjustmentIndicator,
                       deltaConventionAdjustment, sqrtVolYearFraction,
                       dfDom,volId,interpolationMethod="linear",
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

def getJacobianSize(nbStrikesByExpiry, isSmileBroker):
    if isSmileBroker:
        return (nbStrikesByExpiry - 1) / 2
    return 0


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
    return (math.log(forward/ strike) + 0.5 * bsStdDev * bsStdDev) / bsStdDev

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
        forDisc = fxVol["domesticDiscountId"]
        domDisc = fxVol["foreignDiscountId"]
        smileCounter = 0
        premiumAdjustmentIndicator = fxVol["premiumAdjusted"] * 1.0
        isSmileBroker = fxVol["strategyConvention"] == "BROKER_STRANGLE"
        for smileLine in fxVol["expiries"]:
            nbDaysDeliveryDate = smileLine["deliveryDate"]
            dfFor = 0.95 #discountFactorFromDays(forDisc, spotDate, nbDaysDeliveryDate)
            dfDom = 0.96 #discountFactorFromDays(domDisc, spotDate, nbDaysDeliveryDate)
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

def getFxInput(currencyPairId,fxRates):
    for fx in fxRates:
        if currencyPairId==fx["currencyPairId"]:
            return fx["spotDate"],fx["quoteValue"]

def getExpirySmile(foreignCurrency, domesticCurrency, nbStrikesByExpiry, smileLine, fxVolInfo, fxVolTolerance,fxSpot, expirySmileCurve, isSmileB,marketData):

    jacobianSize = getJacobianSize(nbStrikesByExpiry, isSmileB)
    calibrationInstruments = np.zeros((3 * int(jacobianSize) + 1, 7 * (jacobianSize > 0) + 1)) # getJacobianSize() for the smile constaints coming from broker smile

    if calibrationInstruments.shape[0] > nbStrikesByExpiry:
        calibrationInstruments[nbStrikesByExpiry][0] = nbStrikesByExpiry

    fxVolInfo.atmVol = getQuote(marketData["fxVolatilityQuotes"],fxVolInfo.volId,smileLine["atmQuoteId"])
    getFxAtmPoint(fxVolInfo, smileLine["atmConvention"], expirySmileCurve, fxSpot, calibrationInstruments)

    strategyRank = 0
    for i in range(len(smileLine["butterflyQuoteIds"])):
        getBSVolFromBfRr(++strategyRank, foreignCurrency, domesticCurrency, fxVolInfo,smileLine["butterflyQuoteIds"][i],smileLine["riskReversalQuoteIds"][i],marketData["fxVolatilityQuotes"],expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)


    #computeInterpSpaceParam(fxVolInfo, expirySmileCurve)
    #nbStrikeInTheSmile = calibrationInstruments[0][0]
    #resize(expirySmileCurve, height(expirySmileCurve), nbStrikeInTheSmile)
    #insertionSortExpirySmileStrike(nbStrikeInTheSmile, expirySmileCurve)

    #if isSmileB:
    #    jacRepo = matrix(jacobianSize + 3, jacobianSize, 0.0) # 2 for LU pivoting + 1 for f0 = fct() to solve
    #    effectiveProblemDimension = getCalibrationProblemDimension(smileStrategies, isOtmDefined)
    #    idLineFromSmile = matrixLine(expirySmileCurve, 4)
    #    for strikeColumn =0; strikeColumn < nbStrikeInTheSmile; strikeColumn ++:
    #        idIndex = idLineFromSmile[strikeColumn]
    #        for i = 0;i < nbStrikeInTheSmile;i ++:
    #            IdConstraint = calibrationInstruments[i][2]
    #                if idIndex == IdConstraint:
    #                    calibrationInstruments[i][3] = strikeColumn
    #                    break
    #    fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, expirySmileCurve,jacRepo)
    #else:
    #    computeInterpolationHelperParams(expirySmileCurve, fxVolInfo.interpMethod)

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
    priceMs = getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategyRank, delta,
            volMS, rr, 1, 3, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)
    priceMs += getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, -strategyRank, delta,
            volMS,  -rr, -1, 4, expirySmileCurve, calibrationInstruments,nbStrikesByExpiry)
    #if strategy.butterfly.strategyConvention.target == "price":
    #    constraintLine = calibrationInstruments[0][0] #current available line index
    #    calibIntsLine = calibrationInstruments[nbStrikesByExpiry][0]
    #    calibrationInstruments[nbStrikesByExpiry][0] = calibIntsLine + 1 # next avalaible line index
    #    calibrationInstruments[constraintLine-1][6] = calibIntsLine  #index of fitting param line
    #    calibrationInstruments[constraintLine-2][6] = calibIntsLine #index of fitting param line
    #    calibrationInstruments[calibIntsLine][1] = callPutIndicator #constraint & callPut type of the first part of the strangle
    #    calibrationInstruments[calibIntsLine][2] = getInstrumentTypeEnum (strategy.butterfly.strategyConvention.type) #fx instrument type
    #    calibrationInstruments[calibIntsLine][5] = priceMs #target market price
    #    calibrationInstruments[calibIntsLine][6] = bf #fx butterfly quote
    #    calibrationInstruments[calibIntsLine][7] = expirySmileCurve[3][constraintLine-2] #delta of the strategy

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
	#delta = callPutIndicator * abs(delta) / deltaConventionFactor
	#option = OptionDesc(callPutIndicator, bsStdDev, delta)
	#if callPutIndicator == -1:
#		return forward * newtonSolver1D(delta, 1, 1e-8, 10, getPremiumAdjustedDeltaKernel, option, "unused", "unused")
#	kMax = computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator) / forward
#	kMin = findRoot(strikeFromMaximumAdjustedDelta, 0.1 * kMax, kMax, option)
	#return forward * findRoot(getPremiumAdjustedDeltaKernelBrent, kMin, 5 * kMax, option)
    return 100


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
