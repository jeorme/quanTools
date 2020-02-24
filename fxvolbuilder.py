import math
import numpy as np
from datetime import datetime
from quantools.analyticsTools.analyticsTools import yearFraction


def constructFXVolSurface(data):
    asOfDate = datetime.strptime(data["asOfDate"],"%Y-%m-%d")

    for fxvol in data["marketDataDefinitions"]["fxVolatilities"]:
        expiryInput =fxvol["expiries"]
        expiryInputValue = data["marketData"]["fxVolatilityQuotes"][0]["quotes"]
        nbStrikesByExpiry = 2 * len(expiryInput[0]["butterflyQuoteIds"]) + 1
        surface = np.zeros((len(expiryInput) * 7, nbStrikesByExpiry + 1))
        nblines = 7 if fxvol["smileInterpolationMethod"] == "CUBIC_SPLINE" else 6
        expirySmileCurve = np.zeros((nblines, nbStrikesByExpiry))
        domCur =fxvol["domesticCurrencyId"]
        forCur =fxvol["foreignCurrencyId"]
        spotDate = data["marketData"]["fxRates"][0]["spotDate"]
        volatilityBasis =fxvol["basis"]
        underlyingSpotValue = data["marketData"]["fxRates"][0]["quoteValue"]
        forDisc =fxvol["domesticDiscountId"]
        domDisc =fxvol["foreignDiscountId"]
        smileCounter = 0
        premiumAdjustmentIndicator =fxvol["premiumAdjusted"] * 1.0
        isSmileBroker =fxvol["strategyConvention"] == "BROKER_STRANGLE"

        for smileLine in expiryInput:
            nbDaysDeliveryDate = datetime.strptime(smileLine["deliveryDate"])
            dfFor = 0.95 #discountFactorFromDays(forDisc, spotDate, nbDaysDeliveryDate)
            dfDom = 0.96 #discountFactorFromDays(domDisc, spotDate, nbDaysDeliveryDate)
            sqrtVolYearFraction = math.sqrt(yearFraction(asOfDate, datetime.strptime(smileLine["expiryDate"],"%Y-%m-%d"), volatilityBasis))
            forwardStrike = underlyingSpotValue * dfFor / dfDom
            fxVolInfo = FxExpiryfxVolInfo(forwardStrike, premiumAdjustmentIndicator,
                           getDeltaConventionAdjustment(smileLine["deltaConvention"], dfFor), sqrtVolYearFraction,
                           dfDom,fxvol["smileInterpolationMethod"],
                          fxvol["smileInterpolationVariable"], 0.10)
            getExpirySmile(forCur, domCur, nbStrikesByExpiry, data, fxVolInfo, pow(10,-6), underlyingSpotValue, expirySmileCurve,isSmileBroker,nbStrikesByExpiry)
            fxCalibrationResultsDisplay(smileCounter, fxVolInfo, expirySmileCurve, surface)
            ++smileCounter

    return surface


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
        return int((nbStrikesByExpiry - 1) / 2)
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

#### OK

def getExpirySmile(foreignCurrency, domesticCurrency, nbStrikesByExpiry, smileStrategies, fxVolInfo, fxVolTolerance,fxSpot, expirySmileCurve, isSmileB, nbStrikesByExpiry):

    jacobianSize = getJacobianSize(nbStrikesByExpiry, isSmileB)
    calibrationInstruments = np.zeros((3 * jacobianSize + 1, 7 * (jacobianSize > 0) + 1)) # getJacobianSize() for the smile constaints coming from broker smile

    if calibrationInstruments.shape[0] > nbStrikesByExpiry:
        calibrationInstruments[nbStrikesByExpiry][0] = nbStrikesByExpiry

    fxVolInfo.atmVol = data0D("FX_VOL", [smileStrategies.atm.instrumentName, foreignCurrency, domesticCurrency], calculationDate())
    getFxAtmPoint(fxVolInfo, smileStrategies.atm.atmConvention, smileStrategies.atm.instruments[0], 100, expirySmileCurve, fxSpot, calibrationInstruments)

    if isOtmDefined:
        strategyRank = 0
        for otmComponent  in smileStrategies.otm:
            getFxOtmPoint(foreignCurrency, domesticCurrency, fxVolInfo, otmComponent, ++strategyRank, expirySmileCurve, calibrationInstruments)

    computeInterpSpaceParam(fxVolInfo, expirySmileCurve)
    nbStrikeInTheSmile = calibrationInstruments[0][0]
    resize(expirySmileCurve, height(expirySmileCurve), nbStrikeInTheSmile)
    insertionSortExpirySmileStrike(nbStrikeInTheSmile, expirySmileCurve)

    if isSmileB:
        jacRepo = matrix(jacobianSize + 3, jacobianSize, 0.0) # 2 for LU pivoting + 1 for f0 = fct() to solve
        effectiveProblemDimension = getCalibrationProblemDimension(smileStrategies, isOtmDefined)
        idLineFromSmile = matrixLine(expirySmileCurve, 4)
        for strikeColumn =0; strikeColumn < nbStrikeInTheSmile; strikeColumn ++:
            idIndex = idLineFromSmile[strikeColumn]
            for i = 0;i < nbStrikeInTheSmile;i ++:
                IdConstraint = calibrationInstruments[i][2]
                    if idIndex == IdConstraint:
                        calibrationInstruments[i][3] = strikeColumn
                        break
        fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, expirySmileCurve,jacRepo)

    else:
        computeInterpolationHelperParams(expirySmileCurve, fxVolInfo.interpMethod)





