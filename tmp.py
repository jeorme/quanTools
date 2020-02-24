from datetime import datetime



def getExpirySmile(foreignCurrency, domesticCurrency, nbStrikesByExpiry, data, fxVolInfo, fxVolTolerance,fxSpot, expirySmileCurve,isSmileB):
    jacobianSize = getJacobianSize(nbStrikesByExpiry, isSmileB)
    calibrationInstruments = np.zeros((3 * int(jacobianSize) + 1, int(7.0 * (jacobianSize > 0) + 1))) # getJacobianSize() for the smile constaints coming from broker smile

    fxVolInfo.atmVol = data["marketData"]["fxVolatilityQuotes"][0]["quotes"][2]["value"]
    getFxAtmPoint(fxVolInfo, data["marketDataDefinitions"]["fxVolatilities"][0]["expiries"][0]["atmConvention"], 100, expirySmileCurve, fxSpot, calibrationInstruments)

    # strategyRank = 0
    # for otmComponent  in smileStrategies.otm:
    #      getBSVolFromBfRr(recordIndexId, foreignCurrency, domesticCurrency, fxVolInfo, otmRecord, outputFxSmile, calibrationInstruments,nbStrikesByExpiry)
    #
    # computeInterpSpaceParam(fxVolInfo, expirySmileCurve)
    # nbStrikeInTheSmile = calibrationInstruments[0][0]
    # resize(expirySmileCurve, expirySmileCurve.shape[0], nbStrikeInTheSmile)
    # # insertionSortExpirySmileStrike(nbStrikeInTheSmile, expirySmileCurve)
    #
    # if isSmileB:
    #     jacRepo = matrix(jacobianSize + 3, jacobianSize, 0.0) # 2 for LU pivoting + 1 for f0 = fct() to solve
    #     effectiveProblemDimension = getCalibrationProblemDimension(smileStrategies, isOtmDefined)
    #     idLineFromSmile = matrixLine(expirySmileCurve, 4)
    #     for strikeColumn =0; strikeColumn < nbStrikeInTheSmile; strikeColumn ++:
    #         idIndex = idLineFromSmile[strikeColumn]
    #         for i = 0;i < nbStrikeInTheSmile;i ++:
    #             IdConstraint = calibrationInstruments[i][2]
    #                 if idIndex == IdConstraint:
    #                     calibrationInstruments[i][3] = strikeColumn
    #                     break
    #     fitFxVolatilitySmile(calibrationInstruments, fxVolInfo, fxVolTolerance, effectiveProblemDimension, expirySmileCurve,jacRepo)
    #
    # else:
    #     computeInterpolationHelperParams(expirySmileCurve, fxVolInfo.interpMethod)
