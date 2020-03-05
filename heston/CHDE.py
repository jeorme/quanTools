import numpy as np
def CHDEminimisation(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput):
	bestSolution = CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput)
	return objectiveFunction(bestSolution, otherInput)


def CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput):
	uG1 = np.zeros((1,d))

	# Creation of a random initial population
	xG = initializePopulation(upper, lower, np, d)

	#Compute the values of the objective function for the generation g
	fG = evaluateFunction(xG, objectiveFunction, otherInput, np)

	for g in range( maxGen):

		for i in range( np):
		#select randomly r1, r2 and r3
			r1 = np.random.randint(0,np)
			r2 = np.random.randint(0,np)
			r3 = np.random.randint(0,np)
			while (r1 == i):
				r1 = np.random.randint(0,np)

			while (r2 == i or r2 == r1):
				r2 = np.random.randint(0,np)

			while (r3 == i or r3 == r1 or r3 == r2):
				r3 = np.random.randint(0,np)



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
		if (compareSolutionsTDSC(fG[i], fU_i, verifyConstraint, xG[i,:], uG1) == 1):
			replaceMatrixLine_V(xG, uG1, i)
			fG[i] = fU_i
	return bestSolution(xG, bestPosition(xG, objectiveFunction, otherInput, np), d)


def replaceMatrixLine_V(M, vect, pos):
	for i in range(M.shape[0]):
		M[pos][i]= vect[i]


def evaluateFunction(population, objectiveFunction, otherInput, np):
	fG = np.zeros(np)
	for i in range(np):
		fG[i] = objectiveFunction(population[i], otherInput)
	return fG

def initializePopulation(upper, lower, np, d):
	population =  np.zeros((np, d))
	for j in range(d):
		lowerJ = lower[j]
		upperJ = upper[j]
		for i in range(np):
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
	feasible1 = verifyConstraint(individual1)
	feasible2 = verifyConstraint(individual2)

	# case 1 : the two solutions are feasible
	if(feasible1 == 0 and feasible2 == 0 and fitnessValue2 < fitnessValue1):
		return 1    # solution 2 is better than solution 1
	
	# case 2 : if one solution is feasible and the other is unfeasible, the feasible solution wins
	if(feasible2 == 0 and feasible1 > 0):
		return 1  # solution 2 is better than solution 1

	# case 3 : if both solutions are infeasible, the one with the lowest of sum of constraints is prefered
	if(feasible1 > 0 and feasible2 > 0 and feasible2 <= feasible1 ):
		return 1  # solution 2 is better than solution 1

	return 0 # solution 1 is better than solution for all the other cases






def bestSolution(population, position, d):
	solution = np.zeros((1,d))
	for i in range(population.shape[0]):
		solution[i] = population[position][i]
	return solution


def bestPosition(population, objectiveFunction, otherInput, np):
	return minVector(evaluateFunction(population, objectiveFunction, otherInput, np))


def minVector(vector):
	minValue =  vector[0]
	minIndex = 0
	for i in range(len(vector)):
		if (vector[i] < minValue):
			minValue =  vector[i]
			minIndex = i
	return minIndex


