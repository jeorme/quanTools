from calendar import isleap
from datetime import datetime


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
    if basis == "30/360":
        return getNbDays30(startDate, endDate) / 360
    if basis == "30/365":
        return getNbDays30(startDate, endDate) / 365
    if basis == "30E/360":
        return getNbDaysBasis30E(startDate, endDate) / 360
    if basis == "ACT/ACT":
        return yearFractionACTACT(startDate, endDate)

    return (endDate - startDate).days / 365


def getBasis():
    """
    return the list of basis used for the year fraction
    """
    return ["ACT/365.FIXED","ACT/365.25","ACT/360","ACT/364","ACT/366","BEG29","30/360","30E/360","ACT/ACT","30/365"]

def getNbDays30(startDate,endDate):
    day_begin = startDate.day
    day_end = endDate.day
    if (day_begin == 31):
        day_begin = 30
    if ((day_end == 31) and (day_begin == 30)):
        day_end = 30

    return ((endDate.year - startDate.year) * 360) + ((endDate.month - startDate.month) * 30) + (
            day_end - day_begin)

def getNbDaysBasis30E(startDate, endDate):
    return ((endDate.year - startDate.year) * 360) + ((endDate.month - startDate.month) * 30) + (min(endDate.day, 30) - min(startDate.day, 30) )

def yearFractionACTACT(startDate, endDate):
    year_end = endDate.year
    year_begin = startDate.year
    count_start = 366 if isleap(year_begin) else 365
    if (year_end == year_begin):
        return (endDate - startDate).days / count_start
    count_end = 366 if isleap(year_end) else 365
    endFirstYear = datetime(year=year_begin + 1, month=1, day=1)
    endLastYear = datetime(year=year_end, month=1, day=1)
    return ((endFirstYear - startDate).days / (count_start) + (endDate - endLastYear).days / (count_end) + (year_end - year_begin - 1))
