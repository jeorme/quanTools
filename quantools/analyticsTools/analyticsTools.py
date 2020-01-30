import QuantLib as ql


def yearFraction(startDate,endDate,basis):
    if basis == "ACT/365.FIXED":
        day_count =  ql.Actual365Fixed()
    if basis == "ACT/360":
        day_count= ql.Actual360()
    if basis == "30/360":
        day_count = ql.Thirty360()
    if basis == "ACT/ACT":
        day_count = ql.ActualActual()
    if basis == "BUS252":
        day_count = ql.Business252()
    if basis == "ACT29EXC":
        day_count = ql.Actual365NoLeap()
    else:
        day_count = ql.Actual365Fixed()
    return day_count.yearFraction(startDate,endDate)




