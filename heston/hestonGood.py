import math
from datetime import datetime

import numpy as np

from heston.CHDE import CHDEminimisationBestSolution
from quantools.library.utilities.solver import findRoot
from scipy.stats import norm

from quantools.library.fxvolCalibration.yieldCurve import discountFactorFromDays, computeDiscountFactor

from quantools.library.fxvolCalibration.fxVol import getDeltaConventionAdjustment, computeStrikeFromDelta, getYcInput, \
    getBlackSpotPrice, getBlackForwardPrice

from quantools.analyticsTools.analyticsTools import yearFraction





def calibrateHestonModel(surface):
	calcDate = datetime.strptime(surface["calibrationDate"],"%Y-%m-%d")
	for fxVolDef in surface["marketDataDefinitions"]["fxVolatilities"]:
		volat_Id = fxVolDef["id"]
		surfaceTenors = list(surface["marketData"]["fxVolatilities"][volat_Id]["values"].keys())[0]
		smileLength = len(surface["marketData"]["fxVolatilities"]["EURGBP_Volatility"]["values"][surfaceTenors]["smileValues"])
		volatilityBasis = fxVolDef["basis"]
		nbExpiries = len(surfaceTenors)
		size = nbExpiries * smileLength
		smileAxisType = surface["marketData"]["fxVolatilities"][volat_Id]["smileAxis"]
		callOrPut = -1 if smileAxisType=="deltaPut" else 1
		isPremiumAdjusted = fxVolDef["premiumAdjusted"]
		mktStrikes = np.zeros((size,1))
		mktVols = np.zeros((size,1))
		forwards = np.zeros((nbExpiries,1))
		expiries = np.zeros((nbExpiries,1))
		dfs = np.zeros((nbExpiries,1))
		weights = np.ones((size,1))* math.sqrt(1.0 / size)
		ycValuesDom, ycDefDom = surface["marketData"]["yieldCurves"][fxVolDef["domesticDiscountId"]]["values"],getDFYC(surface["marketDataDefinitions"]["yieldCurves"],fxVolDef["domesticDiscountId"])
		ycValuesFor, ycDefFor = surface["marketData"]["yieldCurves"][fxVolDef["foreignDiscountId"]]["values"],getDFYC(surface["marketDataDefinitions"]["yieldCurves"],fxVolDef["foreignDiscountId"])
		spotRate , spotDate = getFx(surface["marketData"]["fxRates"],fxVolDef["foreignCurrencyId"],fxVolDef["domesticCurrencyId"])
		index = -smileLength
		for expiry,value in surface["marketData"]["fxVolatilities"][volat_Id]["values"].items():
			yfExpiry = yearFraction(calcDate, datetime.strptime(expiry,"%Y-%m-%d"), volatilityBasis)
			expiries.append( yfExpiry)
			deliveryAsDays =  datetime.strptime(value["delivery"],"%Y-%m-%d")
			smileAxis = value["smileValues"]
			volValues = value["volatilityValues"]
			dfFor = discountFactorFromDays( ycValuesFor, ycDefFor, calcDate, spotDate, deliveryAsDays)
			dfDom = discountFactorFromDays(ycValuesDom, ycDefDom,calcDate, spotDate, deliveryAsDays)
			dfDomPv = computeDiscountFactor( ycValuesDom, ycDefDom, calcDate,deliveryAsDays)
			forward = spotRate * dfFor / dfDom
			dfs.append(dfDomPv)
			forwards.append(forward)
			deltaConvFactor = getDeltaConventionAdjustment(value["deltaConvention"], dfFor)
			sqrtYf = math.sqrt(yfExpiry)

			for j in range(smileLength):
				vol = volValues[j]
				strike = getStrikeFromSmileAxis(smileAxisType, forward, smileAxis[j], vol * sqrtYf, deltaConvFactor, isPremiumAdjusted, callOrPut)
				index = index + smileLength + j
				mktStrikes[index] = strike
				mktVols[index] = vol
				weights[index] = 1 / math.sqrt(getNormedBlackVega(vol * sqrtYf, strike / forward, sqrtYf) * dfDomPv * forward)

		#initialVolATM is the first available by default.
		initialVolATM = mktVols[math.floor(smileLength / 2)]
		v0 = initialVolATM * initialVolATM


		calibHelper = CalibrationHelper(expiries=expiries, forwards=forwards, dfs=dfs, strikes=mktStrikes, mktVols=mktVols, weights=weights, v0=v0)

		initPoints = CHDEminimisationBestSolution(15, 35, 0.6, 0.75, 4, np.array([ 1, 1, 1, 10]),  np.array([-1,1.0E-6, 0, 0]),
												  costFunction, calibHelper)
		return getResultsWithV0(LevenbergMarquardt(costFunctionLV, initPoints, calibHelper, 4, size, 4, np.array([ 1, 1, 1, 10])),
			v0, 4, calibHelper.kappa)

