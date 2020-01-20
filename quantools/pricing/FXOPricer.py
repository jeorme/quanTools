import math
from quantools.pricing.mathematicTools import bivariateCND


def windowBarrierPricer(ForeignRate,DomesticRate,fixedAmount, optionType,cashPercent,PaymentAt,volatility,Spot,Strike,Time,
                                  timeToSettle,windowBarrierType,Barrier1Level,Barrier1Rebate,Barrier1Direction,Barrier1Activaition,
                                  Barrier2Level,Barrier2Rebate,Barrier2Direction,Barrier2Activaition, computePrimeOnly,hideTraces):
    # if windowBarrierType == "SingleEarlyEnding":
    #     return priceSingleEarlyEnding()

    return 0

# def priceSingleEarlyEnding():
#     barrierDate = daysToDate(option.barrierDates[0])
#
#     if (barrierDate == option.expiryDate)
#         return priceSingleBarrierOption(option, vol, sqrtVolYF, rateYF, spot, dfPv, dfFor, dfDom, "FX_RATE",
#                                         [pricingData.foreignCurrency, pricingData.domesticCurrency], barrierCross1D,
#                                         barrierType, 0)[0]
#
#     level = barrierDetails.level
#
#     direction = barrierDetails.upOrDown
#
#     isCrossed = isFrontWindowBarrierCrossed([pricingData.foreignCurrency, pricingData.domesticCurrency], barrierDetails.isCrossed,
#                                 barrierDate, level, direction)
#
#     #Observation window is closed and option is not activated or the option has been desactivated
#
#     if ((barrierDate <= calculationDate() & & !isCrossed & & barrierType == 1) | | (isCrossed & & barrierType == -1))
#         return 0
#
#     callOrPut = option.callOrPut
#
#     strike = option.strike
#
#     stdDev = vol * sqrtVolYF
#
#     forward = spot * dfFor / dfDom
#
#     if ((isCrossed & & barrierType == 1) | | (!isCrossed & & barrierType == -1 & & barrierDate <= calculationDate())):
#         return dfPv * getBlackForwardPrice(forward, strike, stdDev, callOrPut)
#
#
#     surfaceName = pricingData.volatilityName
#     b = computeCostOfCarry(dfDom, dfFor, surfaceName, dateToDays(option.deliveryDate), pricingData)
#     priceFactor = 1
#     strikeFactor = strike
#     levelFactor = level
#     df1 = dfDom
#     df2 = dfFor
#     eta = -direction
#     spotSqr = spot * spot
#
#     if (callOrPut == -1):
#         priceFactor = strike / spot
#         strikeFactor = spotSqr / strike
#         levelFactor = spotSqr / level
#         df1 = dfFor
#         df2 = dfDom
#         eta = direction
#         b = -b
#
#
#     muFactor = 2 * (b / (vol * vol)) - 1
#     ratio = levelFactor / spot
#     pow1 = pow(ratio, muFactor + 2)
#
#     pow2 = pow(ratio, muFactor)
#
#     if (isPlusInfinity(pow1) | | isPlusInfinity(pow2))
#         warning("Volatility level is too low to price : ", vol)
#         error ("Volatility level is too low to price.")
#
#
#
#     volBasis = metaData("FX_VOLATILITY", [surfaceName], "volatilityBasis")
#
#
#     wYF = withFloorToMinTime(yearFractionBasic(calculationDate(), barrierDate, volBasis))
#
#
#     wSqrtVolYF = sqrt(wYF)
#
#
#     wStdDev = vol * wSqrtVolYF
#
#
#     rho = wSqrtVolYF / sqrtVolYF
#
#
#     bsD1 = getBSCallPutPricePlusDCoefficient(forward, strike, stdDev)
#
#
#     nd1 = spot * dfFor * normalCDF(callOrPut * bsD1)
#
#
#     nd2 = strike * dfDom * normalCDF(callOrPut * (bsD1 - stdDev))
#
#
#     fwd = spot * df2 / df1
#
#
#     wFwd = spot * exp(b * wYF)
#
#
#     coeff1 = spot * df2
#
#
#     coeff2 =strikeFactor * df1
#
#
#     priceDf =dfPv / dfDom
#
#     return priceFrontWindow(spot, strikeFactor, levelFactor, fwd, wFwd, coeff1, coeff2, pow1, pow2, stdDev, wStdDev, eta,
#                         rho, nd1, nd2, callOrPut, priceDf, priceFactor, barrierType)
#
# def priceFrontWindow(spot, strike, level, fwd, wFwd, coeff1, coeff2, pow1, pow2, stdDev, wStdDev, eta, rho, nd1, nd2, callOrPut, priceDf, priceFactor, barrierType):
#
#     d1 = getD1E1G1(fwd, strike, stdDev)
#     d2 = d1 - stdDev
#
#     f1 = getF1(d1, spot, level, stdDev)
#     f2 = f1 - stdDev
#
#     e1 = getD1E1G1(wFwd, level, wStdDev)
#     e2 = e1 - wStdDev
#
#     e3 = getE3(e1, spot, level, wStdDev)
#     e4 = e3 - wStdDev
#
#     etaRho = eta * rho
# 	b1 = bivariateCND(d1, e1 * eta, etaRho)
# 	b2 = pow1 * bivariateCND(f1, e3 * eta, etaRho)
# 	b3 = bivariateCND(d2, e2 * eta, etaRho)
# 	b4 = pow2 * bivariateCND(f2, e4 * eta, etaRho)
#
# 	return priceFrontWindowOrRearB1(callOrPut, barrierType, priceDf, priceFactor, coeff1, coeff2, b1, b2, b3, b4, nd1, nd2)
#
#
# def priceFrontWindowOrRearB1(callOrPut, barrierType, priceDf, priceFactor, coeff1, coeff2, b1, b2, b3, b4, nd1, nd2):
# 	# Knock-Out option
# 	if (barrierType == -1):
# 		return priceDf * priceFactor * (coeff1 * (b1 - b2) - coeff2 * (b3 - b4)) # keep this formula order for instability result issue
# 	# Knock-In option
# 	if (b4 <= 1e-10 && b2 <= 1e-10 && b3 >= 1e-10 && b1 >= 1e-10):
# 		return 0
# 	if (callOrPut == 1):
# 		return priceDf * (((nd1 - coeff1 * b1) + coeff1 * b2) - ((nd2 - coeff2 * b3) + coeff2 * b4))
# 	return priceDf * (((nd2 - priceFactor * coeff1 * b1) - (nd1 - priceFactor * coeff2 * b3)) + (priceFactor * (coeff1 * b2 - coeff2 * b4)))
#
# def getD1E1G1(forward, X, stdDev):
#     return (math.log(forward / X) + 0.5 * stdDev * stdDev) / stdDev
