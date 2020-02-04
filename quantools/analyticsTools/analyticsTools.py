
def yearFraction(startDate,endDate,basis):
    if basis == "ACT/365.FIXED":
        return  (endDate - startDate).days/365
    if basis == "ACT/360":
        return  (endDate - startDate).days/360
    if basis == "ACT/365.25":
        return (endDate - startDate).days / 365.25
    if basis == "ACT/364":
        return (endDate - startDate).days/ 364

    return (endDate - startDate).days / 365




