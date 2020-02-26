# import math
#
# from quantools.analyticsTools.analyticsTools import yearFraction
# from quantools.library.fxvolCalibration.fxVolGood import getIndexBefore, pointFloorIndex, cubicSplineInterpolation, \
# 	linearInterpolation, getInterpolatedValue
#
#
# def discountFactorFromDays(curve, refDate,startDate, endDate):
# 	return computeDiscountFactor(curve, refDate, endDate) / computeDiscountFactor(curve, refDate, startDate)
#
#
# def computeDiscountFactor(curve, refDate, discountDate):
# 	if (discountDate <= refDate):
# 		return 1
#
# 	return interpolateDFOnCurve(curve, discountDate, refDate)
#
#
# def interpolateDFOnCurve(curve, interpDate, refDate):
#     maturities = getYieldCurveMaturities(curve, "discountFactor", refDate)
#     switchDates = getYieldCurveParameter([curve, "discountFactor"], "switchDates")
#     interpolationIndex = interpolationMetaIndexFromCurveSwitchDates(interpDate, switchDates, maturities)
#     indexBefore = getIndexBefore(pointFloorIndex(maturities, interpDate), len(maturities))
#     matBefore = maturities[indexBefore]
#     if (matBefore == interpDate):
#         return getYieldCurveValues(curve, "discountFactor", refDate)[indexBefore]
#
#
#     interpolationVariable = getIRInterpolVariable(interpolationIndex, curve, "discountFactor")
#     interpolationMethod = getIRInterpolMethod(interpolationIndex, curve, "discountFactor")
#     zeroCouponBasis = getYieldCurveParameter([curve, "discountFactor"], "zeroCouponBasis")
#     if (interpolationVariable == "forwardRate"):
#         return getDiscountFactorFromFwd(curve, refDate, interpDate, indexBefore, maturities, zeroCouponBasis,
#                                         interpolationMethod)
#     if (interpolationVariable == "forwardRate1D"):
#         return getDiscountFactorFromDailyFwd(curve, "discountFactor", refDate, interpDate, indexBefore, matBefore,
#                                              maturities[indexBefore + 1])
#
#
#     values = getYieldCurveValues(curve, interpolationVariable, refDate)
#     zeroCouponFormula = getYieldCurveParameter([curve, "discountFactor"], "zeroCouponFormula")
#     secDerivFirstPt = metaData("YIELD_CURVE", [curve, "discountFactor"], "secDerivFirstPt", 0)
#     secDerivLastPt = metaData("YIELD_CURVE", [curve, "discountFactor"], "secDerivLastPt", 0)
#     compoundFrequency = metaData("YIELD_CURVE", [curve, "discountFactor"], "compoundFrequency", 1)
#     dfInterpolParams = DfInterpolParams(refDateDays, zeroCouponBasis, zeroCouponFormula, compoundFrequency,
#                      interpolationVariable, interpolationMethod, secDerivFirstPt, secDerivLastPt,
#                      getSecondDerivative([curve, interpolationVariable]))
#
#     return discountFactorInterpolator(interpDate, maturities, values, dfInterpolParams, indexBefore)
#
#
# def interpolationMetaIndexFromCurveSwitchDates(date, switchDatesIndex, maturities):
# 	switchDatesIndexsize = len(switchDatesIndex)
# 	for i in range( switchDatesIndexsize):
# 		if (maturities[switchDatesIndex[i]] >= date):
# 			return i
# 	return switchDatesIndexsize
#
# def getDiscountFactorFromFwd(curve, refDate, interpDate, indexBefore, maturities, zeroCouponBasis, interpolationMethod):
# 	values = data1D("YIELD_CURVE", [curve, "forwardRate", interpolationMethod], refDate)
# 	discountValue = 1
# 	matBefore = maturities[indexBefore]
# 	matAfter  = maturities[indexBefore + 1]
# 	valueBefore =  values[indexBefore]
# 	valueAfter = values[indexBefore + 1]
# 	fwd = 0
# 	fromDate = matBefore
#
# 	if (interpDate > matAfter && interpolationMethod != "linear"):
# 		discountValue = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore + 1)
#         fromDate = matAfter
#     else:
#         discountValue = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore)
#
#
# 	if interpolationMethod=="linear":
# 		fwd = fwdDFFromInstLinearForward(interpDate, matBefore, matAfter, valueBefore, valueAfter)
# 	if interpolationMethod== "flatRight":
# 		fwd = flatRightInterpolation(interpDate, matBefore, matAfter, valueBefore, valueAfter)
#
# 	return discountValue * math.exp(-yearFraction(daysToDate(fromDate), daysToDate(interpDate), zeroCouponBasis) * fwd)
#
# def getDiscountFactorFromDailyFwd(curve, curveType, refDate, interpDate, indexBefore, matBefore, matAfter):
# 	lastDF = 1
# 	fwdRate = 0
# 	if (matBefore > interpDate):
# 		matBefore = dateToDays(refDate)
# 		fwdRate = scenarioDataPoint("YIELD_CURVE", [curve, "forwardRate1D"], refDate, indexBefore)
# 	if (interpDate > matAfter) :
# 		lastDF = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore + 1)
# 		fwdRate = scenarioDataPoint("YIELD_CURVE", [curve, "forwardRate1D"], refDate, indexBefore + 1)
# 		matBefore = matAfter
#
# 	fwdRatesBasis = getYieldCurveParameter([curve, curveType], "fwdRatesBasis")
# 	fwdRatesFormula = metaData("YIELD_CURVE", [curve, "discountFactor"], "fwdRatesFormula")
#
# 	lastDFNonBusinessDay = getDiscountFactor(matBefore, interpDate, lastDF, fwdRate, fwdRatesBasis, fwdRatesFormula)
#
# 	return lastDFNonBusinessDay
#
# def getDiscountFactor(start, end, lastDF, fwdRate, basis, fwdRatesFormula):
# 	def factor = 0
# 	if (fwdRatesFormula == "exponential") :
# 		for  curDay in range( start + 1,end+1):
# 			factor += yearFraction(daysToDate(curDay - 1), daysToDate(curDay), basis)
#
# 		return lastDF * math.exp(- fwdRate * factor)
#
#
# 	factor = 1
# 	# simple case
# 	for curDay in range( start + 1, end+1):
# 		factor *= (1 + fwdRate * yearFraction(daysToDate(curDay - 1), daysToDate(curDay), basis))
#
# 	return lastDF / factor
#
# class DfInterpolParams:
# 	refDate = 0
# 	basis = "default"
# 	compoundFormula = "default"
#     compoundFrequency = 1
# 	interpolationVariable = "default"
# 	interpolationMethod = "default"
# 	secDerivFirstPt = 0
# 	secDerivLastPt = 0
# 	secondDerivatives = array(0,0)
#
#
# def discountFactorInterpolator(discountDate, maturities, values, dfInterpolParams, indexBefore):
# 	df = 0
# 	interpolationVariable =	dfInterpolParams.interpolationVariable
# 	if (discountDate < maturities[0] and interpolationVariable != "zeroCouponRate"):
# 		df = curveInterpolator(discountDate, dfInterpolParams.refDate, maturities[0],
# 							   initDiscountFactorValue(interpolationVariable), values[0], dfInterpolParams, indexBefore,
# 							   len(values))
# 	if (len(values) == 1):
# 		df = values[0]
# 	else:
# 		df = curveInterpolator(discountDate, maturities[indexBefore], maturities[indexBefore + 1], values[indexBefore],
# 						   values[indexBefore + 1], dfInterpolParams, indexBefore, len(values))
#
# 	return transformElementToDF(df, discountDate, dfInterpolParams, BasicYearFractionParameters())
#
# def curveInterpolator(date, matBefore, matAfter, valueBefore, valueAfter, dfInterpolParams, indexBefore, nbValues):
# 	if (dfInterpolParams.interpolationMethod == "cubicSpline"):
# 		return getInterpolatedDFWithCubicSpline(nbValues, indexBefore, matBefore, matAfter, valueBefore, valueAfter, date, dfInterpolParams)
# 	if (dfInterpolParams.interpolationMethod == "flatSpread"):
# 		return flatSpreadInterpolation(date, matBefore, matAfter, valueBefore, valueAfter)
# 	#linear or flat interpolation
# 	return getInterpolatedValue(dfInterpolParams.interpolationMethod, date, matBefore, matAfter, valueBefore, valueAfter)
#
# def initDiscountFactorValue(interpolationVariable):
# 	if(interpolationVariable == "logDiscountFactor"):
# 		return 0
# 	return 1
# def getInterpolatedDFWithCubicSpline(nbTenors, indexBefore, pointBefore, pointAfter, valueBefore, valueAfter, point, dfInterpolParams):
# 	if (nbTenors > 2):
# 		return cubicSplineInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter, dfInterpolParams.secondDerivatives[indexBefore],
# 				dfInterpolParams.secondDerivatives[indexBefore+1])
#
# 	return linearInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)
#
# def flatSpreadInterpolation(x, x1, x2, y1, y2):
# 	if (x1 == x2 or x == x1 or y1 == 0):
# 		return y1
# 	if (x == x2 or y2 == 0):
# 		return y2
# 	return 1 / ((x - x1) / (y2 * (x2 - x1)) + 1 / y1)
#
# def transformElementToDF(y, x, params, yfParams):
# 	if params.interpolationVariable == "logDiscountFactor":
# 		return math.exp(y)
# 	if params.interpolationVariable == "zeroCouponRate":
# 		return DFFormula(y, params.refDate, x, params.basis, yfParams, params.compoundFormula, params.compoundFrequency)
# 	if params.interpolationVariable ==  "inverseDiscountFactor":
# 		return 1 / y
#
# 	return y
#
# def DFFormula(zeroCouponRate, refDate, dfDate, basis, yfParams, compoundFormula, compoundFrequency):
# 	yf = yfParams.yearFraction(daysToDate(refDate), daysToDate(dfDate), basis)
# 	if compoundFormula=="exponential":
# 		return math.exp(-zeroCouponRate * yf)
# 	if compoundFormula =="compound":
# 		return pow(1 / (1 + zeroCouponRate * compoundFrequency), yf / compoundFrequency)
#
# 	return 1 / (1 + zeroCouponRate * yf)
