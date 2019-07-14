import os.path
from utility import *
from cpNet import *
from random import *
from math import *

class Database:
	# filename = name of file, nbV = number of variables, lb = lambda (number of edges), nbP = number of parents, nbO = number of objects, nbN = number of different scores, rand: true = generate random cp-net and false = use a (random) dataset, useFile: true = use an existent file and false = generate a random dataset
	def __init__(self,filename,p,nbV = -1,lb = -1,nbP = -1,nbO = -1, nbA = -1, nbN = -1,rand = False,useFile = True):
		if not rand:
			if useFile:
				data = []
				file = open(filename,"r")
				for line in file:
					temp = []
					lineTab = line[:-1].split(" ")
					if len(data) == 0:
						self.numberOfAttributes = len(lineTab) - 1
					for elt in lineTab:
						temp.append(int(elt))
					data.append(temp)
				file.close()
			else:
				data = self.randomGeneration(nbO,nbA,nbN)
				self.numberOfAttributes = len(data[0])-1
			
			self.data = []
			for i in range(len(data)-1):
				for j in range(i+1,len(data)):
					fVar = isASwap(data[i],data[j])
					if fVar != -1 and data[i][-1] != data[j][-1]:
						if data[i][-1] > data[j][-1]:
							self.data.append([data[i][:-1],data[j][:-1],fVar])
						else:
							self.data.append([data[j][:-1],data[i][:-1],fVar])
					
			self.numberOfObjects = len(data)
		
		else:
			self.numberOfAttributes = nbV
			self.data = []
			self.dataTr = []
			self.dataTe = []
			N = CPNet(name = "N2", random = rand,nbVar = nbV,lbd = lb,nbMaxParents = nbP)
			
			# N.displayCPNetInfo()
			
			while len(self.data) < nbO:
				outcome = fromIntToBin(randint(0,(2**nbV)-1),nbV)
				flipOutcome = list(outcome)
				varAl = randint(0,nbV-1)
				flipOutcome[varAl] = not flipOutcome[varAl]
				var = N.getVariable(varAl)
				par = []
				for k in var.parents:
					par.append(outcome[k.id])
				if N.preferred([var.id,fromBinToInt(par),outcome[var.id]]):
					nombreRand = randint(1,100)
					if nombreRand > p:
						self.data.append([outcome,flipOutcome,var.id])
						if len(self.dataTr) < 0.75*nbO:
							self.dataTr.append([outcome,flipOutcome,var.id])
						else:
							self.dataTe.append([outcome,flipOutcome,var.id])
					else:
						self.data.append([flipOutcome,outcome,var.id])
						if len(self.dataTr) < 0.75*nbO:
							self.dataTr.append([flipOutcome,outcome,var.id])
						else:
							self.dataTe.append([flipOutcome,outcome,var.id])
			self.numberOfObjects = len(self.data)
						
	def randomGeneration(self,nbOfObjects,nbOfA,nbOfNotes):
		if nbOfA == -1:
			nbOfAttributes = ceil(log(nbOfObjects,2)) + 1
		else:
			nbOfAttributes = nbOfA
		listOfObjects = []
		data = []

		while len(listOfObjects) < nbOfObjects:
			objectNumber,flipObjectNumber = self.newObject(nbOfAttributes)
			while objectNumber in listOfObjects or flipObjectNumber in listOfObjects:
				objectNumber,flipObjectNumber = self.newObject(nbOfAttributes)
			object = fromIntToBin(objectNumber,nbOfAttributes)
			flipObject = fromIntToBin(flipObjectNumber,nbOfAttributes)
			object.append(randint(1,nbOfNotes))
			flipObject.append(randint(1,nbOfNotes))
			data.extend([object,flipObject])
			listOfObjects.extend([objectNumber,flipObjectNumber])
		return data
	
	def newObject(self,length):
		number = 0
		for i in range(length):
			if randint(0,1) % 2:
				number += 2**i
		flipValue = randint(0,length - 1)
		vector = fromIntToBin(number,length)
		flipVector = list(vector)
		flipVector[flipValue] = not flipVector[flipValue]
			
		return number,fromBinToInt(flipVector)
	
	# return True if there exist a swap couple with a different value of parent variable
	def findSwapOutcomes(self,curVarId,curVarVal,parVarId,parVarVal):
		for swap in self.data:
			if swap[2] == curVarId and swap[0][curVarId] == curVarVal and swap[0][parVarId] == parVarVal:
				return True
		return False

	# equivalence query
	def EQ(self,N,listOfViolatedRules):
		trueSwap = 0
		falseSwap = 0
		indifferentSwap = 0
		shuffle(self.data)
		for swap in self.data:
			rule = N.returnRule(N.getVariable(swap[2]),swap[0],swap[1])
			if N.preferred(rule):
				trueSwap += 1
			else:
				if N.preferred([rule[0],rule[1],not rule[2]]):
					falseSwap += 1
				else:
					indifferentSwap += 1
			if not N.preferred(rule) and not searchRule(rule,listOfViolatedRules):
				return False,swap[0],swap[1],rule,-1,-1,-1
		return True,-1,-1,-1,trueSwap,falseSwap,indifferentSwap
		
	def EQTr(self,N,listOfViolatedRules):
		trueSwap = 0
		falseSwap = 0
		indifferentSwap = 0
		shuffle(self.data)
		for swap in self.dataTr:
			rule = N.returnRule(N.getVariable(swap[2]),swap[0],swap[1])
			if N.preferred(rule):
				trueSwap += 1
			else:
				if N.preferred([rule[0],rule[1],not rule[2]]):
					falseSwap += 1
				else:
					indifferentSwap += 1
			if not N.preferred(rule) and not searchRule(rule,listOfViolatedRules):
				return False,swap[0],swap[1],rule,-1,-1,-1
		return True,-1,-1,-1,trueSwap,falseSwap,indifferentSwap
		
	def EQTe(self,N,listOfViolatedRules):
		trueSwap = 0
		falseSwap = 0
		indifferentSwap = 0
		shuffle(self.data)
		for swap in self.dataTe:
			rule = N.returnRule(N.getVariable(swap[2]),swap[0],swap[1])
			if N.preferred(rule):
				trueSwap += 1
			else:
				if N.preferred([rule[0],rule[1],not rule[2]]):
					falseSwap += 1
				else:
					indifferentSwap += 1
			if not N.preferred(rule) and not searchRule(rule,listOfViolatedRules):
				return False,swap[0],swap[1],rule,-1,-1,-1
		return True,-1,-1,-1,trueSwap,falseSwap,indifferentSwap
		
	def completeParent(self,p,v,fvp,fvv):
		numberOfViolate = 0
		for swap in self.data:
		# for swap in self.dataTr:
				if swap[2] == v and ((swap[0][p] == fvp and swap[0][v] != fvv) or (swap[0][p] == (not fvp) and swap[0][v] != (not fvv))):
					numberOfViolate += 1
		return numberOfViolate
