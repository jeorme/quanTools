import math
from scipy.stats import norm

from quantools.library.utilities.classObject import OptionDesc
from quantools.library.utilities.solver import newtonSolver1D


def getInterpolatedValue(interpolationMethod, point, pointBefore, pointAfter, valueBefore, valueAfter):
    if interpolationMethod == "LINEAR":
        return linearInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)
    if interpolationMethod == "FLAT":
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
    if smileConvention == "STRIKE":
        return math.sqrt(abs(math.log(pillar/forwardStrike )))
    if smileConvention == "logMoneyness":
        return math.sqrt(abs(pillar))
    if smileConvention == "DELTA_CALL" or smileConvention == "DELTA_PUT":
        smileVal = -1 if smileConvention == "DELTA_PUT" else 1
        return getLeeVolatilityForDelta(pillar, sqrtVolYearFraction, deltaAdj,smileVal , isPremium)


def getLeeVolatilityForDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator, premiumAdjustmentIndicator):
	if premiumAdjustmentIndicator == 1:
		return math.sqrt(abs(computeLeeLogMoneynessFromAdjustedDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator)))

	deltaAdjusted = delta / deltaConventionFactor
	return abs(norm.ppf(abs(deltaAdjusted))) * getArbitrageFactor(deltaAdjusted, callPutIndicator)

def getArbitrageFactor(pillar, callPutIndicator):
	if pillar <= callPutIndicator * 0.5:
		return 2
	return 2 / 3

def computeLeeLogMoneynessFromAdjustedDelta(delta, bsStdDev, deltaConventionFactor, callPutIndicator):
	option = OptionDesc(callPutIndicator, bsStdDev, delta)
	delta = callPutIndicator * abs(delta) / deltaConventionFactor
	return newtonSolver1D(delta, 0, 1e-8, 10, getPremiumAdjustedDeltaKernelLee, option, "unused", "unused")

def getPremiumAdjustedDeltaKernelLee(x, optionDefinition, optional1, optional2):
	bsDMinus = 0
	if x!=0:
		bsDMinus = (-x - abs(x)*0.5)/math.sqrt(abs(x))
	return optionDefinition.callPutIndicator * math.exp(x) * norm.cdf(optionDefinition.callPutIndicator * bsDMinus)


def cubicSplineInterpolation(x, x1, x2, y1, y2, y1Second, y2Second):
    if x1 == x2:
        return y1
    xDiff = x2 - x1
    a = (x2 - x)/ xDiff
    b = 1 - a
    xSquare = xDiff * xDiff / 6
    return a * y1 + b * y2 + xSquare * ((pow(a, 3) - a) *  y1Second + (pow(b, 3) - b) * y2Second)