def computeStrike(forwardStrike, premiumAdjustmentIndicator, deltaConventionAdjustment, realizedStdDev, strikeQuotationType, quotedStrike, callPutIndicator):
	if strikeQuotationType == "delta":
		return computeStrikeFromDelta(callPutIndicator * abs(quotedStrike), realizedStdDev, forwardStrike, deltaConventionAdjustment, callPutIndicator, premiumAdjustmentIndicator)
	if strikeQuotationType == "strike":
		return quotedStrike
	if strikeQuotationType == "logMoneyness":
		return forwardStrike * math.exp(quotedStrike)


def computeStrikeFromDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
	if premiumAdjustmentIndicator == 1:
		return computeStrikeFromAdjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator)
	return computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator)


def computeStrikeFromAdjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator):
	delta = callPutIndicator * abs(delta) / deltaConventionFactor
	option = OptionDesc(callPutIndicator, bsStdDev, delta)
	if callPutIndicator == -1:
		return forward * newtonSolver1D(delta, 1, 1e-8, 10, getPremiumAdjustedDeltaKernel, option, "unused", "unused")
	kMax = computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator) / forward
	kMin = findRoot(strikeFromMaximumAdjustedDelta, 0.1 * kMax, kMax, option)
	return forward * findRoot(getPremiumAdjustedDeltaKernelBrent, kMin, 5 * kMax, option)


def computeStrikeFromUnadjustedDelta(delta, bsStdDev, forward, deltaConventionFactor, callPutIndicator)
	return (forward * math.exp(-callPutIndicator * inverseNormalCDF(callPutIndicator * delta / deltaConventionFactor) * bsStdDev + 0.5 * bsStdDev*bsStdDev))

