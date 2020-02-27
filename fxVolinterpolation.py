surface = matrix(length(expiryPoints), nbMaxPointsPerExpiry, 0.0)
lineIndex = 0
surfaceName = volatilitySurface
foreignCurrency = metaData("FX_VOLATILITY", [surfaceName], "foreignCurrency")
domesticCurrency = metaData("FX_VOLATILITY", [surfaceName], "domesticCurrency")
spotDate = getSpotDate(foreignCurrency, domesticCurrency)
s0 = getFxRate(foreignCurrency, domesticCurrency, calculationDate())

foreignCurve = metaData(surfaceType, [surfaceName], "foreignCurve")
domesticCurve = metaData(surfaceType, [surfaceName], "domesticCurve")

for (expiryPoint in expiryPoints) :
    columnIndex = 0
    if isDefined(expiryPoint.pointsDetails.atmConvention) and expiryPoint.pointsDetails.atmConvention != "none":
        surface[lineIndex][columnIndex++] = getATMVolatility(expiryPoint.expiry, surfaceName, surfaceType)

    if len(expiryPoint.points) > 0:
        nbDaysDelivery = dateToDays(expiryPoint.delivery)
        dfFor = discountFactorFromDays(foreignCurve, spotDate, nbDaysDelivery)
        dfDom = discountFactorFromDays(domesticCurve, spotDate, nbDaysDelivery)
        requestType = expiryPoint.pointsDetails.requestType
        sliceType = expiryPoint.pointsDetails.sliceType
        expiry = expiryPoint.expiry
        deltaConvention = expiryPoint.pointsDetails.deltaConvention
        premiumAdjusted = expiryPoint.pointsDetails.premiumAdjusted
        inverseCurrency = expiryPoint.pointsDetails.inverseCurrency
        fwd = s0 * dfFor / dfDom
        for (def point in expiryPoint.points)
            surface[lineIndex][columnIndex++] = getFxVolatility(point, expiry, surfaceName, requestType, deltaConvention, premiumAdjusted, fwd, inverseCurrency, sliceType)

    ++lineIndex

return surface