def getStrikeFromSmileAxis(smileAxisType, forward, quote, volStdDev, deltaConventionFactor, premiumAdjusted, callOrPut):
	if (smileAxisType == "deltaCall" or smileAxisType == "deltaPut"):
		return computeStrikeFromDelta(quote, volStdDev, forward, deltaConventionFactor, callOrPut, premiumAdjusted)
	if (smileAxisType == "logMoneyness"):
		return forward * math.exp(quote)
	return quote

def getDFYC(ycDefs,id):
	for ycDef in ycDefs:
		if id == ycDef["id"]:
			return ycDef
	return None

def getFx(fxRates, ccy1, ccy2):
	for rate in fxRates:
		if rate["currency2"] == ccy2 and rate["currency1"] == ccy1:
			return rate["spotDate"],rate["value"]
	return None


def getNormedBlackVega(bsStdDev, moneyness, sqrtYf):
	d1 = (math.log(1 / moneyness) + 0.5 * bsStdDev * bsStdDev) / bsStdDev
	return 1/(math.sqrt(2*math.pi))*math.exp(-0.5*d1*d1) * sqrtYf


class CalibrationHelper:
	def __init__(self,expiries= np.zeros((1,2)),forwards= np.zeros((1,2)),dfs= np.zeros((1,2)),strikes= np.zeros((1,2)),mktVols= np.zeros((1,2)),weights= np.zeros((1,2)),v0=1.0,kappa=0.0):
		self.expiries = expiries# array of expiries
		self.forwards = forwards# array of fwd value at expiry dates
		self.dfs =dfs # array of dfs
		self.strikes =strikes # option strikes
		self.mktVols = mktVols # implied vols
		self.weights = weights # calibration weights
		self.v0 = v0  # V0 parameter
		self.kappa = kappa #equals to 0 when the kappa needs to be calibrated otherwise the value of kappa coming from dataManager is stored



def costFunction(hestonParams, calibHelper):
	expiries = calibHelper.expiries
	forwards = calibHelper.forwards
	dfs = calibHelper.dfs
	strikes = calibHelper.strikes
	mktVols = calibHelper.mktVols
	weights = calibHelper.weights
	nbExpiries = len(expiries)
	nbStrikesPerExp = len(strikes) / nbExpiries
	v0 = calibHelper.v0
	kappa = calibHelper.kappa

	sum = 0.0
	for i in range(nbExpiries):
		time = expiries[i]
		df = dfs[i]
		forward = forwards[i]
		for j in range(nbStrikesPerExp):
			index = i * nbStrikesPerExp + j
			strike = strikes[index]
			price = bgmHestonApprox(time, strike, forward, 1, df, hestonParams[3] + kappa, hestonParams[1], hestonParams[2], hestonParams[0], v0, 1, "", "")
			error = weights[index] * (getImpliedVolatilityFromPrice(1, price, forward, strike, time, df) / mktVols[index] - 1)
			sum += error * error

	return sum

