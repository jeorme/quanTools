
def newtonSolver1D(target, initialPoint, tolerance, maxNbIteration, function, argument1, argument2, argument3):
    f0 = function(initialPoint, argument1, argument2, argument3)
    epsilon = 0.00001
    for k in range(maxNbIteration+1):
        f1 = function(initialPoint + epsilon, argument1, argument2, argument3)
        df =(f1 - f0) / epsilon
        if (df == 0.0):
            return -1
        xkPlus1 = initialPoint + (target - f0) / df
        fkPlus1 = function(xkPlus1, argument1, argument2, argument3)
        if (abs(xkPlus1 - initialPoint) < tolerance):
            return xkPlus1
        initialPoint = xkPlus1
        f0 = fkPlus1

    return -1


def findRoot(function, lowerBound, upperBound, context):
    tolerance = pow(10,-6)
    floatEpsilon = pow(10,-6)
    maxIterations =100
    d    = 0
    e    = 0
    min1 = 0
    min2 = 0
    fc   = 0
    p    = 0
    q    = 0
    r    = 0
    s    = 0
    tol1 = 0
    xm   = 0
    a  = lowerBound
    b  = upperBound
    c  = upperBound
    fa = function(a, context)
    fb = function(b, context)

    #check that bounds definitely include solution
    if ((fa > 0 and fb > 0) or (fa < 0) and (fb < 0)):
        return -1

    # Attempt to find the solution
    fc = fb
    for i in range( maxIterations):
        if ((fb > 0 and fc > 0) or (fb < 0 and fc < 0)):
            c = a
            fc = fa
            d  = (b - a)
            e = d

        if (abs(fc) < abs(fb)):
            a  = b
            b  = c
            c  = a
            fa = fb
            fb = fc
            fc = fa


        # Convergence check
        tol1 = 2 * floatEpsilon * abs(b) + (0.5 * tolerance)
        xm = 0.5 * (c - b)
        if abs(xm) <= tol1 or fb == 0.0:
            return b

    # Attempt inverse quadratic interpolation
        if ((abs(e) >= tol1) and (abs(fa) > abs(fb))):
            s = fb / fa
            if (a == c):
                p = 2 * xm * s
                q = 1 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * ((2 * xm * q * (q - r)) - ((b - a) * (r - 1)))
                q = (q - 1) * (r - 1) * (s - 1)

            # Check bounds
            if (p > 0):
                q = -q

            p = abs(p)
            min1 = (3 * xm * q) - abs(tol1 * q)
            min2 = abs(e * q)
            if (2 * p < min(min1, min2)):# Accept interpolation
                e = d
                d = p / q
            else:#Interpolation failed, use bisection
                d = xm
                e = d

        else:# Bounds decreasing too slowly, use bisection
            d = xm
            e = d

        # Move last best guess to a
        a = b
        fa = fb
        if (abs(d) > tol1):
            b = b + d
        else:
            if (xm >= 0):
                b = b + abs(tol1)
            else:
                b = b - abs(tol1)

        fb = function(b, context)

    return -1