def computeDeltaFromStrike(strike, bsStdDev, forward, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
	return callPutIndicator * deltaConventionFactor * getPremiumAdjustedRatioFromIndicator(forward, premiumAdjustmentIndicator, strike) *
			normalCDF(callPutIndicator * (getBSCallPutPricePlusDCoefficient(forward, strike, bsStdDev) - premiumAdjustmentIndicator * bsStdDev))


class OptionDesc:
    def __init__(self):
	    self.callPutIndicator = 1.0 #+1 for call, -1 for put
	    self.stdDeviation = 1.0
	    self.delta = 1.0

def getFxOtmPointFromCallPutQuoteFromStrangle(fxVolInfo, strategy, strategyRank, callPutRecord, volMS, rr,callPutIndicator,strikeColumn, expirySmileCurve, calibrationInstruments):
    priceMs = 0
    volatility = volMS + 0.5 * rr #rr  is signed depending on the fact the we buy or sell the call/put
    getFxOtmPointFromCallPutQuote(fxVolInfo, volatility, strategyRank, callPutRecord, expirySmileCurve , calibrationInstruments)
    if strategy.butterfly.strategyConvention.target == "price":
        constraintLine = calibrationInstruments[0][0]
        delta = expirySmileCurve[3][constraintLine -1]
        realizedStdDev = volMS* fxVolInfo.sqrtYfExpiryAsOf
        K_MS = computeStrikeFromDelta(callPutIndicator * abs(delta), realizedStdDev, fxVolInfo.forwardStrike, fxVolInfo.deltaConventionAdjustment, callPutIndicator, fxVolInfo.premiumAdjustmentIndicator)
        calibrationInstruments[calibrationInstruments[nbStrikesByExpiry][0]][strikeColumn] = K_MS
        calibrationInstruments[calibrationInstruments[0][0] - 1][5] = fxVolInfo.atmVol + 0.5*rr
        priceMs = getBlackSpotPrice(fxVolInfo.forwardStrike, K_MS, realizedStdDev, fxVolInfo.dfDom, callPutIndicator)

    return priceMs

def getFxOtmPointFromCallPutQuote(fxVolInfo, volatility, recordIndexId, otmInstrument, outputFxSmile, calibrationInstruments):
    realizedStdDev = volatility * fxVolInfo.sqrtYfExpiryAsOf
    callPutIndicator = otmInstrument.instrumentType
    currentLine = calibrationInstruments[0][0]
    calibrationInstruments[0][0] = currentLine + 1
    strikeQuotationType = otmInstrument.strikeQuotation.type
    strikeQuotationValue = otmInstrument.strikeQuotation.quotedValue
    outputFxSmile[3][currentLine] = computeDelta(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator,
                                             fxVolInfo.deltaConventionAdjustment, realizedStdDev, strikeQuotationType,
                                             strikeQuotationValue, callPutIndicator)
    outputFxSmile[1][currentLine] = computeStrike(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator,
                                              fxVolInfo.deltaConventionAdjustment, realizedStdDev, strikeQuotationType,
                                              strikeQuotationValue, callPutIndicator)
    outputFxSmile[2][currentLine] = volatility
    outputFxSmile[4][currentLine] = recordIndexId
    if height(calibrationInstruments) > currentLine and width(calibrationInstruments) > 4:
        calibrationInstruments[currentLine][2] = recordIndexId # id
        calibrationInstruments[currentLine][1] = sign(recordIndexId) # constraint
        calibrationInstruments[currentLine][4] = outputFxSmile[3][currentLine] # delta constraint

def computeDelta(forwardStrike, premiumAdjustmentIndicator, deltaConventionAdjustment, realizedStdDev, strikeQuotationType, quotedStrike, callPutIndicator):
    if strikeQuotationType == "logMoneyness":
        quotedStrike = forwardStrike * math.exp(quotedStrike)
    if strikeQuotationType == "strike" or strikeQuotationType == "logMoneyness":
        quotedStrike = computeDeltaFromStrike(quotedStrike, realizedStdDev, forwardStrike,
                deltaConventionAdjustment, callPutIndicator, premiumAdjustmentIndicator)

    return callPutIndicator * abs(quotedStrike)

def getBlackSpotPrice(forwardValue, strikeValue, bsStdDev, df, flavor):
	return df * getBlackForwardPrice(forwardValue, strikeValue, bsStdDev, flavor)

def getBlackForwardPrice(forwardValue, strikeValue, bsStdDev, flavor):
	if isZero(bsStdDev):
		return getVanillaIntrinsicValue(forwardValue, strikeValue, flavor)

	d1 = getBSCallPutPricePlusDCoefficient(forwardValue, strikeValue, bsStdDev)
	return  computeBlackFormula(flavor, forwardValue, strikeValue, normalCDF(flavor * d1), bsStdDev, d1, 0, normalCDF(flavor * (d1 - bsStdDev)))

def getVanillaIntrinsicValue(forwardRate, strike, flavor):
	return max(flavor * (forwardRate - strike), 0)

def getBSCallPutPricePlusDCoefficient(forward, strike, bsStdDev):
	if strike == 0: # when strike is near zero, N(d1) is equal to 1
		return getPlusInfinityValue()
	return (math.log(forward/ strike) + 0.5 * bsStdDev * bsStdDev) / bsStdDev

def computeBlackFormula(flavor, forwardRate, strike, cumulNormald1, volFactor, d1, stdNormald1, cumulNormald2):
	return flavor * (-strike * cumulNormald2 + forwardRate * cumulNormald1) # keep this formula order for instability result issue

def computeInterpSpaceParam(fxVolInfo, expirySmileCurve):
    for strikeColumn = 0 ; strikeColumn <width(expirySmileCurve); ++strikeColumn:
        expirySmileCurve[0][strikeColumn] = computePointInterpSpaceParamFromDeltaOrStrike(fxVolInfo, expirySmileCurve[1][strikeColumn], expirySmileCurve[3][strikeColumn])

def computePointInterpSpaceParamFromDeltaOrStrike(fxVolInfo, strike, delta):
    if fxVolInfo.interpSpace == "deltaCall" or fxVolInfo.interpSpace == "deltaPut":
        callPutIndicator = getDeltaCallOrPutIndicator(fxVolInfo.interpSpace)
        if callPutIndicator != sign(delta):
            return getDeltaFromParity(fxVolInfo.forwardStrike, fxVolInfo.premiumAdjustmentIndicator, fxVolInfo.deltaConventionAdjustment, delta, callPutIndicator, strike)
        return delta
    if fxVolInfo.interpSpace == "strike":
        return strike
    if fxVolInfo.interpSpace == "logMoneyness":
        return getLogMoneynessFromStrike(fxVolInfo.forwardStrike, strike)

def getDeltaCallOrPutIndicator(deltaCallPut):
	if deltaCallPut == "deltaPut":
		return -1
	return 1

def getLogMoneynessFromStrike(forward, strike):
	return math.log(strike / forward)

def insertionSortExpirySmileStrike(nbStrikeSmile, expirySmileCurve):
    for strikeColumn =0; strikeColumn < nbStrikeSmile; strikeColumn++):
        for j = strikeColumn; j > 0; j--:
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

