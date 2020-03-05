
# def getATMVolatility(expiry, curveName, curveType):
#     values = data1D(curveType, [curveName, "ATM_VOLATILITY"], calculationDate())
#     atmCurveSize = len(values)
#     if(atmCurveSize == 1):
#         return values[0]
#
#     expiries = axis(curveType, [curveName, "ATM_VOLATILITY"], 0)
#     t_t0 = dateToDays(expiry)
#     tenorFloorIndex = pointFloorIndex(expiries, t_t0)
#     pointBeforeIndex = getVolIndexBefore(tenorFloorIndex, atmCurveSize)
#     ti_t0 = expiries[pointBeforeIndex]
#     atmVoli = values[pointBeforeIndex]
#
#     if (abs(t_t0 - ti_t0) < getTimePrecision()):
#         return atmVoli
#     ti1_t0 = expiries[pointBeforeIndex + 1]
#     atmVoli1 = values[pointBeforeIndex + 1]
#
#     if (abs(t_t0 - ti1_t0) < getTimePrecision()):
#         return atmVoli1
#
#     return getExpiryVolatility(tenorFloorIndex, ti_t0, ti1_t0, atmVoli, atmVoli1, t_t0, curveName, curveType)
#
# def getTimePrecision():
# 	return 1e-10
#
# def getExpiryVolatility(expiryFloorIndex, tBeforeAsDays, tAfterAsDays, volBefore, volAfter, tAsDays, surfaceName, surfaceType):
# 	interpVariable = getInterpolationVariableOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())
# 	interpolationMethod = getInterpolationMethodOnAxis(expiryFloorIndex, [surfaceName], surfaceType, ExpiriesAxisMetaData())
#
# 	if (expiryFloorIndex == -1 and interpVariable == "timeWeightedTotalVariance" and interpolationMethod == "linear"):
# 		tAfterAsDays = tBeforeAsDays
# 		volAfter = volBefore
# 		tBeforeAsDays = dateToDays(calculationDate())
#
#
# 	if (abs(tAsDays - tBeforeAsDays) < getTimePrecision()):
# 		return volBefore
# 	if (abs(tAsDays - tAfterAsDays) < getTimePrecision()):
# 		return volAfter
# 	nbDaysCalcDate = dateToDays(calculationDate())
# 	tAsDays -= nbDaysCalcDate
# 	if (tAsDays == 0):
# 		return volBefore
# 	tBeforeAsDays -= nbDaysCalcDate
# 	volBefore = transformImpliedVolToInterpVariable(volBefore, tBeforeAsDays, interpVariable)
#
# 	tAfterAsDays -= nbDaysCalcDate
# 	volAfter = transformImpliedVolToInterpVariable(volAfter, tAfterAsDays, interpVariable)
#
# 	if (interpVariable != "timeWeightedTotalVariance"):
# 		volBefore = getInterpolatedValue(interpolationMethod, tAsDays, tBeforeAsDays, tAfterAsDays, volBefore, volAfter)
# 	else:
# 		volBefore = computeWeightedInterpolation(tBeforeAsDays, volBefore, tAfterAsDays, volAfter, tAsDays, nbDaysCalcDate, surfaceName, surfaceType)
#
# 	return transformInterpVariableToImpliedVol(volBefore, tAsDays, interpVariable)
#
# def getInterpolationVariableOnAxis(floorIndex, surfaceParameters, surfaceType, axisMetaData):
# 	if (floorIndex == -1):
# 		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationVariableBeforeFirstPoint())
# 	if (floorIndex == -2):
# 		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationVariableAfterLastPoint())
# 	return metaData(surfaceType, surfaceParameters, axisMetaData.getInterpolationVariable())
#
# def getInterpolationMethodOnAxis(floorIndex, surfaceParameters, surfaceType, axisMetaData):
# 	if (floorIndex == -1):
# 		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationMethodBeforeFirstPoint())
# 	if (floorIndex == -2):
# 		return metaData(surfaceType, surfaceParameters, axisMetaData.getExtrapolationMethodAfterLastPoint())
# 	return metaData(surfaceType, surfaceParameters, axisMetaData.getInterpolationMethod())
#
#
# def transformImpliedVolToInterpVariable(vol, relativeDate, dataTypeToInterpolate):
# 	if dataTypeToInterpolate == "variance":
# 		return vol * vol
# 	if dataTypeToInterpolate == "volatility":
# 		return vol
# 	return vol * vol * relativeDate
#
# def transformInterpVariableToImpliedVol(variable, relativeDate, dataTypeToInterpolate):
# 	if dataTypeToInterpolate == "variance":
# 		return math.sqrt(variable)
# 	if dataTypeToInterpolate == "volatility":
# 		return variable
# 	return math.sqrt(variable / relativeDate)
#
# def computeWeightedInterpolation(tBeforeAsDays, volBefore, tAfterAsDays, volAfter, tAsDays, nbDaysCalcDate, surfaceName, surfaceType):
# 	omega1 = getVolTimeAdjWeight(tBeforeAsDays + nbDaysCalcDate, tAsDays + nbDaysCalcDate, surfaceName, surfaceType)
#
# 	omega = getVolTimeAdjWeight(tBeforeAsDays + nbDaysCalcDate, tAfterAsDays + nbDaysCalcDate, surfaceName, surfaceType)
#
# 	omega = omega1 / omega
# 	return (omega * volAfter + (1 - omega) * volBefore)
#
# def getVolTimeAdjWeight(ts, te, surfaceName, surfaceType):
#     sign = 1
#     if(ts > te):
# 		t = ts
# 		ts = te
# 		te = t
# 		sign = -1
#
#     volTimeWeight = getWeightFromPeriodPattern(ts, te, metaData(surfaceType, [surfaceName], "periodicTimesVolTimeAdj"), metaData(surfaceType, [surfaceName], "periodicCumulativeTimeWeights"))
#     volTimeWeight += getWeightFromEventsRange(ts, te,  metaData(surfaceType, [surfaceName], "holidaysStartEndAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "holidaysCumulativeTimeWeights"))
#     volTimeWeight += getWeightFromEventsRange(ts, te,  metaData(surfaceType, [surfaceName], "eventsStartEndAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "eventsCumulativeTimeWeights"))
#     volTimeWeight += getWeightFromEventsDates(ts, te,  metaData(surfaceType, [surfaceName], "eventsDateAsDaysVolTimeAdj"), metaData(surfaceType, [surfaceName], "eventsCumulativeDateWeights"))
#     return sign * volTimeWeight
#
# def getWeightFromPeriodPattern(ts, te, times, cumulTimeWeights):
# 	return getWeightFromCumulativeTimeWeights(getWeightFromPeriodCumulTimeWeightPatternHelper, ts, te, times, cumulTimeWeights, te - ts)
#
# def getWeightFromCumulativeTimeWeights(weightFunctor, ts, te, times, cumulTimeWeights, defaultVal):
# 	if(!isDefined(times) or !isDefined(cumulTimeWeights) or abs(ts - te) <  getTimePrecision()):
# 		return defaultVal
# 	return weightFunctor(ts, te, times, cumulTimeWeights)
#
# def getWeightFromPeriodCumulTimeWeightPatternHelper(ts, te, times, cumulTimeWeights):
#     if(len(times) <=1):
#         return  te - ts
#     # 3 is sunday from epoch 01 jan 1970
# 	nbTimes = len(times)-1
#     dperiodLength = times[nbTimes] # times[0] = 0  REQUIRED
#     nbPeriods = floor ((te - ts) / periodLength)
#     return nbPeriods * cumulTimeWeights[nbTimes] + getWeightFromRangeLessThanAPeriod(ts + nbPeriods * periodLength, te, periodLength, times, cumulTimeWeights, getWeightFromCumulTimeWeightWithStartAndEndInRange)
#
# def getWeightFromEventsRange(ts, te, times, cumulTimeWeights):
# 	return getWeightFromCumulativeTimeWeights(getWeightFromCumulTimeWeightWithStartAndEndInRange, ts, te, times, cumulTimeWeights, 0)
#
# def getWeightFromCumulTimeWeightWithStartAndEndInRange(timeS, timeE, times, cumulTimeWeights):
#     if(len(times)<=1)
#         return 0
#     #REQUIRED: length(times) >= 2
# 	nbTimes = length(times)
# 	timelast = times[nbTimes-1]
# 	timeFirst = times[0]
#     timeS = max(timeS, timeFirst)
#     timeE = min(timeE, timelast)
#     if(timeS >= timelast || timeE <= timeFirst):
#         return 0
#     #We are sure that periodicTimeIndexS < length(times)-1
#     periodicDayIndexE = binaryFloorIndex(times, timeE)
#     if(length(times) - 1 == periodicDayIndexE):
#         periodicDayIndexE -= 1
#     periodicTimeIndexS = binaryFloorIndex(times, timeS)
#     prevCumulWeight = cumulTimeWeights[periodicTimeIndexS+1]
#     if(times[periodicTimeIndexS+1] == times[periodicTimeIndexS]):
#         error("duplicate dates not allowed in volatility time adjustment  date axis patterns, you can use instead eventsDateAsDaysVolTimeAdj and eventsCumulativeDateWeights")
#
#     weight0 = (prevCumulWeight - cumulTimeWeights[periodicTimeIndexS])/(times[periodicTimeIndexS+1] - times[periodicTimeIndexS])
#     if(periodicTimeIndexS == periodicDayIndexE):
#         return  weight0 * (timeE - timeS)
#
#     # we are sure at this stage that periodicDayIndexE >= 1 because periodicDayIndexE > periodicTimeIndexS>= 0
#     dtPrev = times[periodicTimeIndexS+1]
#     weightTime = weight0 * (dtPrev - timeS)# first part
#     nextCumulWeight = cumulTimeWeights[periodicDayIndexE]
#     weightTime += (nextCumulWeight -  prevCumulWeight)
#     dtPrev = times[periodicDayIndexE]
#     if(abs(times[periodicDayIndexE+1] - dtPrev) <  getTimePrecision()):
#         error("duplicate dates not allowed in volatility time adjustment  date axis patterns, you can use instead eventsDateAsDaysVolTimeAdj and eventsCumulativeDateWeights")
#
#     weightTime += ((cumulTimeWeights[periodicDayIndexE+1] - nextCumulWeight)/(times[periodicDayIndexE+1] - dtPrev))*(timeE - dtPrev)#last part
#     return weightTime
#
# def getWeightFromEventsDates(ts, te, times, cumulTimeWeights):
# 	return  getWeightFromCumulativeTimeWeights(getWeightFromCumulTimeWeightWithDateEvents, ts, te, times, cumulTimeWeights, 0)
#
# def getWeightFromCumulTimeWeightWithDateEvents(timeS, timeE, times, cumulTimeWeights):
#
# 	if(len(times)== 0):
# 		return 0
#
# 	timeFirst = times[0]
# 	if(len(times) == 1):
# 		if(timeS <= timeFirst && timeFirst<= timeE):
# 			return cumulTimeWeights[0]
# 		return 0
#
#
# 	#case length(times)>= 2
# 	if(timeS >= times[len(times)-1] or timeE <= times[0]):
# 		return 0
# 	#case timeS < times[length(times)-1] and times[0] < timeE
# 	#so periodicTimeIndexS <= length(times)-2 and periodicDayIndexE >= 1
# 	timeS = max(timeS, timeFirst) #so periodicTimeIndexS >= 0
# 	periodicTimeIndexS = binaryFloorIndex(times, timeS)
# 	if(abs (timeS - times[periodicTimeIndexS]) <  getTimePrecision())
# 		periodicTimeIndexS -= 1
# 	#timeE = min(timeE, times[length(times)-1]) //so periodicDayIndexE <= length(times)-1
# 	periodicDayIndexE = binaryFloorIndex(times, timeE)
# 	if(abs(timeE - times[periodicDayIndexE]) < getTimePrecision()):
# 		periodicDayIndexE -= 1 #still periodicDayIndexE >= 0
# 	cumulWeight1 = 0
# 	if(periodicTimeIndexS >= 0):
# 		cumulWeight1 = cumulTimeWeights[periodicTimeIndexS]
# 	return cumulTimeWeights[periodicDayIndexE] - cumulWeight1
#


#
#
#
# def copyInitialPoints(initPoints, initialPoints, nbParameters):
# 	for i in range(nbParameters):
# 		initPoints[i] = initialPoints[i+1]
#
#
#