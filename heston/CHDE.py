import numpy as np

def CHDEminimisation(nbParam, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput):
	bestSolution = CHDEminimisationBestSolution(nbParam, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput)
	return objectiveFunction(bestSolution, otherInput)


def CHDEminimisationBestSolution(nbParam, maxGen, cr, F, d, upper, lower, objectiveFunction, otherInput):
	uG1 = np.zeros((d,1))

	# Creation of a random initial population
	xG = initializePopulation(upper, lower, nbParam, d)

	#Compute the values of the objective function for the generation g
	fG = evaluateFunction(xG, objectiveFunction, otherInput, nbParam)

	for g in range( maxGen):

		for i in range( nbParam):
		#select randomly r1, r2 and r3
			r1 = np.random.randint(0,nbParam)
			r2 = np.random.randint(0,nbParam)
			r3 = np.random.randint(0,nbParam)
			while (r1 == i):
				r1 = np.random.randint(0,nbParam)

			while (r2 == i or r2 == r1):
				r2 = np.random.randint(0,nbParam)

			while (r3 == i or r3 == r1 or r3 == r2):
				r3 = np.random.randint(0,nbParam)



		jrand = np.random.randint(0, d)

		for j in range(d):
			child = 0.0
			if (np.random.random()< cr or j == jrand):
				child = xG[r3][j] + F * (xG[r1][j] - xG[r2][j])
			else:
				child = xG[i][j]

			uG1[j] = rangeKeeperByReflection(child, lower[j], upper[j])


# compute the value of the  objective function for i 
		fU_i = objectiveFunction(uG1, otherInput)
		if (compareSolutionsTDSC(fG[i], fU_i, 0 , xG[i,:], uG1) == 1):
			xG[i,:] = uG1.reshape((4))
			fG[i] = fU_i

	return bestSolution(xG, bestPosition(xG, objectiveFunction, otherInput, nbParam), d)

def evaluateFunction(population, objectiveFunction, otherInput, nbParam):
	fG = np.zeros(nbParam)
	for i in range(nbParam):
		fG[i] = objectiveFunction(population[i], otherInput)
	return fG

def initializePopulation(upper, lower, nbParam, d):
	population =  np.zeros((nbParam, d))
	for j in range(d):
		lowerJ = lower[j]
		upperJ = upper[j]
		for i in range(nbParam):
			population[i][j] = np.random.uniform(lowerJ, upperJ)

	return population



def rangeKeeperByReflection(child, lowerBound, upperBound):
	width = upperBound - lowerBound
	if (child < lowerBound):
		return lowerBound + (lowerBound - child) % width
	if (child > upperBound):
		return upperBound - (child - upperBound)% width
	return child





def compareSolutionsTDSC(fitnessValue1, fitnessValue2, verifyConstraint, individual1, individual2 ):

	# case 1 : the two solutions are feasible
	if(fitnessValue2 < fitnessValue1):
		return 1    # solution 2 is better than solution 1

	return 0 # solution 1 is better than solution for all the other cases



def bestSolution(population, position, d):
	solution = np.zeros((d,1))
	for i in range(population.shape[1]):
		solution[i] = population[position][i]
	return solution


def bestPosition(population, objectiveFunction, otherInput, nbParam):
	return minVector(evaluateFunction(population, objectiveFunction, otherInput, nbParam))


def minVector(vector):
	minValue =  vector[0]
	minIndex = 0
	for i in range(len(vector)):
		if (vector[i] < minValue):
			minValue =  vector[i]
			minIndex = i
	return minIndex