def getCalibrationProblemDimension(smileLineStrategies, isOtmDefined):
    effectiveProblemDimension = 0
    if isOtmDefined:
        for otmComponent  in smileLineStrategies.otm:
            if isDefined(otmComponent.butterfly) and isDefined(otmComponent.riskReversal) and otmComponent.butterfly.strategyConvention.target == "price":
                effectiveProblemDimension++

    return effectiveProblemDimension

def fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo):
    fitSmileForFxVolMarketWithMultiDimNewtonSolver(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo)


def fitSmileForFxVolMarketWithMultiDimNewtonSolver(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, calibrationPoint, jacRepo):
    f0 = matrixLine(jacRepo, height(jacRepo) - 1)
    for def k =0;k < 50;k + +:
        computeFxVolatilityNextGuess(calibrationPoint, f0, fxVolInfo, effectiveProblemDimension, calibrationInstruments)
        computeStrategiesSolverFunction(calibrationPoint, fxVolInfo, calibrationInstruments, f0)
    if getL1Norm(f0) <= fxVolTolerance:
        break
    if k == 0:
        computeStrategiesSolverJacobianFunction(effectiveProblemDimension, calibrationPoint, fxVolInfo, calibrationInstruments, f0, jacRepo)
        luDecompostionByCroutAlgorithm(effectiveProblemDimension, jacRepo, 1.0e-40)
    for i = 0;i < effectiveProblemDimension;i + +:
        f0[i] = -f0[i]
        solveLinearSystemFromCroutLUDecomposition(effectiveProblemDimension, jacRepo, f0)
        if getL1Norm(f0) <= fxVolTolerance:
            break

def computeFxVolatilityNextGuess(currentPoint, incrementArray, commonInputs, effectiveProblemDimension, instrumentsToFit):
   for nextXi = 0;  nextXi < effectiveProblemDimension; ++nextXi:
        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + nextXi, incrementArray[nextXi], commonInputs, instrumentsToFit)
   computeInterpSpaceParam(commonInputs, currentPoint)
   computeInterpolationHelperParams(currentPoint, commonInputs.interpMethod)

def updateSolvingPointOneCoordinate(currentPoint, parameterIndex, incrementValue, commonInputs, instrumentsToFit):
    instrumentsToFit[parameterIndex][6] += incrementValue
    for i = 0; i < nbStrikesByExpiry; ++i:
        constraintLine = matrixLine(instrumentsToFit, i)
        fittingParamIndex = constraintLine[6]
        if fittingParamIndex == parameterIndex:
            updateOneSmileAxisElement(currentPoint, commonInputs, constraintLine, instrumentsToFit)


