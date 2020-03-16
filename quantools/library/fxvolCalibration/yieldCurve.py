import math
from datetime import datetime

from dateutil.parser import parse
from quantools.analyticsTools.analyticsTools import yearFraction
from quantools.library.utilities.interpolation import getInterpolatedValue, cubicSplineInterpolation, linearInterpolation
from quantools.library.utilities.utilitiesAccessor import pointFloorIndex, getIndexBefore
import numpy as np

def discountFactorFromDays( ycValuesFor, ycDefFor, refDate,startDate, endDate):
	return computeDiscountFactor( ycValuesFor, ycDefFor, refDate, endDate) / computeDiscountFactor( ycValuesFor, ycDefFor, refDate, startDate)


def computeDiscountFactor( ycValuesFor, ycDefFor, refDate, discountDate):
	if (discountDate > refDate):
		return interpolateDFOnCurve(ycValuesFor, ycDefFor, discountDate, refDate)
	return 1

def getMaturity(ycDefFor):
	return  [datetime.strptime(x,"%Y-%m-%d") for x in ycDefFor["maturities"] ]


#@profile
def interpolateDFOnCurve(values, ycDefFor, interpDate, refDate):
	switchDates = [0,len(ycDefFor["maturities"])-1]
	# getMaturity = np.vectorize(lambda x: parse(x))
	# maturities = getMaturity(ycDefFor["maturities"])
	maturities = getMaturity(ycDefFor)
	interpolationIndex = interpolationMetaIndexFromCurveSwitchDates(interpDate, switchDates, maturities)
	indexBefore = getIndexBefore(pointFloorIndex(maturities, interpDate), len(maturities))
	matBefore = maturities[indexBefore]
	if (matBefore == interpDate):
		return values[indexBefore]
	if interpolationIndex ==0:
		interpolationVariable, interpolationMethod = ycDefFor["extrapolationBeforeFirstPoint"]["variable"], ycDefFor["extrapolationBeforeFirstPoint"][
			"method"]
	if interpolationIndex ==2:
		interpolationVariable, interpolationMethod = ycDefFor["extrapolationAfterLastPoint"]["variable"], \
													 ycDefFor["extrapolationAfterLastPoint"][
														 "method"]
	else:
		interpolationVariable, interpolationMethod = ycDefFor["interpolation"]["variable"], ycDefFor["interpolation"][
			"method"]


	zeroCouponBasis = ycDefFor["zeroCouponBasis"]
	if (interpolationVariable == "FORWARD_RATE"):
		pass
		#return getDiscountFactorFromFwd(curve, refDate, interpDate, indexBefore, maturities, zeroCouponBasis,
#                                          interpolationMethod)
#      if (interpolationVariable == "forwardRate1D"):
#          return getDiscountFactorFromDailyFwd(curve, "discountFactor", refDate, interpDate, indexBefore, matBefore,
#                                               maturities[indexBefore + 1])

	zeroCouponFormula = ycDefFor["zeroCouponFormula"]
	secDerivFirstPt = ycDefFor["secDerivFirstPt"] if "secDerivFirstPt" in ycDefFor else 0
	secDerivLastPt = ycDefFor["secDerivFirstPt"] if "secDerivLastPt" in ycDefFor else 0
	secondDerivatives = ycDefFor["SECOND_DERIVATIVE"] if "SECOND_DERIVATIVE" in ycDefFor else []
	if interpolationVariable == "ZERO_COUPON_RATE":
		ZC = np.vectorize(ZCFormula,excluded=['refDate','basis','compoundFormula'])
		values = ZC(discountFactor=values,dfDate=maturities,refDate=refDate,basis=zeroCouponBasis,compoundFormula=zeroCouponFormula)
	compoundFrequency = ycDefFor["compoundFrequency"] if "compoundFrequency" in ycDefFor else 1
	dfInterpolParams = DfInterpolParams(refDate, zeroCouponBasis, zeroCouponFormula, compoundFrequency,
                       interpolationVariable, interpolationMethod, secDerivFirstPt, secDerivLastPt,
                      secondDerivatives)

	return discountFactorInterpolator(interpDate, maturities, values, dfInterpolParams, indexBefore)
#
#
def interpolationMetaIndexFromCurveSwitchDates(date, switchDatesIndex, maturities):
	switchDatesIndexsize = len(switchDatesIndex)
	for i in range( switchDatesIndexsize):
		if (maturities[switchDatesIndex[i]] >= date):
			return i
	return switchDatesIndexsize