def bgmHestonApprox(time, strike, forward, spot, dfDom, kappa, sigma, theta, rho, v0, flavor, abscissas, weights):
	k2 = kappa * kappa
	k3 = k2 * kappa
	kT = kappa * time
	ekT = math.exp(kT)
	ekTm = math.exp(-kT)
	sigmaEkTm = ekTm * sigma
	rs = rho * sigma
	rsEkTm = rs * ekTm
	ekT2 = 2 * ekT
	e2kT = ekT * ekT
	y = (v0 - theta) * (1 - ekTm) / kappa + theta * time
	sqrtY = math.sqrt(y)

	g = math.log(strike / forward) / sqrtY - 0.5 * sqrtY
	f = g + sqrtY
	bsPrice = dfDom * (strike * norm.cdf(f) - forward * norm.cdf(g))

	a1T = rsEkTm * (v0 * (-kT + ekT - 1) + theta * (kT + ekT * (kT - 2) + 2)) / k2
	a2T = 0.5 * rs * rsEkTm * (v0 * (-kT * (kT + 2) + ekT2 - 2) + theta * (ekT2 * (kT - 3) + kT * (kT + 4) + 6)) / k3
	b0T = 0.25 * sigmaEkTm * sigmaEkTm * (v0 * (-4 * ekT * kT + 2 * e2kT - 2) + theta * (4 * ekT * (kT + 1) + e2kT * (2 * kT - 5) + 1)) / k3
	b2T = 0.5 * a1T * a1T

	putPrice = bsPrice + bgmCorrectionTerm(a1T, a2T, b2T, b0T, y, f, g, strike, dfDom, forward)

	if (flavor == -1):
		return putPrice
	return  putPrice + dfDom * (forward - strike)

def bgmCorrectionTerm(a1T, a2T, b2T, b0T, y, f, g, strike, dfDom, forward):
	sqrt2Pi = math.sqrt(2 * np.pi())
	sqrtY = math.sqrt(y)
	ySqrtY = 1 / (sqrtY * y)
	y2 = y * y
	y3 = y2 * y
	f2 = f * f
	g2 = g * g
	fg = f * g
	fg2 = f * g2
	f2g = f2 * g
	phif = 0.5 * math.exp(-0.5 * f2) / sqrt2Pi
	phig = 0.5 * math.exp(-0.5 * g2) / sqrt2Pi
	strikeStar = strike * dfDom * phif
	fStar = forward * dfDom * phig

	PHIfxy = (1 - fg) * ySqrtY
	PHIfxyt2 = 2 * PHIfxy
	PHIgy = -f / y
	PHIgx2y = (2 * g + f - fg2) / y2
	PHIgy2 = (f + 0.5 * g - 0.5 * f2g) / y2

	greek1 = strikeStar * PHIfxy - fStar * (PHIgy + PHIfxy)
	greek2 = strikeStar * (2 * f + g - f2g) / y2 - fStar * (PHIgy + PHIfxyt2 + PHIgx2y)
	greek3 = strikeStar * (g + 0.5 * f - 0.5 * fg2) / y2 - fStar * PHIgy2
	greek4 = strikeStar * ((0.5 * fg - 2) * (2 * f + g - f2g) - g - 0.5 * f + fg2 + 0.5 * f2 * f) / y3 - fStar * (PHIgy + PHIfxyt2 + PHIgx2y + PHIgy2 +
	  2 * (-1.5 + 1.5 * fg + 0.5 * g2 * (1 - f2) + 0.5 * f2) / (sqrtY * y2) + ((0.5 * fg - 2) * (2 * g + f - g2 * f) - f - 0.5 * g + f2g + 0.5 * g2 * g) / y3)
	return  a1T * greek1 + a2T * greek2 + b0T * greek3 + b2T * greek4

def getImpliedVolatilityFromPrice(optionType, price, forward, strike, yf, dfDom):
    lowerBound = 0.0001
    upperBound = 1.5
    param = ParameterIV(optionType, price, forward, strike, dfDom, math.sqrt(yf))
    return findRoot(getDiffPrices, lowerBound, upperBound, param)

class ParameterIV:
	def __init__(self,optionType,price,forwardValue,strike,domesticDF,sqrtYf):
		self.optionType = optionType
		self.price = price
		self.forwardValue = forwardValue
		self.strike = strike
		self.domesticDF = domesticDF
		self.sqrtYf = sqrtYf

def getDiffPrices(x, context):
	return getBlackSpotPrice(context.forwardValue, context.strike, x * context.sqrtYf, context.domesticDF, context.optionType) - context.price


def getResultsWithV0(calibrationOutput, v0, size, kappa):
	results = np.zeros((5,1))
	results[0] = v0
	for i in range(size):
		results[i + 1] = calibrationOutput[i]

	if (size == 3):
		results[4] = kappa
	return results