def updateOneSmileAxisElement(calibrationPoint, commonInputs, constraintLine, instrumentsToFit):
    callPutIndicator = constraintLine[1] #used also to determine if it is a fitting instrument
    if callPutIndicator != 0: #to be repriced
        vol = constraintLine[5] #atmPlusHalfSignedRiskReversal
        indexLineOfFittingParam = constraintLine[6]
        vol += instrumentsToFit[indexLineOfFittingParam][6]  #add bf
        strikeColumnIndexInTheSmile = constraintLine[3]
        deltaConstraint = constraintLine[4]
        calibrationPoint[1][ strikeColumnIndexInTheSmile] = computeStrikeFromDelta(callPutIndicator * abs(deltaConstraint), vol * commonInputs.sqrtYfExpiryAsOf,
                commonInputs.forwardStrike, commonInputs.deltaConventionAdjustment, callPutIndicator, commonInputs.premiumAdjustmentIndicator)

        calibrationPoint[2][strikeColumnIndexInTheSmile] = vol


def computeInterpolationHelperParams(currentPoint, interpMethod):
    if interpMethod == "cubicSpline":
		computeSecondDerivativeHelper(matrixLine(currentPoint, 6), matrixLine(currentPoint, 0), matrixLine(currentPoint, 2), 0, 0, matrixLine(currentPoint, 5))


def computeSecondDerivativeHelper(helper, points, values, lowerConstraint, upperConstraint, secondDerivative):
    secondDerivative[0] = lowerConstraint
    if length(values) < 3:
        for i =1;i < length(values);i ++:
            secondDerivative[i] = lowerConstraint
        if(length(secondDerivative) >= 2:
            secondDerivative[length(values) - 1] = upperConstraint
        return secondDerivative
# tri - diagonal system with dominant diagonal solving
    helper[0] = lowerConstraint
    p0 = points[0]
    p1 = points[1]
    v0 = values[0]
    v1 = values[1]
    for i = 1;i < length(values) - 1;i ++:
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
    secondDerivative[length(values) - 1] = upperConstraint
    for  k = length(values) - 2; k >= 1; k--:
        secondDerivative[k] = secondDerivative[k] * secondDerivative[k+1] + helper[k]
    return secondDerivative

def computeStrategiesSolverFunction(currentPoint, commonInputs, instrumentsToFit, fx):
    nextXi = 0
    for i = nbStrikesByExpiry; i <  height(instrumentsToFit) ;++i:
        instrumentLine = matrixLine(instrumentsToFit, i)
        callPutIndicator = instrumentLine[1] # also used to know if it is a repricing instrument
        if callPutIndicator != 0:
            fx[nextXi++] = priceOneCalibrationInstrument(currentPoint, commonInputs, instrumentLine) - instrumentLine[5]
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
    commonInput.volValues = matrixLine(calibrationPoint, 2)
    commonInput.smileAxis = matrixLine(calibrationPoint, 0)
    commonInput.secondDerivatives = matrixLine(calibrationPoint, 5)
    commonInput.forwardStrike = forwardStrike
    commonInput.sqrtVolYearFraction = sqrtVolYearFraction
    return commonInput

class CommonFxSmileInputs:
    def __init__(self):
        self.smileAxis = array(0,0)
        self.volValues = array(0,0)
        self.secondDerivatives =  array(0,0)
        self.sqrtVolYearFraction = 0
        self.forwardStrike = 1
        self.userTargetPoint = 0
        self.volInterpolationMethod  = "linear"
        self.volExtrapolBefore = "flat"
        self.volExtrapolAfter = "flat"
        self.smileConventionInput = "strike"
        self.deltaConvAdjInput = 1.0
        self.leeFactor = 1.0
        self.isPremiumInput = 0

def getVolatilityFromSmile(smilePoint, commonInput, volInterpolationMethod, indexBefore):
    volValues = commonInput.volValues
    curveLength = length(volValues)
    if curveLength == 1:
        return volValues[0]

    indexBefore = getVolIndexBefore(indexBefore, curveLength)
    smileAxis = commonInput.smileAxis

    if smileAxis[indexBefore] == smilePoint:
        return volValues[indexBefore]

    if smileAxis[indexBefore + 1] == smilePoint:
        return volValues[indexBefore + 1]

    if volInterpolationMethod == "cubicSpline":
        secondDerivatives = commonInput.secondDerivatives
        return cubicSplineInterpolation(smilePoint, smileAxis[indexBefore], smileAxis[indexBefore + 1], volValues[indexBefore], volValues[indexBefore + 1], secondDerivatives[indexBefore], secondDerivatives[indexBefore + 1])

    if volInterpolationMethod == "lee":
        return leeExtrapolation(smileAxis, indexBefore, smilePoint, volValues, commonInput)

    return getInterpolatedValue(volInterpolationMethod, smilePoint, smileAxis[indexBefore], smileAxis[indexBefore+1], volValues[indexBefore], volValues[indexBefore+1])

def cubicSplineInterpolation(x, x1, x2, y1, y2, y1Second, y2Second):
    if x1 == x2:
        return y1
    xDiff = x2 - x1
    a = (x2 - x)/ xDiff
    b = 1 - a
    xSquare = xDiff * xDiff / 6
    return a * y1 + b * y2 + xSquare * ((pow(a, 3) - a) *  y1Second + (pow(b, 3) - b) * y2Second)

def leeExtrapolation(smileAxis, indexBefore, smilePoint, volValues, commonInput):
    startIndex = indexBefore
    endIndex = indexBefore + 1
    if startIndex == 0:
        endIndex = 0
        startIndex = 1

    forwardStrike = commonInput.forwardStrike
    smileConventionInput = commonInput.smileConventionInput
    deltaConvAdjInput = commonInput.deltaConvAdjInput
    isPremiumInput = commonInput.isPremiumInput
    sqrtVolYearFraction = commonInput.sqrtVolYearFraction

    pillarEnd = convertPillarLeeExtrapolation(smileAxis[endIndex], deltaConvAdjInput, smileConventionInput, forwardStrike, isPremiumInput, sqrtVolYearFraction)
    pillarStart = convertPillarLeeExtrapolation(smileAxis[startIndex], deltaConvAdjInput, smileConventionInput, forwardStrike, isPremiumInput, sqrtVolYearFraction)
    pillar = convertPillarLeeExtrapolation(smilePoint, deltaConvAdjInput, smileConventionInput, forwardStrike, isPremiumInput, sqrtVolYearFraction)
    volEnd = volValues[endIndex]

    slope = (volValues[startIndex] - volEnd) / (pillarStart - pillarEnd)
    return slope * commonInput.leeFactor * (pillar - pillarEnd) + volEnd

def convertPillarLeeExtrapolation(pillar, deltaAdj, smileConvention, forwardStrike, isPremium, sqrtVolYearFraction):
    if smileConvention == "strike":
        return math.sqrt(abs(getLogMoneynessFromStrike(forwardStrike, pillar)))
    if smileConvention == "logMoneyness":
        return math.sqrt(abs(pillar))
    if smileConvention == "deltaCall" or smileConvention == "deltaPut":
        return getLeeVolatilityForDelta(pillar, sqrtVolYearFraction, deltaAdj, getDeltaCallOrPutIndicator(smileConvention), isPremium)

def getLeeVolatilityForDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
	if premiumAdjustmentIndicator == 1:
		return math.sqrt(abs(computeLeeLogMoneynessFromAdjustedDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator)))

	deltaAdjusted = delta / deltaConventionFactor
	return abs(inverseNormalCDF(abs(deltaAdjusted))) * getArbitrageFactor(deltaAdjusted, callPutIndicator)

def computeLeeLogMoneynessFromAdjustedDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator):
	option = OptionDesc(callPutIndicator, bsStdDev, delta)
	delta = callPutIndicator * abs(delta) / deltaConventionFactor
	return newtonSolver1D(delta, 0, 1e-8, 10, getPremiumAdjustedDeltaKernelLee, option, "unused", "unused")

def getPremiumAdjustedDeltaKernelLee(x, optionDefinition, optional1, optional2):
	bsDMinus = 0
	if x!=0:
		bsDMinus = (-x - abs(x)*0.5)/math.sqrt(abs(x))
	return optionDefinition.callPutIndicator * math.exp(x) * normalCDF(optionDefinition.callPutIndicator * bsDMinus)

def getArbitrageFactor(pillar, callPutIndicator):
	if pillar <= callPutIndicator * 0.5:
		return 2
	return 2 / 3

def getInterpolatedValue(interpolationMethod, point, pointBefore, pointAfter, valueBefore, valueAfter):
    if interpolationMethod == "linear":
        return linearInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)
    if interpolationMethod == "flat":
            return flatInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)
    if interpolationMethod == "flatRight":
        return flatRightInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)
    if interpolationMethod == "flatLeft":
            return flatLeftInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)

def linearInterpolation(x, x1, x2, y1, y2):
    if x1 == x2:
        return y1
    return ((x - x1) * y2 + (x2 - x) * y1) / (x2 - x1)

