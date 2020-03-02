#calibrateHestonModel(volatilityName, solver, weightType, upperBounds, lowerBounds, 4)
import math
import numpy as np

from quantools.analyticsTools.analyticsTools import yearFraction
from quantools.library.fxvolCalibration.fxVol import computeStrikeFromDelta, getVolIndexBefore
from quantools.library.utilities.interpolation import getInterpolatedValue
from quantools.library.utilities.utilitiesAccessor import pointFloorIndex


def calibrateHestonModel(surface, solver, weightType, upperBounds, lowerBounds, nbParameters):
	surfaceTenors = metaData("FX_VOLATILITY", [surface], "expiries")
	tenorsAsDays = getVolatilitySurfaceExpiryAxis(surface, "FX_VOLATILITY")
	smileLength = len(axis("FX_VOLATILITY", [surface, surfaceTenors[0]], 0))
	volatilityBasis = metaData("FX_VOLATILITY", [surface], "volatilityBasis")
	nbExpiries = len(tenorsAsDays)
	smileAxisType = metaData("FX_VOLATILITY", [surface], "smileAxis")
	callOrPut = -1 if smileAxisType=="deltaPut" else 1
	spotDate = getSpotDate(metaData("FX_VOLATILITY", [surfaceName], "foreignCurrency"), metaData("FX_VOLATILITY", [surfaceName], "domesticCurrency"))
	foreignCurve = metaData("FX_VOLATILITY", [surface], "foreignCurve")
	domesticCurve = metaData("FX_VOLATILITY", [surface], "domesticCurve")
	spotRate =getFxRate(metaData("FX_VOLATILITY", [surfaceName], "foreignCurrency"), metaData("FX_VOLATILITY", [surfaceName], "domesticCurrency"), date)
	deliveriesAsDays = getVolatilitySurfaceDeliveries(surface, "FX_VOLATILITY")
	isPremiumAdjusted = metaData("FX_VOLATILITY", [surface], "premiumAdjusted")
	calcDate = dateToDays(calculationDate())

	size = nbExpiries * smileLength
	mktStrikes = np.zeros((size,1))
	mktVols = np.zeros((size,1))
	forwards = np.zeros((nbExpiries,1))
	expiries = np.zeros((nbExpiries,1))
	dfs = np.zeros((nbExpiries,1))
	weights = np.ones((size,1))* math.sqrt(1.0 / size)

	for i in range(nbExpiries):
		yfExpiry = yearFraction(calculationDate(), daysToDate(tenorsAsDays[i]), volatilityBasis)
		expiries[i] = yfExpiry
		refTenor = surfaceTenors[i]
		deliveryAsDays = deliveriesAsDays[i]
		smileAxis = getVolatilitySmileAxis(surface, "FX_VOLATILITY", refTenor)
		volValues = getVolatilitySmileValues(surface, "FX_VOLATILITY", refTenor)
		dfFor = 0.96#discountFactorFromDays( ycValuesFor, ycDefFor, refDate,startDate, endDate) #discountFactorFromDays(foreignCurve, spotDate, deliveryAsDays)
		dfDom = 0.78#discountFactorFromDays(domesticCurve, spotDate, deliveryAsDays)
		dfDomPv = computeDiscountFactor( ycValuesFor, ycDefFor, refDate,deliveryAsDays) #computeDiscountFactor(domesticCurve, calcDate, deliveryAsDays)
		forward = spotRate * dfFor / dfDom
		dfs[i] = dfDomPv
		forwards[i] = forward
		deltaConvFactor = getDeltaConventionAdjustment(metaData("FX_VOLATILITY", [surface, refTenor], "smileConvention"), dfFor)
		sqrtYf = sqrt(yfExpiry)

		for j in range(smileLength):
			vol = volValues[j]
			strike = getStrikeFromSmileAxis(smileAxisType, forward, smileAxis[j], vol * sqrtYf, deltaConvFactor, isPremiumAdjusted, callOrPut)
			index = i * smileLength + j
			mktStrikes[index] = strike
			mktVols[index] = vol
			if (weightType == "vega"):
				weights[index] = 1 / math.sqrt(getNormedBlackVega(vol * sqrtYf, strike / forward, sqrtYf) * dfDomPv * forward)
		
	#initialVolATM is the first available by default.
    initialVolATM = 0
	if(isDefined(shortVolDays)):
        initialVolATM = getATMVolatility(addDays(calculationDate(), shortVolDays), surface, "FX_VOLATILITY")
    else:
        initialVolATM = mktVols[floor(smileLength / 2)]
	

	v0 = initialVolATM * initialVolATM

	initialPoints = getPreviousHestonParams(surface)
	calibHelper = CalibrationHelper(expiries, forwards, dfs, mktStrikes, mktVols, weights, v0, getKappaValue(initialPoints))
	return getHestonParameters(calibHelper, solver, upperBounds, lowerBounds, v0, size, nbParameters, initialPoints)