def costFunctionLV(hestonParams, calibHelper, dimension) :
	expiries = calibHelper.expiries
	forwards = calibHelper.forwards
	dfs = calibHelper.dfs
	strikes = calibHelper.strikes
	mktVols = calibHelper.mktVols
	weights = calibHelper.weights
	nbExpiries = len(expiries)
	nbStrikesPerExp = len(strikes) / nbExpiries
	weightsIntg = gaussLaguerreWeights()
	abscissas = gaussLaguerreAbscissas()
	v0 = calibHelper.v0
	kappa = calibHelper.kappa

	sum = np.zeros((1,dimension))
	for i in range(nbExpiries): 
		time = expiries[i]
		df = dfs[i]
		forward = forwards[i]
		for j in range(nbStrikesPerExp): 
			index = i * nbStrikesPerExp + j
			strike = strikes[index]
			price = hestonVanillaPriceByGaussQuadrature(time, strike, forward, 1, df,  hestonParams[3] + kappa, hestonParams[1], hestonParams[2], hestonParams[0], v0, 1, abscissas, weightsIntg)
			sum[index] = weights[index] * (getImpliedVolatilityFromPrice(1, price, forward, strike, time, df) / mktVols[index] - 1)
		
	
	return sum

def hestonVanillaPriceByGaussQuadrature(time, strike, forward, spot, dfDom, kappa, sigma, theta, rho, v0, flavor, abscissas, weights):

	sigmaBS = math.sqrt((1 - math.exp(-kappa * time)) * (v0 - theta)  / (kappa * time) + theta)
	bsPrice = dfDom * getBlackForwardPrice(forward, strike, sigmaBS * math.sqrt(time), 1)
	hestParams = HestonParams(time, sigmaBS, kappa, sigma, theta, rho, v0, math.log(strike / forward))
	hPrice = math.sqrt(forward * strike) * dfDom * gaussLaguerreIntegrate(hestonIntegrand, hestParams, abscissas, weights) / math.pi()

	if (flavor == 1):
		return max(bsPrice + hPrice, 0.0)
	return  max(bsPrice + hPrice - dfDom * (forward - strike), 0.0)


def gaussLaguerreIntegrate(funct, context, abscissas, weights):
    sum = 0.0
    for i in range(len(abscissas)):
        sum += weights[i] * funct(abscissas[i], context)
    return sum

def hestonIntegrand(u, hestParams):
    z = Complex(u, -0.5)
    sigmaBS = hestParams.sigmaBS
    phiBS = cExp(cScale(-0.5 * sigmaBS * sigmaBS * hestParams.T, cAdd(cMult(z, z), Complex(-z.im, z.re))))
    phi = characFunction(z, hestParams.T, hestParams.kappa, hestParams.sigma, hestParams.theta, hestParams.rho, hestParams.v0)
    return cMult(cExp(Complex(0.0, -u * hestParams.logMoneyness)), cScale(1 / (u * u + 0.25), cSub(phiBS, phi))).re

def cExp(z):
    return Complex(math.exp(z.re) * math.cos(z.im), math.exp(z.re) * math.sin(z.im))

def cScale(scale,z):
    return Complex(scale * z.re, scale * z.im)

def cAdd(z1, z2):
    return Complex(z1.re + z2.re, z1.im + z2.im)

def cMult(z1, z2):
    return Complex(z1.re * z2.re - z1.im * z2.im, z1.im * z2.re + z1.re * z2.im)

def cSub(z1, z2):
    return Complex(z1.re - z2.re, z1.im - z2.im)

def cAddRealToComplex(z, d):
    res = Complex(z.re, z.im)
    res.re += d
    return res

def cSqrt(z):
    arg = cArg(z) * 0.5
    mod = math.sqrt(math.sqrt(z.re * z.re + z.im * z.im))
    return Complex(mod * math.cos(arg), mod * math.sin(arg))

def cArg(z):
    if (z.re > 0):
        return math.atan(z.im / z.re)
    if (z.re < 0 and z.im >= 0):
        return math.atan(z.im / z.re) + math.pi()
    if (z.re < 0 and z.im < 0):
        return math.atan(z.im / z.re) - math.pi()
    if (z.re == 0 and z.im > 0):
        return math.pi() * 0.5
    if (z.re == 0 and z.im < 0):
        return -math.pi() * 0.5
    return None


