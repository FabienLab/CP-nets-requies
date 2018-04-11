import math as m

def fromIntToBin(number,numberOfBits):
	binaryVect = [0 for i in range(numberOfBits)]
	while number > 0:
		binaryVect[numberOfBits -1 -m.floor(m.log(number,2))] = 1
		number -= 2**(m.floor(m.log(number,2)))
	return binaryVect
	
def fromBinToInt(binaryVect):
	number = 0
	for i in range(len(binaryVect)-1,-1,-1):
		if binaryVect[i]:
			number += 2**(len(binaryVect) -1 -i)
	return number
	
def flipVariable(outcome1,outcome2):
	for i in range(len(outcome1)):
		if outcome1[i] != outcome2[i]:
			return i
	return -1
	
def VarDoesntChange(varId,listParentsId,length):
	listPossibleParents = []
	for i in range(length):
		if i != varId and not i in listParentsId:
			listPossibleParents.append(i)
	return listPossibleParents
	
def flipState(state,varId):
	fState = list(state)
	fState[varId] = not fState[varId]
	return fState

def existElt(elt,listParents,varId,flip):
	for parent in listParents.keys():
		if elt[parent] != listParents[parent]:
			return False
	if (elt[varId] and not flip) or (not elt[varId] and flip):
		return True
	return False
	
def setOfParentsValue(state,listOfParentsId):
	listOfParentsValue = {}
	for i,id in enumerate(listOfParentsId):
		listOfParentsValue[id] = state[i]
	return listOfParentsValue
	
# return id of swap variable iff (outcome1,outcome2) is a swap, return -1 else
def isASwap(outcome1,outcome2):
	cpt = 0
	swapId = -1
	for i in range(len(outcome1)-1):
		if outcome1[i] != outcome2[i]:
			cpt += 1
			swapId = i
		if cpt > 1:
			return -1
	return swapId
	
def searchRule(rule,listOfViolatedRules):
	if rule[0] in listOfViolatedRules and rule[1] in listOfViolatedRules[rule[0]] and listOfViolatedRules[rule[0]][rule[1]] == rule[2]:
		return True
	return False