#
#  def getDiscountFactorFromFwd(curve, refDate, interpDate, indexBefore, maturities, zeroCouponBasis, interpolationMethod):
#  	values = data1D("YIELD_CURVE", [curve, "forwardRate", interpolationMethod], refDate)
#  	discountValue = 1
#  	matBefore = maturities[indexBefore]
#  	matAfter  = maturities[indexBefore + 1]
#  	valueBefore =  values[indexBefore]
#  	valueAfter = values[indexBefore + 1]
#  	fwd = 0
#  	fromDate = matBefore
#
#  	if (interpDate > matAfter && interpolationMethod != "LINEAR"):
#  		discountValue = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore + 1)
#          fromDate = matAfter
#      else:
#          discountValue = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore)
#
#
#  	if interpolationMethod=="LINEAR":
#  		fwd = fwdDFFromInstLinearForward(interpDate, matBefore, matAfter, valueBefore, valueAfter)
#  	if interpolationMethod== "flatRight":
#  		fwd = flatRightInterpolation(interpDate, matBefore, matAfter, valueBefore, valueAfter)
#
#  	return discountValue * math.exp(-yearFraction(daysToDate(fromDate), daysToDate(interpDate), zeroCouponBasis) * fwd)
#
#  def getDiscountFactorFromDailyFwd(curve, curveType, refDate, interpDate, indexBefore, matBefore, matAfter):
#  	lastDF = 1
#  	fwdRate = 0
#  	if (matBefore > interpDate):
#  		matBefore = dateToDays(refDate)
#  		fwdRate = scenarioDataPoint("YIELD_CURVE", [curve, "forwardRate1D"], refDate, indexBefore)
#  	if (interpDate > matAfter) :
#  		lastDF = scenarioDataPoint("YIELD_CURVE", [curve, "discountFactor"], refDate, indexBefore + 1)
#  		fwdRate = scenarioDataPoint("YIELD_CURVE", [curve, "forwardRate1D"], refDate, indexBefore + 1)
#  		matBefore = matAfter
#
#  	fwdRatesBasis = getYieldCurveParameter([curve, curveType], "fwdRatesBasis")
#  	fwdRatesFormula = metaData("YIELD_CURVE", [curve, "discountFactor"], "fwdRatesFormula")
#
#  	lastDFNonBusinessDay = getDiscountFactor(matBefore, interpDate, lastDF, fwdRate, fwdRatesBasis, fwdRatesFormula)
#
#  	return lastDFNonBusinessDay
#
#  def getDiscountFactor(start, end, lastDF, fwdRate, basis, fwdRatesFormula):
#  	def factor = 0
#  	if (fwdRatesFormula == "EXPONENTIAL") :
#  		for  curDay in range( start + 1,end+1):
#  			factor += yearFraction(daysToDate(curDay - 1), daysToDate(curDay), basis)
#
#  		return lastDF * math.exp(- fwdRate * factor)
#
#
#  	factor = 1
#  	 simple case
#  	for curDay in range( start + 1, end+1):
#  		factor *= (1 + fwdRate * yearFraction(daysToDate(curDay - 1), daysToDate(curDay), basis))
#
#  	return lastDF / factor
#
class DfInterpolParams:
	def __init__(self,refDate=0,basis="default",compoundFormula="default",compoundFrequency=1,interpolationVariable="default",interpolationMethod="default",secDerivFirstPt=0,secDerivLastPt=0, secondDerivatives=[]):
		self.refDate = refDate
		self.basis = basis
		self.compoundFormula = compoundFormula
		self.compoundFrequency = compoundFrequency
		self.interpolationVariable = interpolationVariable
		self.interpolationMethod = interpolationMethod
		self.secDerivFirstPt = secDerivFirstPt
		self.secDerivLastPt = secDerivLastPt
		self.secondDerivatives = secondDerivatives


def discountFactorInterpolator(discountDate, maturities, values, dfInterpolParams, indexBefore):
	df = 0
	interpolationVariable =	dfInterpolParams.interpolationVariable
	if (discountDate < maturities[0] and interpolationVariable != "ZERO_COUPON_RATE"):
		df = curveInterpolator(discountDate, dfInterpolParams.refDate, maturities[0],initDiscountFactorValue(interpolationVariable), values[0], dfInterpolParams, indexBefore,len(values))
	if (len(values) == 1):
		df = values[0]
	else:
		df = curveInterpolator(discountDate, maturities[indexBefore], maturities[indexBefore + 1], values[indexBefore],
	 					   values[indexBefore + 1], dfInterpolParams, indexBefore, len(values))
	return transformElementToDF(df, discountDate, dfInterpolParams)