def characFunction(z, T, kappa, sigma, theta, rho, v0):
    sigma2 = sigma * sigma
    g = cAddRealToComplex(cScale(rho * sigma, Complex(z.im, -z.re)), kappa)
    D = cSqrt(cAdd(cMult(g, g), cScale(sigma2, cAdd(cMult(z, z), Complex(-z.im, z.re)))))
    gMinusD = cSub(g, D)
    G = cDiv(gMinusD, cAdd(g, D))
    exp1 = cExp(cScale(-T, D))
    gExpDt = cMult(G, exp1)
    OneMinusgExpDt = Complex(1 - gExpDt.re, -gExpDt.im)

    return cExp(cAdd(cScale(v0 / sigma2, cMult(cDiv(Complex(1 - exp1.re, -exp1.im), OneMinusgExpDt), gMinusD)),
				cScale(kappa * theta / sigma2, cSub(cScale(T, gMinusD), cScale(2, cLog(cDiv(OneMinusgExpDt, Complex(1 - G.re, -G.im))))))))



def cDiv(zNum, zDen):
    res = Complex()
    if (zDen.im == 0 and zDen.re == 0):
        res.re = None
        res.im = None
    if (abs(zDen.im) < abs(zDen.re)):
        scale = zDen.re + (zDen.im * zDen.im) / zDen.re
        res.re = (zNum.re + (zNum.im * zDen.im) / zDen.re) / scale
        res.im = (zNum.im - (zNum.re * zDen.im) / zDen.re) / scale
    else:
        scale = (zDen.re * zDen.re) / zDen.im + zDen.im
        res.re = (zNum.im + (zNum.re * zDen.re) / zDen.im) / scale
        res.im = ((zNum.im * zDen.re) / zDen.im - zNum.re) / scale

    return res



def cLog(z):
    return Complex(0.5 * math.log(z.re * z.re + z.im * z.im), cArg(z))

class Complex:
    def __init__(self):
        self.re = 0
        self.im = 0


class HestonParams:
    def __init__(self):
        self.T = 0.0
        self.sigmaBS = 0.0
        self.kappa = 0.0
        self.sigma = 0.0
        self.theta = 0.0
        self.rho = 0.0
        self.v0 = 0.0
        self.logMoneyness = 0.0


