from calendar import isleap

def yearFraction(startDate,endDate,basis):
    """
    compute the yearfraction
    """
    if basis == "ACT/365.FIXED":
        return  (endDate - startDate).days/365
    if basis == "ACT/360":
        return  (endDate - startDate).days/360
    if basis == "ACT/365.25":
        return (endDate - startDate).days / 365.25
    if basis == "ACT/364":
        return (endDate - startDate).days/ 364
    if basis == "ACT/366":
        return (endDate - startDate).days/ 366
    if basis == "BEG29":
        basis = 365
        if isleap(startDate.year):
            basis =  366
        return (endDate - startDate).days / basis

    return (endDate - startDate).days / 365


def getBasis():
    """
    return the list of basis used for the year fraction
    """
    return ["ACT/365.FIXED","ACT/365.25","ACT/360","ACT/364","ACT/366","BEG29"]