def getVolatilitySurfaceExpiryAxis(surfaceName, surfaceType):
	return axis(surfaceType, [surfaceName], 0)

def getSpotDate(currency1, currency2):
	return axis("FX_RATE", [currency1, currency2], 0)[0]

def getFxRate(currency1, currency2, date):
	if(currency1 == currency2):
		return 1
	return data1D("FX_RATE", [currency1, currency2], date)[0]
def getVolatilitySurfaceDeliveries(surfaceName, surfaceType):
	return data1D(surfaceType, [surfaceName], calculationDate())

def getVolatilitySmileAxis(surfaceName, surfaceType, expiry):
    # 1 represents the "y" axis
    # After market data preprocess, the smile axis is stored in the Y axis
    if (metaData(surfaceType, [surfaceName, expiry], "preprocessed")):
        return axis(surfaceType, [surfaceName, expiry], 1)
    return axis(surfaceType, [surfaceName, expiry], 0)

def getVolatilitySmileValues(surfaceName, surfaceType, expiry):
    # After preprocess the data1D is transformed into a matrix
    # First line of the matrix contains the volatilities
    # Second line of the matrix contains the computed strikes
    if (metaData(surfaceType, [surfaceName, expiry], "preprocessed")):
        return matrixLine(data2D(surfaceType, [surfaceName, expiry], calculationDate()), 0)
    return data1D(surfaceType, [surfaceName, expiry], calculationDate())

def getDeltaConventionAdjustment(smileConvention, df):
	if (smileConvention == "spot"):
		return df
	return 1

def getStrikeFromSmileAxis(smileAxisType, forward, quote, volStdDev, deltaConventionFactor, premiumAdjusted, callOrPut):
	if (smileAxisType == "deltaCall" or smileAxisType == "deltaPut"):
		return computeStrikeFromDelta(quote, volStdDev, forward, deltaConventionFactor, callOrPut, premiumAdjusted)
	if (smileAxisType == "logMoneyness"):
		return forward * math.exp(quote)
	return quote

def getNormedBlackVega(bsStdDev, moneyness, sqrtYf):
	d1 = (math.log(1 / moneyness) + 0.5 * bsStdDev * bsStdDev) / bsStdDev
	return 1/(math.sqrt(2*math.pi))*math.exp(-0.5*d1*d1) * sqrtYf

def getATMVolatility(expiry, curveName, curveType):
    values = data1D(curveType, [curveName, "ATM_VOLATILITY"], calculationDate())
    atmCurveSize = len(values)
    if(atmCurveSize == 1):
        return values[0]
    
    expiries = axis(curveType, [curveName, "ATM_VOLATILITY"], 0)
    t_t0 = dateToDays(expiry)
    tenorFloorIndex = pointFloorIndex(expiries, t_t0)
    pointBeforeIndex = getVolIndexBefore(tenorFloorIndex, atmCurveSize)
    ti_t0 = expiries[pointBeforeIndex]
    atmVoli = values[pointBeforeIndex]

    if (abs(t_t0 - ti_t0) < getTimePrecision()):
        return atmVoli
    ti1_t0 = expiries[pointBeforeIndex + 1]
    atmVoli1 = values[pointBeforeIndex + 1]

    if (abs(t_t0 - ti1_t0) < getTimePrecision()):
        return atmVoli1

    return getExpiryVolatility(tenorFloorIndex, ti_t0, ti1_t0, atmVoli, atmVoli1, t_t0, curveName, curveType)

def getTimePrecision():
	return 1e-10

