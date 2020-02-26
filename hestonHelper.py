import math

import numpy as np
from quantools.library.fxvolCalibration.fxVolGood import getDeltaConventionAdjustment, computeStrikeFromDelta, \
	pointFloorIndex, getVolIndexBefore, getInterpolatedValue

from quantools.analyticsTools.analyticsTools import yearFraction


def calibrateHestonModel(surface, solver, weightType, upperBounds, lowerBounds, nbParameters) :
	surfaceTenors = metaData("FX_VOLATILITY", [surface], "expiries")
	tenorsAsDays = getVolatilitySurfaceExpiryAxis(surface, "FX_VOLATILITY")
	smileLength = len(axis("FX_VOLATILITY", [surface, surfaceTenors[0]], 0))
	volatilityBasis = metaData("FX_VOLATILITY", [surface], "volatilityBasis")
	nbExpiries = len(tenorsAsDays)
	smileAxisType = metaData("FX_VOLATILITY", [surface], "smileAxis")
	callOrPut = -1 if smileAxisType== "deltaPut" else 1
	spotDate = getSpotDate(metaData(surfaceType, [surfaceName], "foreignCurrency"), metaData(surfaceType, [surfaceName], "domesticCurrency"))
	foreignCurve = metaData("FX_VOLATILITY", [surface], "foreignCurve")
	domesticCurve = metaData("FX_VOLATILITY", [surface], "domesticCurve")
	spotRate = getFxRate(metaData(surfaceType, [surfaceName], "foreignCurrency"), metaData(surfaceType, [surfaceName], "domesticCurrency"), date)
	deliveriesAsDays = getVolatilitySurfaceDeliveries(surface, "FX_VOLATILITY")
	isPremiumAdjusted = boolToInt(metaData("FX_VOLATILITY", [surface], "premiumAdjusted"))
	calcDate = dateToDays(calculationDate())

	size = nbExpiries * smileLength
	mktStrikes = np.zeros((1,size))
	mktVols = np.zeros((1,size))
	forwards = np.zeros(1,nbExpiries)
	expiries = np.zeros((1,nbExpiries))
	dfs = np.zeros((1,nbExpiries))
	weights = np.ones((size,1))* math.sqrt(1.0 / size)

	for i in range(nbExpiries):
		yfExpiry = yearFraction(calculationDate(), daysToDate(tenorsAsDays[i]), volatilityBasis)
		expiries[i] = yfExpiry
		refTenor = surfaceTenors[i]
		deliveryAsDays = deliveriesAsDays[i]
		smileAxis = getVolatilitySmileAxis(surface, "FX_VOLATILITY", refTenor)
		volValues = getVolatilitySmileValues(surface, "FX_VOLATILITY", refTenor)
		dfFor = discountFactorFromDays(foreignCurve, spotDate, deliveryAsDays)
		dfDom = discountFactorFromDays(domesticCurve, spotDate, deliveryAsDays)
		dfDomPv = computeDiscountFactor(domesticCurve, calcDate, deliveryAsDays)
		forward = spotRate * dfFor / dfDom
		dfs[i] = dfDomPv
		forwards[i] = forward
		deltaConvFactor = getDeltaConventionAdjustment(metaData("FX_VOLATILITY", [surface, refTenor], "smileConvention"), dfFor)
		sqrtYf = math.sqrt(yfExpiry)

		for j in range(smileLength):
			vol = volValues[j]
			strike = getStrikeFromSmileAxis(smileAxisType, forward, smileAxis[j], vol * sqrtYf, deltaConvFactor, isPremiumAdjusted, callOrPut)
			index = i * smileLength + j
			mktStrikes[index] = strike
			mktVols[index] = vol
			if (weightType == "vega"):
				weights[index] = 1 / math.sqrt(getNormedBlackVega(vol * sqrtYf, strike / forward, sqrtYf) * dfDomPv * forward)


	# initialVolATM is the first available by default.
	initialVolATM = 0
	if (isDefined(shortVolDays)) :
		initialVolATM = getATMVolatility(addDays(calculationDate(), shortVolDays), surface, "FX_VOLATILITY")
    else:
		initialVolATM = mktVols[floor(smileLength / 2)]


	v0 = initialVolATM * initialVolATM

	initialPoints = getPreviousHestonParams(surface)
	calibHelper = CalibrationHelper(expiries, forwards, dfs, mktStrikes, mktVols, weights, v0, getKappaValue(initialPoints))
	return getHestonParameters(calibHelper, solver, upperBounds, lowerBounds, v0, size, nbParameters, initialPoints)

