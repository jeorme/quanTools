
def binary_search(vector, Search_Term):
    n = len(vector)
    if n== 0:
        return 0
    low = 0
    while(n-low>1):
        index = int((n+low)/2)
        if Search_Term < vector[index]:
            n = index
        else:
            low = index
    return -1 if vector[low] > Search_Term else low


def pointFloorIndex(list, point):
	if list[len(list)-1] < point:
		return -2
	return binary_search(list, point)


def getIndexBefore(pointFloorIndex, listLength):
	if pointFloorIndex == -1:
		return 0
	if pointFloorIndex == -2:
		return max(0, listLength - 2)
	return pointFloorIndex