def getExpiryVolatility(expiryFloorIndex, tBeforeAsDays, tAfterAsDays, volBefore, volAfter, tAsDays, surfaceName, surfaceType):
	interpVariable = getInterpolationVariableOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())
	interpolationMethod = getInterpolationMethodOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())

	if (expiryFloorIndex == -1 and interpVariable == "timeWeightedTotalVariance" and interpolationMethod == "linear"):
		tAfterAsDays = tBeforeAsDays
		volAfter = volBefore
		tBeforeAsDays = dateToDays(calculationDate())


	if (abs(tAsDays - tBeforeAsDays) < getTimePrecision()):
		return volBefore
	if (abs(tAsDays - tAfterAsDays) < getTimePrecision()):
		return volAfter
	nbDaysCalcDate = dateToDays(calculationDate())
	tAsDays -= nbDaysCalcDate
	if (tAsDays == 0):
		return volBefore
	tBeforeAsDays -= nbDaysCalcDate
	volBefore = transformImpliedVolToInterpVariable(volBefore, tBeforeAsDays, interpVariable)

	tAfterAsDays -= nbDaysCalcDate
	volAfter = transformImpliedVolToInterpVariable(volAfter, tAfterAsDays, interpVariable)

	if (interpVariable != "timeWeightedTotalVariance"):
		volBefore = getInterpolatedValue(interpolationMethod, tAsDays, tBeforeAsDays, tAfterAsDays, volBefore, volAfter)
	else:
		volBefore = computeWeightedInterpolation(tBeforeAsDays, volBefore, tAfterAsDays, volAfter, tAsDays, nbDaysCalcDate, surfaceName, surfaceType)

	return transformInterpVariableToImpliedVol(volBefore, tAsDays, interpVariable)

def getInterpolationVariableOnAxis(floorIndex, surfaceParameters, surfaceType, axisMetaData):
	if (floorIndex == -1):
		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationVariableBeforeFirstPoint())
	if (floorIndex == -2):
		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationVariableAfterLastPoint())
	return metaData(surfaceType, surfaceParameters, axisMetaData.getInterpolationVariable())

def getInterpolationMethodOnAxis(floorIndex, surfaceParameters, surfaceType, axisMetaData):
	if (floorIndex == -1):
		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationMethodBeforeFirstPoint())
	if (floorIndex == -2):
		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationMethodAfterLastPoint())
	return metaData(surfaceType, surfaceParameters, axisMetaData.getInterpolationMethod())


def transformImpliedVolToInterpVariable(vol, relativeDate, dataTypeToInterpolate):
	if dataTypeToInterpolate == "variance":
		return vol * vol
	if dataTypeToInterpolate == "volatility":
		return vol
	return vol * vol * relativeDate

def transformInterpVariableToImpliedVol(variable, relativeDate, dataTypeToInterpolate):
	if dataTypeToInterpolate == "variance":
		return math.sqrt(variable)
	if dataTypeToInterpolate == "volatility":
		return variable
	return math.sqrt(variable / relativeDate)

def computeWeightedInterpolation(tBeforeAsDays, volBefore, tAfterAsDays, volAfter, tAsDays, nbDaysCalcDate, surfaceName, surfaceType):
	omega1 = getVolTimeAdjWeight(tBeforeAsDays + nbDaysCalcDate, tAsDays + nbDaysCalcDate, surfaceName, surfaceType)

	omega = getVolTimeAdjWeight(tBeforeAsDays + nbDaysCalcDate, tAfterAsDays + nbDaysCalcDate, surfaceName, surfaceType)

	omega = omega1 / omega
	return (omega * volAfter + (1 - omega) * volBefore)