def getStrikeFromSmileAxis(smileAxisType, forward, quote, volStdDev, deltaConventionFactor, premiumAdjusted, callOrPut) :
	if smileAxisType == "deltaCall" or smileAxisType == "deltaPut":
		return computeStrikeFromDelta(quote, volStdDev, forward, deltaConventionFactor, callOrPut, premiumAdjusted)
	if (smileAxisType == "logMoneyness"):
		return forward * math.exp(quote)
	return quote

def getNormedBlackVega(bsStdDev, moneyness, sqrtYf):
	d1 = (math.log(1 / moneyness) + 0.5 * bsStdDev * bsStdDev) / bsStdDev
	return 1/math.sqrt(2*np.pi)  * math.exp(-0.5 * d1 * d1)() * sqrtYf

def getATMVolatility(expiry, curveName, curveType) :
    values = data1D(curveType, [curveName, "ATM_VOLATILITY"], calculationDate())
    atmCurveSize = length(values)
    if (atmCurveSize == 1) :
        return values[0]

    expiries = axis(curveType, [curveName, "ATM_VOLATILITY"], 0)
    t_t0 = dateToDays(expiry)
    tenorFloorIndex = pointFloorIndex(expiries, t_t0)
    pointBeforeIndex = getVolIndexBefore(tenorFloorIndex, atmCurveSize)
    ti_t0 = expiries[pointBeforeIndex]
    atmVoli = values[pointBeforeIndex]
    precision = pow(10,-9)
    if (abs(t_t0 - ti_t0) < precision):
        return atmVoli
    ti1_t0 = expiries[pointBeforeIndex + 1]
    atmVoli1 = values[pointBeforeIndex + 1]

    if (abs(t_t0 - ti1_t0) < precision)
        return atmVoli1

    return getExpiryVolatility(tenorFloorIndex, ti_t0, ti1_t0, atmVoli, atmVoli1, t_t0, curveName, curveType)

def getExpiryVolatility(expiryFloorIndex, tBeforeAsDays, tAfterAsDays, volBefore, volAfter, tAsDays, surfaceName, surfaceType):
	interpVariable = getInterpolationVariableOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())

	interpolationMethod = getInterpolationMethodOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())

	if (expiryFloorIndex == -1 and interpVariable == "timeWeightedTotalVariance" and interpolationMethod == "linear") :
		tAfterAsDays = tBeforeAsDays
		volAfter = volBefore
		tBeforeAsDays = dateToDays(calculationDate())

	precision = pow(10, -9)
	if (abs(tAsDays - tBeforeAsDays) < precision):
		return volBefore
	if (abs(tAsDays - tAfterAsDays) < precision):
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

def transformImpliedVolToInterpVariable(vol, relativeDate, dataTypeToInterpolate) :
	if (dataTypeToInterpolate == "variance"):
		return vol * vol
	if (dataTypeToInterpolate == "volatility"):
			return vol

	return vol * vol * relativeDate

def transformInterpVariableToImpliedVol(variable, relativeDate, dataTypeToInterpolate):
	if (dataTypeToInterpolate == "variance"):
		return math.sqrt(variable)
	if(dataTypeToInterpolate=="volatility"):
		return variable

	return math.sqrt(variable / relativeDate)

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

