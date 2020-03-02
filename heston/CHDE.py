def CHDEminimisation(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput) {
	def bestSolution = CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput)
	return objectiveFunction(bestSolution, otherInput)
}

def CHDEminimisationBestSolution(np, maxGen, cr, F, d, upper, lower, objectiveFunction, verifyConstraint, otherInput) {


def uG1 =


array(d)

// Creation
of
a
random
initial
population


def xG =


initializePopulation(upper, lower, np, d)

// Compute
the
values
of
the
objective
function
for the generation g


def fG =


evaluateFunction(xG, objectiveFunction, otherInput, np)

for (


    def g =


0;
g < maxGen;
g + +) {

for (


    def i =


0;
i < np;
i + +) {

// select
randomly
r1, r2 and r3


def r1 =


intRand(0, np)


def r2 =


intRand(0, np)


def r3 =


intRand(0, np)

while (r1 == i) {
r1 = intRand(0, np)
}
while (r2 == i | | r2 == r1) {
r2 = intRand(0, np)
}
while (r3 == i | | r3 == r1 | | r3 == r2) {
r3 = intRand(0, np)
}


def jrand =


intRand(0, d)

for (


    def j =


0;
j < d;
j + +) {


def child =


0.0
if (floatRand() < cr | | j == jrand)
    child = xG[r3][j] + F * (xG[r1][j] - xG[r2][j])
else
    child = xG[i][j]

uG1[j] = rangeKeeperByReflection(child, lower[j], upper[j])
}

// compute
the
value
of
the
objective
function
for i


    def fU_i =


objectiveFunction(uG1, otherInput)
if (compareSolutionsTDSC(fG[i], fU_i, verifyConstraint, matrixLine(xG, i), uG1) == 1) {
replaceMatrixLine_V(xG, uG1, i)
fG[i] = fU_i
}
}
}
return bestSolution(xG, bestPosition(xG, objectiveFunction, otherInput, np), d)

}

def evaluateFunction(population, objectiveFunction, otherInput, np){
	def fG = array(np)
	for (def i = 0; i < np; i++)
		fG[i] = objectiveFunction(matrixLine(population, i), otherInput)
	return fG

}

def compareSolutionsTDSC(fitnessValue1, fitnessValue2, verifyConstraint, individual1, individual2 ){

	def feasible1 = verifyConstraint(individual1)
	def feasible2 = verifyConstraint(individual2)

	// case 1 : the two solutions are feasible
	if(feasible1 == 0 && feasible2 == 0 && fitnessValue2 < fitnessValue1){
		return 1    // solution 2 is better than solution 1
	}
	// case 2 : if one solution is feasible and the other is unfeasible, the feasible solution wins
	if(feasible2 == 0 && feasible1 > 0)
		return 1  // solution 2 is better than solution 1

	// case 3 : if both solutions are infeasible, the one with the lowest of sum of constraints is prefered
	if(feasible1 > 0 && feasible2 > 0 && feasible2 <= feasible1 )
		return 1  // solution 2 is better than solution 1

	return 0 // solution 1 is better than solution for all the other cases
}

def initializePopulation(upper, lower, np, d){
	def population =  matrix(np, d)
	for (def j= 0; j < d; j++) {
		def lowerJ = lower[j]
		def upperJ = upper[j]
		for(def i = 0; i < np; i++)
			population[i][j] = floatRandBound(lowerJ, upperJ)
	}
	return population
}


ef replaceMatrixLine_V(M, vect, pos){
	for (def i = 0; i < width(M); i++)
		M[pos][i]= vect[i]
}


def bestSolution(population, position, d){
	def solution = array(d)
	for(def i = 0; i< width(population); i++)
		solution[i] = population[position][i]
	return solution
}

def bestPosition(population, objectiveFunction, otherInput, np){
	return minVector(evaluateFunction(population, objectiveFunction, otherInput, np))
}

def minVector(vector){
	def minValue =  vector[0]
	def minIndex = 0
	for (def i = 1; i < length(vector); i++){
		if (vector[i] < minValue){
			minValue =  vector[i]
			minIndex = i
		}
	}
	return minIndex
}

def floatRandBound(lowerBound, upperBound){
	return lowerBound + (upperBound - lowerBound) * floatRand()
}

def rangeKeeperByReflection(child, lowerBound, upperBound){
	def width = upperBound - lowerBound
	if (child < lowerBound)
		return lowerBound + mod(lowerBound - child, width)
	if (child > upperBound)
		return upperBound - mod(child - upperBound, width)
	return child
}

def verifyConstraints(x){
	return 0.0
}