def curveInterpolator(date, matBefore, matAfter, valueBefore, valueAfter, dfInterpolParams, indexBefore, nbValues):
	if (dfInterpolParams.interpolationMethod == "CUBIC_SPLINE"):
		return getInterpolatedDFWithCubicSpline(nbValues, indexBefore, matBefore, matAfter, valueBefore, valueAfter, date, dfInterpolParams)
	if (dfInterpolParams.interpolationMethod == "FLAT_SPREAD"):
		return flatSpreadInterpolation(date, matBefore, matAfter, valueBefore, valueAfter)
	#linear or flat interpolation
	return getInterpolatedValue(dfInterpolParams.interpolationMethod, date, matBefore, matAfter, valueBefore, valueAfter)

def initDiscountFactorValue(interpolationVariable):
	if(interpolationVariable == "logDiscountFactor"):
		return 0
	return 1

def getInterpolatedDFWithCubicSpline(nbTenors, indexBefore, pointBefore, pointAfter, valueBefore, valueAfter, point, dfInterpolParams):
	if (nbTenors > 2):
		return cubicSplineInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter, dfInterpolParams.secondDerivatives[indexBefore],
				dfInterpolParams.secondDerivatives[indexBefore+1])

	return linearInterpolation(point, pointBefore, pointAfter, valueBefore, valueAfter)

def flatSpreadInterpolation(x, x1, x2, y1, y2):
	if (x1 == x2 or x == x1 or y1 == 0):
		return y1
	if (x == x2 or y2 == 0):
		return y2
	return 1 / ((x - x1) / (y2 * (x2 - x1)) + 1 / y1)

def transformElementToDF(y, x, params):
	if params.interpolationVariable == "LOG_DISCOUNT_FACTOR":
		return math.exp(y)
	if params.interpolationVariable == "ZERO_COUPON_RATE":
		return DFFormula(y, params.refDate, x, params.basis, params.compoundFormula, params.compoundFrequency)
	if params.interpolationVariable ==  "INVERSE_DISCOUNT_FACTOR":
		return 1 / y
	return y

def DFFormula(zeroCouponRate, refDate, dfDate, basis, compoundFormula, compoundFrequency):
	yf = yearFraction(refDate, dfDate, basis)
	if compoundFormula=="EXPONENTIAL":
		return math.exp(-zeroCouponRate * yf)
	if compoundFormula =="COMPOUND":
		return pow(1 / (1 + zeroCouponRate * compoundFrequency), yf / compoundFrequency)

	return 1 / (1 + zeroCouponRate * yf)

def transformElementFromDF(y, x, params, yfParams, preprocessParams):
	if params.interpolationVariable == "LOG_DISCOUNT_FACTOR":
		return math.log(y)
	if params.interpolationVariable == "ZERO_COUPON_RATE":
		return ZCFormula(y, params.refDate, x, params.basis, params.compoundFormula)
	if params.interpolationVariable == "INVERSE_DISCOUNT_FACTOR":
		return 1 / y
	# if params.interpolationVariable =="forwardRate1D":
	# 	dailyForwardRate = implyForward(y / preprocessParams.prevDF, params.basis, params.compoundFormula, preprocessParams.prevDFDate, x)
	# 	updateParams(preprocessParams, dailyForwardRate, x, y)
	# 	return dailyForwardRate
	# if params.interpolationVariable =="forwardRate":
	# 	instantForwardRate = instantaneousForwardRate(y, x, params, yfParams, preprocessParams)
	# 	updateParams(preprocessParams, instantForwardRate, x, y)
	# 	return instantForwardRate
	return y

def updateParams(preprocessParams, instantForwardRate, x, y):
	preprocessParams.previousForwardRateValue = instantForwardRate
	preprocessParams.prevDFDate = x
	preprocessParams.prevDF = y

class PreprocessingParams:
	def __init__(self,prevDF,prevDFDate,previousForwardRateValue):
		self.prevDF = prevDF
		self.prevDFDate = prevDFDate
		self.previousForwardRateValue = previousForwardRateValue

def ZCFormula(discountFactor, refDate, dfDate, basis, compoundFormula):
	if (refDate == dfDate):
		return 0
	yf = yearFraction(refDate, dfDate, basis)
	if compoundFormula=="EXPONENTIAL":
		return -math.log(discountFactor) / yf
	if compoundFormula=="COMPOUND":
		return pow(1 / discountFactor, 1 / yf) - 1
	if compoundFormula=="SIMPLE":
		return (1 / discountFactor - 1) / yf

