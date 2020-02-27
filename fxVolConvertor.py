#allocate output matrix
expiries = metaData("FX_VOLATILITY", [surfaceName], "expiries")
outputMatrix = allocateDeltaStrikeMatrix(surfaceName, expiries)
smileAxis = metaData("FX_VOLATILITY", [surfaceName], "smileAxis")
if (smileAxis == "DELTA_CALL" or smileAxis == "DELTA_PUT"):
    return strikeDeltaConvertor(outputMatrix, surfaceName, convertFromDelta, getDeltaCallOrPutIndicator(smileAxis), targetSmileAxis, expiries)


if (isStrikeToLog(targetSmileAxis, smileAxis)):
    return strikeDeltaConvertor(outputMatrix, surfaceName, convertFromStrikeOrLog, 1, targetSmileAxis, expiries)


return strikeDeltaConvertor(outputMatrix, surfaceName, convertFromStrike, getDeltaCallOrPutIndicator(targetSmileAxis), smileAxis, expiries)