def gaussLaguerreAbscissas():
    abscissas  =  np.zeros((1,128))
    abscissas[0] = 484.61554398644364028
    abscissas[1] = 463.08003410944661482
    abscissas[2] = 445.74309697392811813
    abscissas[3] = 430.64344416659719172
    abscissas[4] = 417.02490297798891561
    abscissas[5] = 404.49472475051487663
    abscissas[6] = 392.81567124080805797
    abscissas[7] = 381.83044411906132609
    abscissas[8] = 371.42788921432764937
    abscissas[9] = 361.52572639232482743
    abscissas[10] = 352.06085354652594788
    abscissas[11] = 342.98350627382546918
    abscissas[12] = 334.25354206765388199
    abscissas[13] = 325.83797012119538294
    abscissas[14] = 317.70924895490594508
    abscissas[15] = 309.84407732661253476
    abscissas[16] = 302.22251324644946635
    abscissas[17] = 294.82731778764792807
    abscissas[18] = 287.64345689921947269
    abscissas[19] = 280.65771677632324099
    abscissas[20] = 273.85840246269384579
    abscissas[21] = 267.23509852895392669
    abscissas[22] = 260.77847677357971179
    abscissas[23] = 254.48014004486913109
    abscissas[24] = 248.33249416235719309
    abscissas[25] = 242.3286419497027282
    abscissas[26] = 236.46229485017778416
    abscissas[27] = 230.72769865820367841
    abscissas[28] = 225.11957068420900896
    abscissas[29] = 219.63304625557827876
    abscissas[30] = 214.26363289878787555
    abscissas[31] = 209.0071708855109307
    abscissas[32] = 203.85979908576987896
    abscissas[33] = 198.81792527372067525
    abscissas[34] = 193.87820019047296682
    abscissas[35] = 189.03749479395415278
    abscissas[36] = 184.29288022584682949
    abscissas[37] = 179.64161010586704492
    abscissas[38] = 175.08110482841465227
    abscissas[39] = 170.60893758924237318
    abscissas[40] = 166.22282191276897834
    abscissas[41] = 161.9206004859757968
    abscissas[42] = 157.70023513397813986
    abscissas[43] = 153.55979779656664164
    abscissas[44] = 149.49746238517781194
    abscissas[45] = 145.51149741665969373
    abscissas[46] = 141.60025933439314372
    abscissas[47] = 137.76218643933944463
    abscissas[48] = 133.99579336374816307
    abscissas[49] = 130.29966602891343541
    abscissas[50] = 126.67245703576024596
    abscissas[51] = 123.11288144336015193
    abscissas[52] = 119.61971289593208212
    abscissas[53] = 116.19178006355679145
    abscissas[54] = 112.8279633659042247
    abscissas[55] = 109.52719195177751033
    abscissas[56] = 106.28844091034535779
    abscissas[57] = 103.11072869259402296
    abscissas[58] = 99.993114723864223947
    abscissas[59] = 96.934697190381967857
    abscissas[60] = 93.934610984479675722
    abscissas[61] = 90.99202579479265296
    abscissas[62] = 88.106144329099493007
    abscissas[63] = 85.276200658715410441
    abscissas[64] = 82.501458674431376039
    abscissas[65] = 79.781210644968510337
    abscissas[66] = 77.114775869770582517
    abscissas[67] = 74.501499418734027813
    abscissas[68] = 71.940750952154374431
    abscissas[69] = 69.431923614783386256
    abscissas[70] = 66.974432998441457698
    abscissas[71] = 64.567716168121179976
    abscissas[72] = 62.211230746961376781
    abscissas[73] = 59.904454055872079721
    abscissas[74] = 57.646882303945176318
    abscissas[75] = 55.438029826117862342
    abscissas[76] = 53.277428364840766051
    abscissas[77] = 51.164626392776632713
    abscissas[78] = 49.099188473791016918
    abscissas[79] = 47.080694659717210016
    abscissas[80] = 45.108739920577249904
    abscissas[81] = 43.182933606120379011
    abscissas[82] = 41.302898936707123312
    abscissas[83] = 39.468272521715810797
    abscissas[84] = 37.678703903788353102
    abscissas[85] = 35.93385512735618903
    abscissas[86] = 34.233400330002211831
    abscissas[87] = 32.577025355323755207
    abscissas[88] = 30.964427386052790325
    abscissas[89] = 29.395314596284908504
    abscissas[90] = 27.869405821746426
    abscissas[91] = 26.386430247105263192
    abscissas[92] = 24.946127109403477107
    abscissas[93] = 23.548245416748891046
    abscissas[94] = 22.19254368146782852
    abscissas[95] = 20.878789666971350414
    abscissas[96] = 19.606760147641629999
    abscissas[97] = 18.376240681089694107
    abscissas[98] = 17.187025392181258354
    abscissas[99] = 16.038916768267057478
    abscissas[100] = 14.931725465091943761
    abscissas[101] = 13.865270122892054516
    abscissas[102] = 12.83937719222324958
    abscissas[103] = 11.853880769091839298
    abscissas[104] = 10.908622438990871473
    abscissas[105] = 10.003451129468258429
    abscissas[106] = 9.1382229708803901502
    abscissas[107] = 8.3128011650077695549
    abscissas[108] = 7.5270558612294067302
    abscissas[109] = 6.7808640399756159312
    abscissas[110] = 6.0741094031965232602
    abscissas[111] = 5.4066822716004825367
    abscissas[112] = 4.7784794884348382737
    abscissas[113] = 4.1894043295940042171
    abscissas[114] = 3.6393664198523794084
    abscissas[115] = 3.1282816550279117784
    abscissas[116] = 2.6560721298834737425
    abscissas[117] = 2.2226660715618824504
    abscissas[118] = 1.8279977783123382284
    abscissas[119] = 1.4720075631667286498
    abscissas[120] = 1.1546417019743908661
    abscissas[121] = 0.87585238454649816386
    abscissas[122] = 0.63559766578164322848
    abscissas[123] = 0.43384140755383476806
    abscissas[124] = 0.27055317875863965638
    abscissas[125] = 0.14570796659426421549
    abscissas[126] = 0.059284741269022160626
    abscissas[127] = 0.011251388263662889452
    return abscissas