def getVolTimeAdjWeight(ts, te, surfaceName, surfaceType):
    sign = 1
    if(ts > te):
		t = ts
		ts = te
		te = t
		sign = -1

    volTimeWeight = getWeightFromPeriodPattern(ts, te, metaData(surfaceType, [surfaceName], "periodicTimesVolTimeAdj"), metaData(surfaceType, [surfaceName], "periodicCumulativeTimeWeights"))
    volTimeWeight += getWeightFromEventsRange(ts, te,  metaData(surfaceType, [surfaceName], "holidaysStartEndAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "holidaysCumulativeTimeWeights"))
    volTimeWeight += getWeightFromEventsRange(ts, te,  metaData(surfaceType, [surfaceName], "eventsStartEndAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "eventsCumulativeTimeWeights"))
    volTimeWeight += getWeightFromEventsDates(ts, te,  metaData(surfaceType, [surfaceName], "eventsDateAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "eventsCumulativeDateWeights"))
    return sign * volTimeWeight

def getWeightFromPeriodPattern(ts, te, times, cumulTimeWeights):
	return getWeightFromCumulativeTimeWeights(getWeightFromPeriodCumulTimeWeightPatternHelper, ts, te, times, cumulTimeWeights, te - ts)

def getWeightFromCumulativeTimeWeights(weightFunctor, ts, te, times, cumulTimeWeights, defaultVal):
	if(!isDefined(times) or !isDefined(cumulTimeWeights) or abs(ts - te) <  getTimePrecision()):
		return defaultVal
	return weightFunctor(ts, te, times, cumulTimeWeights)

def getWeightFromPeriodCumulTimeWeightPatternHelper(ts, te, times, cumulTimeWeights):
    if(len(times) <=1):
        return  te - ts
    # 3 is sunday from epoch 01 jan 1970
	nbTimes = len(times)-1
    dperiodLength = times[nbTimes] # times[0] = 0  REQUIRED
    nbPeriods = floor ((te - ts) / periodLength)
    return nbPeriods * cumulTimeWeights[nbTimes] + getWeightFromRangeLessThanAPeriod(ts + nbPeriods * periodLength, te, periodLength, times, cumulTimeWeights, getWeightFromCumulTimeWeightWithStartAndEndInRange)

def getWeightFromEventsRange(ts, te, times, cumulTimeWeights):
	return getWeightFromCumulativeTimeWeights(getWeightFromCumulTimeWeightWithStartAndEndInRange, ts, te, times, cumulTimeWeights, 0)

def getWeightFromCumulTimeWeightWithStartAndEndInRange(timeS, timeE, times, cumulTimeWeights):
    if(len(times)<=1)
        return 0
    #REQUIRED: length(times) >= 2
	nbTimes = length(times)
	timelast = times[nbTimes-1]
	timeFirst = times[0]
    timeS = max(timeS, timeFirst)
    timeE = min(timeE, timelast)
    if(timeS >= timelast || timeE <= timeFirst):
        return 0
    #We are sure that periodicTimeIndexS < length(times)-1
    periodicDayIndexE = binaryFloorIndex(times, timeE)
    if(length(times) - 1 == periodicDayIndexE):
        periodicDayIndexE -= 1
    periodicTimeIndexS = binaryFloorIndex(times, timeS)
    prevCumulWeight = cumulTimeWeights[periodicTimeIndexS+1]
    if(times[periodicTimeIndexS+1] == times[periodicTimeIndexS]):
        error("duplicate dates not allowed in volatility time adjustment  date axis patterns, you can use instead eventsDateAsDaysVolTimeAdj and eventsCumulativeDateWeights")

    weight0 = (prevCumulWeight - cumulTimeWeights[periodicTimeIndexS])/(times[periodicTimeIndexS+1] - times[periodicTimeIndexS])
    if(periodicTimeIndexS == periodicDayIndexE):
        return  weight0 * (timeE - timeS)

    # we are sure at this stage that periodicDayIndexE >= 1 because periodicDayIndexE > periodicTimeIndexS>= 0
    dtPrev = times[periodicTimeIndexS+1]
    weightTime = weight0 * (dtPrev - timeS)# first part
    nextCumulWeight = cumulTimeWeights[periodicDayIndexE]
    weightTime += (nextCumulWeight -  prevCumulWeight)
    dtPrev = times[periodicDayIndexE]
    if(abs(times[periodicDayIndexE+1] - dtPrev) <  getTimePrecision()):
        error("duplicate dates not allowed in volatility time adjustment  date axis patterns, you can use instead eventsDateAsDaysVolTimeAdj and eventsCumulativeDateWeights")

    weightTime += ((cumulTimeWeights[periodicDayIndexE+1] - nextCumulWeight)/(times[periodicDayIndexE+1] - dtPrev))*(timeE - dtPrev)#last part
    return weightTime

def getWeightFromEventsDates(ts, te, times, cumulTimeWeights):
	return  getWeightFromCumulativeTimeWeights(getWeightFromCumulTimeWeightWithDateEvents, ts, te, times, cumulTimeWeights, 0)

def getWeightFromCumulTimeWeightWithDateEvents(timeS, timeE, times, cumulTimeWeights):

	if(len(times)== 0):
		return 0

	timeFirst = times[0]
	if(len(times) == 1):
		if(timeS <= timeFirst && timeFirst<= timeE):
			return cumulTimeWeights[0]
		return 0


	#case length(times)>= 2
	if(timeS >= times[len(times)-1] or timeE <= times[0]):
		return 0
	#case timeS < times[length(times)-1] and times[0] < timeE
	#so periodicTimeIndexS <= length(times)-2 and periodicDayIndexE >= 1
	timeS = max(timeS, timeFirst) #so periodicTimeIndexS >= 0
	periodicTimeIndexS = binaryFloorIndex(times, timeS)
	if(abs (timeS - times[periodicTimeIndexS]) <  getTimePrecision())
		periodicTimeIndexS -= 1
	#timeE = min(timeE, times[length(times)-1]) //so periodicDayIndexE <= length(times)-1
	periodicDayIndexE = binaryFloorIndex(times, timeE)
	if(abs(timeE - times[periodicDayIndexE]) < getTimePrecision()):
		periodicDayIndexE -= 1 #still periodicDayIndexE >= 0
	cumulWeight1 = 0
	if(periodicTimeIndexS >= 0):
		cumulWeight1 = cumulTimeWeights[periodicTimeIndexS]
	return cumulTimeWeights[periodicDayIndexE] - cumulWeight1

def getPreviousHestonParams(surface):
	if(calibKappa == 1 && solver == "DELV"):
		return array(0)
	return data1D("HESTON_PARAMETERS", [surface], calculationDate())

class CalibrationHelper:
	expiries = array(0, 0.0) # array of expiries
	forwards = array(0, 0.0) # array of fwd value at expiry dates
	dfs = array(0, 0.0) # array of dfs
	strikes = array(0, 0.0) # option strikes
	mktVols = array(0, 0.0) # implied vols
	weights = array(0, 0.0) # calibration weights
	v0 = 1.0  # V0 parameter
	kappa = 0.0 #equals to 0 when the kappa needs to be calibrated otherwise the value of kappa coming from dataManager is stored


def getHestonParameters(calibHelper, solver, upperBounds, lowerBounds, v0, size, nbParameters, initialPoints):
	def initPoints = np.zeros((nbParameters,1))
	if (solver == "DELV"):
		initPoints = CHDEminimisationBestSolution(15, 35 * calibKappa + (1-calibKappa) * 20, 0.6 * calibKappa + (1-calibKappa) * 0.4, 0.75, nbParameters, upperBounds, lowerBounds, costFunction, verifyConstraints, calibHelper)
	else:
		copyInitialPoints(initPoints, initialPoints, nbParameters)
	return getResultsWithV0(LevenbergMarquardt(costFunctionLV, initPoints, calibHelper, nbParameters, size, lowerBounds, upperBounds), v0, nbParameters, calibHelper.kappa)





def copyInitialPoints(initPoints, initialPoints, nbParameters):
	for i in range(nbParameters):
		initPoints[i] = initialPoints[i+1]



def getResultsWithV0(calibrationOutput, v0, size, kappa):
	results = np.zeros((5,1))
	results[0] = v0
	for i in range(size):
		results[i + 1] = calibrationOutput[i]

	if (size == 3):
		results[4] = kappa
	return results




def CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput) {


def uG1 =


array(d)

// Creation
of
a
random
initial
population


def xG =


initializePopulation(upper, lower, np, d)

// Compute
the
values
of
the
objective
function
for the generation g


def fG =


evaluateFunction(xG, objectiveFunction, otherInput, np)

for (


	def g =


0;
g < maxGen;
g + +) {

for (


	def i =


0;
i < np;
i + +) {

// select
randomly
r1, r2 and r3


def r1 =


intRand(0, np)


def r2 =


intRand(0, np)


def r3 =


intRand(0, np)

while (r1 == i) {
r1 = intRand(0, np)
}
while (r2 == i | | r2 == r1) {
r2 = intRand(0, np)
}
while (r3 == i | | r3 == r1 | | r3 == r2) {
r3 = intRand(0, np)
}


def jrand =


intRand(0, d)

for (


	def j =


0;
j < d;
j + +) {


def child =


0.0
if (floatRand() < cr | | j == jrand)
	child = xG[r3][j] + F * (xG[r1][j] - xG[r2][j])
else
	child = xG[i][j]

uG1[j] = rangeKeeperByReflection(child, lower[j], upper[j])
}

// compute
the
value
of
the
objective
function
for i


	def fU_i =


objectiveFunction(uG1, otherInput)
if (compareSolutionsTDSC(fG[i], fU_i, verifyConstraint, matrixLine(xG, i), uG1) == 1) {
replaceMatrixLine_V(xG, uG1, i)
fG[i] = fU_i
}
}
}
return bestSolution(xG, bestPosition(xG, objectiveFunction, otherInput, np), d)

}