def getHestonParameters(calibHelper, solver, upperBounds, lowerBounds, v0, size, nbParameters, initialPoints):
	initPoints = array(nbParameters)
	if (solver == "DELV"):
		initPoints = CHDEminimisationBestSolution(getPopulationSize(), 35 * calibKappa + (1-calibKappa) * 20, 0.6 * calibKappa + (1-calibKappa) * 0.4, 0.75, nbParameters, upperBounds, lowerBounds, costFunction, verifyConstraints, calibHelper)
	else:
		copyInitialPoints(initPoints, initialPoints, nbParameters)
	return getResultsWithV0(LevenbergMarquardt(costFunctionLV, initPoints, calibHelper, nbParameters, size, lowerBounds, upperBounds), v0, nbParameters, calibHelper.kappa)

class CalibrationHelper:
	expiries = np.zeros((1,2)) # array of expiries
	forwards = np.zeros((1,2)) # array of fwd value at expiry dates
	dfs = np.zeros((1,2)) # array of dfs
	strikes = np.zeros((1,2)) # option strikes
	mktVols = np.zeros((1,2)) # implied vols
	weights = np.zeros((1,2)) # calibration weights
	v0 = 1.0  # V0 parameter
	kappa = 0.0 #equals to 0 when the kappa needs to be calibrated otherwise the value of kappa coming from dataManager is stored

def getPreviousHestonParams(surface):
	if(calibKappa == 1 and solver == "DELV"):
		return np.zeros((1,1))
	return data1D("HESTON_PARAMETERS", [surface], calculationDate())


def CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput):
	
	
	uG1 =	array(d)
	
	# Creation of a	random	initial	population
	
	
	xG = initializePopulation(upper, lower, np, d)
	
	# Compute the 	values 	of 	the 	objective 	function 	for the generation g
	
	
	fG =evaluateFunction(xG, objectiveFunction, otherInput, np)
	
	for g in range(maxGen):
	
		for i in range(np):
		# select		randomly		r1, r2 and r3
			r1 = intRand(0, np)
			r2 = intRand(0, np)
			r3 = intRand(0, np)
			
			while (r1 == i):
				r1 = intRand(0, np)

			while (r2 == i | | r2 == r1) :
				r2 = intRand(0, np)

			while (r3 == i | | r3 == r1 | | r3 == r2) :
				r3 = intRand(0, np)

			def jrand =	intRand(0, d)
	
			for j in range(d):
				child =0.0
				if (floatRand() < cr | | j == jrand):
					child = xG[r3][j] + F * (xG[r1][j] - xG[r2][j])
				else:
					child = xG[i][j]
	
				uG1[j] = rangeKeeperByReflection(child, lower[j], upper[j])

	
		#compute the	value	of	the	objective	function	for i
		fU_i =	objectiveFunction(uG1, otherInput)
		if (compareSolutionsTDSC(fG[i], fU_i, verifyConstraint, matrixLine(xG, i), uG1) == 1):
			replaceMatrixLine_V(xG, uG1, i)
			fG[i] = fU_i

	return bestSolution(xG, bestPosition(xG, objectiveFunction, otherInput, np), d)
	
def compareSolutionsTDSC(fitnessValue1, fitnessValue2, verifyConstraint, individual1, individual2 ):
	feasible1 = verifyConstraint(individual1)
	feasible2 = verifyConstraint(individual2)

	#case 1 : the two solutions are feasible
	if(feasible1 == 0 and feasible2 == 0 and fitnessValue2 < fitnessValue1):
		return 1    # solution 2 is better than solution 1
	
	#case 2 : if one solution is feasible and the other is unfeasible, the feasible solution wins
	if(feasible2 == 0 and feasible1 > 0):
		return 1  # solution 2 is better than solution 1

	#case 3 : if both solutions are infeasible, the one with the lowest of sum of constraints is prefered
	if(feasible1 > 0 and feasible2 > 0 and feasible2 <= feasible1 ):
		return 1  # solution 2 is better than solution 1

	return 0 # solution 1 is better than solution for all the other cases

def bestSolution(population, position, d):
	solution = np.array((1,d))
	for i in range(population.shpae[1]):
		solution[i] = population[position][i]
	return solution

def getResultsWithV0(calibrationOutput, v0, size, kappa):
	results = np.array((1,5))
	results[0] = v0
	for i in range(size):
		results[i + 1] = calibrationOutput[i]

	if (size == 3):
		results[4] = kappa
	return results