def flatInterpolation(x, x1, x2, y1, y2):
    if x <= x1:
        return y1
    if x < x2:
        return (y1 + y2) / 2
    return y2

def flatRightInterpolation(x, x1, x2, y1, y2):
    if x <= x1:
        return y1
    return y2

def flatLeftInterpolation(x, x1, x2, y1, y2):
    if x < x2:
        return y1
    return y2

def computeStrategiesSolverJacobianFunction(problemDimension, currentPoint, commonInputs, instrumentsToFit, fx, jacobian):
    for j = 0; j < problemDimension; j++:
        currentValue = instrumentsToFit[j + nbStrikesByExpiry][6]
        dx = getDerivativeEpsilon()
        if currentValue != 0.0:
            dx *= abs(currentValue)
        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + j, dx, commonInputs, instrumentsToFit)
        computeInterpSpaceParam(commonInputs, currentPoint)
        computeInterpolationHelperParams(currentPoint, commonInputs.interpMethod)
        for i = 0; i < problemDimension; ++i:
            instrumentLineToFit = matrixLine(instrumentsToFit, nbStrikesByExpiry + i)
            diffPrice = priceOneCalibrationInstrument(currentPoint, commonInputs, instrumentLineToFit) - instrumentLineToFit[5]
            jacobian[i][j] = (diffPrice - fx[i]) / dx

        updateSolvingPointOneCoordinate(currentPoint, nbStrikesByExpiry + j, -dx, commonInputs, instrumentsToFit)

def luDecompostionByCroutAlgorithm(systemDimension, inAoutLu, TINY):

    #scalingArray stores the implicit scaling of each row.
    #Loop over rows to get the implicit scaling information.
    for i=0; i<systemDimension; i++:
        big = 0
        for j=0; j <systemDimension; j++:
            temp = abs(inAoutLu[i][j])
            if temp > big:
                big = temp

        if big == 0.0:
            error("Singular matrix in LUDecompostionByCroutAlgorithm")
        #No nonzero largest element.
        inAoutLu[systemDimension+1][i]=1.0/big #Save the scaling.

    # This is the outermost kij loop.
    imax = 0
    for k=0; k<systemDimension; k++:
        big = 0 # Initialize for the search for largest pivot element.
        for i = k; i<systemDimension; i++:
            temp=  inAoutLu[systemDimension+1][i]*abs(inAoutLu[i][k])
            if (temp > big):# Is the figure of merit for the pivot better than
                big = temp #the best
                imax=i


        if k != imax:
            for j=0; j<systemDimension; j++:
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
        for i=k+1;i<systemDimension;i++:
            temp=inAoutLu[i][k] /= inAoutLu[k][k] #Divide by the pivot element.
            for j=k+1;j<systemDimension;j++: #Innermost loop: reduce remaining submatrix.
                inAoutLu[i][j] -= temp*inAoutLu[k][j]



def solveLinearSystemFromCroutLUDecomposition(systemDimension, lu, secondMemberAndResult):
    ii = 0
    for i=0;i<systemDimension;i++:
        #When ii is set to a positive value, it will become the
        #index of the first nonvanishing element of b. We now do the forward substitution. The
        #only new wrinkle is to unscramble the permutationas we go.
        ip = lu[systemDimension][i]
        sum = secondMemberAndResult[ip]
        secondMemberAndResult[ip] = secondMemberAndResult[i]
        if ii != 0:
            for j=ii-1; j<i ;j++:
                sum -= lu[i][j] * secondMemberAndResult[j]
        if sum != 0.0: #A nonzero element was encountered, so from now on we
            ii = i+1 #will have to do the sums in the loop above.

        secondMemberAndResult[i]=sum

    for i=systemDimension-1;i>=0;i--: #Now we do the backsubstitution,
        sum=secondMemberAndResult[i]
        for j=i+1; j<systemDimension; j++:
            sum -= lu[i][j] * secondMemberAndResult[j]
        secondMemberAndResult[i] =sum / lu[i][i] #Store a component of the solution vector X.

def getL1Norm(x):
    maxVal = 0
    for i = 0; i < length(x); ++i:
        maxVal = max(maxVal, abs(x[i]))
    return maxVal