def gaussLaguerreWeights():
    weights = np.zeros((1,128))
    weights[0] = 25.258065262116357275
    weights[1] = 18.906551250536754338
    weights[2] = 16.041733742401532936
    weights[3] = 14.274217908051513248
    weights[4] = 13.025508245772547511
    weights[5] = 12.073281458938208033
    weights[6] = 11.310526642692119381
    weights[7] = 10.67818359244368942
    weights[8] = 10.140485810084211238
    weights[9] = 9.6742632597146087647
    weights[10] = 9.2637165068808844381
    weights[11] = 8.8976283542327561094
    weights[12] = 8.5677707729826551031
    weights[13] = 8.267943590984030422
    weights[14] = 7.9933678354872252925
    weights[15] = 7.7402883033436102878
    weights[16] = 7.5057048110520110384
    weights[17] = 7.2871854415574839337
    weights[18] = 7.0827336620203151796
    weights[19] = 6.8906917895512540539
    weights[20] = 6.709669563091303246
    weights[21] = 6.5384904204498397462
    weights[22] = 6.3761504949746532489
    weights[23] = 6.2217869037019353229
    weights[24] = 6.0746529257832868609
    weights[25] = 5.9340983608172903629
    weights[26] = 5.7995538301817406435
    weights[27] = 5.6705181142772858038
    weights[28] = 5.5465478519565039051
    weights[29] = 5.4272490958220389601
    weights[30] = 5.3122703387172496292
    weights[31] = 5.2012967162404182275
    weights[32] = 5.0940451566110542814
    weights[33] = 4.9902602992458255926
    weights[34] = 4.8897110413004387652
    weights[35] = 4.7921876004651711156
    weights[36] = 4.697499004720838478
    weights[37] = 4.6054709371618551828
    weights[38] = 4.5159438777011198241
    weights[39] = 4.4287714941986067174
    weights[40] = 4.343819244179964123
    weights[41] = 4.2609631551175475295
    weights[42] = 4.1800887567761986219
    weights[43] = 4.1010901435837734397
    weights[44] = 4.0238691485890782928
    weights[45] = 3.9483346135610046801
    weights[46] = 3.8744017421796788092
    weights[47] = 3.801991525303647812
    weights[48] = 3.7310302289460088865
    weights[49] = 3.6614489369710478961
    weights[50] = 3.5931831416895181341
    weights[51] = 3.5261723764921750757
    weights[52] = 3.4603598854769819226
    weights[53] = 3.3956923257111482073
    weights[54] = 3.3321194983644759624
    weights[55] = 3.2695941054299533235
    weights[56] = 3.2080715291859349669
    weights[57] = 3.1475096319055748673
    weights[58] = 3.087868573636356917
    weights[59] = 3.0291106461389039062
    weights[60] = 2.9712001213002423583
    weights[61] = 2.9141031125411647196
    weights[62] = 2.8577874479129796725
    weights[63] = 2.8022225537168923282
    weights[64] = 2.747379347627825652
    weights[65] = 2.6932301404018081925
    weights[66] = 2.6397485453581444048
    weights[67] = 2.5869093949129906562
    weights[68] = 2.5346886635096423923
    weights[69] = 2.4830633963744275228
    weights[70] = 2.4320116435697620716
    weights[71] = 2.3815123988838537983
    weights[72] = 2.3315455431326768121
    weights[73] = 2.2820917914995448861
    weights[74] = 2.2331326445662367242
    weights[75] = 2.1846503427314409862
    weights[76] = 2.1366278237348295121
    weights[77] = 2.0890486830341905566
    weights[78] = 2.0418971368071119343
    weights[79] = 1.9951579873673115362
    weights[80] = 1.9488165908071333199
    weights[81] = 1.9028588266908910143
    weights[82] = 1.8572710696473515579
    weights[83] = 1.8120401627075197748
    weights[84] = 1.7671533922681279538
    weights[85] = 1.7225984645498078063
    weights[86] = 1.6783634834466170105
    weights[87] = 1.6344369296613174836
    weights[88] = 1.5908076410381992716
    weights[89] = 1.5474647940006300839
    weights[90] = 1.504397886024419817
    weights[91] = 1.4615967190643281981
    weights[92] = 1.4190513838756071419
    weights[93] = 1.3767522451619427226
    weights[94] = 1.3346899274979950878
    weights[95] = 1.2928553019702917481
    weights[96] = 1.2512394734889966674
    weights[97] = 1.209833768725666836
    weights[98] = 1.1686297246324710564
    weights[99] = 1.1276190775078043238
    weights[100] = 1.0867937525678863508
    weights[101] = 1.0461458539923151889
    weights[102] = 1.005667655412371797
    weights[103] = 0.96535159081182952967
    weights[104] = 0.92519024581214781566
    weights[105] = 0.88517634931802535725
    weights[106] = 0.84530276549780858364
    weights[107] = 0.80556248607572644715
    weights[108] = 0.76594862291772236595
    weights[109] = 0.72645440088604273932
    weights[110] = 0.68707315095090681911
    weights[111] = 0.64779830353558975897
    weights[112] = 0.60862338208432464892
    weights[113] = 0.56954199683809647592
    weights[114] = 0.53054783880766120951
    weights[115] = 0.49163467393863402588
    weights[116] = 0.45279633747266839761
    weights[117] = 0.41402672852483812793
    weights[118] = 0.37531980493875832794
    weights[119] = 0.33666957856955609385
    weights[120] = 0.29807011138272609951
    weights[121] = 0.25951551341155237873
    weights[122] = 0.22099994569917963405
    weights[123] = 0.18251763897077086241
    weights[124] = 0.14406297271813597871
    weights[125] = 0.10563085860984439135
    weights[126] = 0.067219473590110864758
    weights[127] = 0.028874906380275778411
    return weights

def LevenbergMarquardt(func, x0, context, numberOfParameters, dimension, lower, upper):
    maxIterations = 1000 # maximum number of iterations
    minLambda = 1e-6 # minimum lambda allowed
    maxLambda = 1e6 # maximum lambda allowed
    eps1 = 1e-15 # convergence tolerance for objective function
    eps2 = 1e-10 # convergence tolerance for gradient
    delta = 1e-3 # finite difference shift

    f = func(x0, context, dimension)
    F = np.linalg.norm(f)
    if(F <= eps1):
        return x0

    jacobian = computeJacobian(func, x0, context, dimension, numberOfParameters, delta)
    jacobianTranspose = transpose(jacobian, numberOfParameters, dimension)
    B = multipyMtxByVector(jacobianTranspose, f, dimension, numberOfParameters)
    normGrad = computeNormInf(B)

    h = np.zeros((1,numberOfParameters))
    F_try = F
    iteration = 1
    L = 0.01

    while( (F > eps1 and normGrad > eps2 ) and iteration <= maxIterations ):
        lmHessian = lmHessian(jacobianTranspose, jacobian, L, numberOfParameters, dimension)

        #solve the system A*X=B
        solverLU(lmHessian, B, h)
        x_try = diffVectors(x0, h, numberOfParameters)
        applyConstraints(x_try, lower, upper)
        # Evaluate the total distance error at the updated parameters
        f_try = func(x_try, context, dimension)
        F_try = np.linalg.norm(f_try)
        # If the total distance error of the updated parameters is less than the previous one
        #then makes the updated parameters to be the current parameters and decreases the value of the damping factor
        if (F_try < F ):
            L = max(L/10, minLambda)
            copyArray(x0, x_try, numberOfParameters)
            jacobian = computeJacobian(func, x0, context, dimension, numberOfParameters, delta)
            jacobianTranspose = transpose(jacobian, numberOfParameters, dimension)
            B = multipyMtxByVector(jacobianTranspose, f_try, dimension, numberOfParameters)
            normGrad = computeNormInf(B)
            F = F_try

        else: # Otherwise increases the value of the damping factor
            L = min(L*10, maxLambda)

        iteration +=1

    

    return x0

def computeJacobian(func, x0, context, dimension, numberOfParameters, deltaX):
    jacobian = np.zeros((dimension, numberOfParameters))
    factor = 1/(2 * deltaX)
    for j in range( numberOfParameters):
        left = applyShift(x0, -deltaX, j, numberOfParameters)
        right = applyShift(x0, deltaX, j, numberOfParameters)
        partDerj = diffVectors(func(right, context, dimension), func(left, context, dimension), dimension)
        for i in range( dimension):
            jacobian[i][j] = partDerj[i] * factor

    return jacobian