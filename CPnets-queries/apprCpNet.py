from cpNet import *
from database import *
import time
from random import *
from math import *

def searchParent(N,dataset,outcome,flipOutcome,rule,var,autorizedCycle):
	# list of variables V such that o[V] = o'[v]
	listOfParentsPretender = VarDoesntChange(var.id,var.parentsId(),len(outcome))

	oldPref = var.preferences
	
	l = []
	
	for parId in listOfParentsPretender:
		par = N.getVariable(parId)
		N.addParentVariables(var,[par])
		
		if (autorizedCycle or not N.cycle()) and dataset.findSwapOutcomes(rule[0],int(not rule[2]),parId,int(not flipOutcome[parId])):
			l.append(parId)
		N.deleteParentVariables(var,[par])
			
	if len(l) != 0:
	
		listOfParentsPretender2Pass = [0] * len(l)
		
		for i in range(len(l)):
			listOfParentsPretender2Pass[i] = dataset.completeParent(l[i],var.id,outcome[l[i]],outcome[var.id])
				
		listOfParentsPretender3Pass = []
		min = float('inf')	
		for i,nb in enumerate(listOfParentsPretender2Pass):
			if nb < min:
				min = nb
				listOfParentsPretender3Pass = [l[i]]
			if nb == min:
				listOfParentsPretender3Pass.append(l[i])
		x = randint(0,len(listOfParentsPretender3Pass)-1)
		N.addParentVariables(var,[N.getVariable(listOfParentsPretender3Pass[x])])
		return N.getVariable(listOfParentsPretender3Pass[x])		
	else:
		var.preferences = oldPref
		return Variable()
	

	
	
	
def learningCPNet(fileName,v,b,numberOfParents1,numberOfParents2,smooth,smooth2,random,autorizedCycle,o,a,n,useRandomDataset,convergence,trte,prob):

	minAccuracy = 101
	maxAccuracy = -1
	minT = float('inf')
	maxT = -1
	averageAccuracy = 0
	averageIndifferenceAccuracy = 0
	averageSwap = 0
	averageTrueSwap = 0
	averageFalseSwap = 0
	averageIndifferentSwap = 0
	
	temps = []
	acc = []
	
	timeSmooth = 0
	
	convergenceAccuracy = []
	
	for i in range(smooth):

		dataset = Database(filename = fileName,p = prob,nbV = v,lb = b,nbP = numberOfParents1,nbO = o,nbA = a, nbN = n,rand = random,useFile = useRandomDataset)
		# flush(dataset)
		print("generation done")
		for j in range(smooth2):
		
			N = CPNet(name = "N", empty = True,random = False)
			N.addVariables(numberOfVariables = dataset.numberOfAttributes)
			listOfViolatedRules = {}
			cpt = 1
			
			timeBefore = time.clock()
			
			# let outcome = o and flipOutcome = o'
			if trte:
				equivalent,outcome,flipOutcome,rule,trueSwap,falseSwap,indifferentSwap = dataset.EQTr(N,listOfViolatedRules)
			else:
				equivalent,outcome,flipOutcome,rule,trueSwap,falseSwap,indifferentSwap = dataset.EQ(N,listOfViolatedRules)
			
			cpt = 0
			
			while not equivalent:
				# print("Etape",cpt,":")
				# print(listOfViolatedRules)
				cpt += 1
				
				var = N.getVariable(rule[0])
				
				inversedRule = list(rule)
				inversedRule[-1] = not inversedRule[-1]
				
				# new rule
				if not N.preferred(inversedRule):
					var.addPreference(rule[1:])
				
				# rule already exists, we need to add a parent to a variable
				else:
					if numberOfParents2 == -1 or len(var.parents) < numberOfParents2:
						parFind = searchParent(N,dataset,outcome,flipOutcome,rule,var,autorizedCycle)
						
						if parFind.id != -1:
							if var.id in listOfViolatedRules:
								del listOfViolatedRules[var.id]
							# update the preferences
							parentsState,parentPos = var.stateWithParentsValue(outcome,parFind)
							rule[1] = fromBinToInt(parentsState)
							inversedParentsState = list(parentsState)
							inversedParentsState[parentPos] = not inversedParentsState[parentPos]
							inversedRule = [rule[0],fromBinToInt(inversedParentsState),not rule[2]]
							var.addPreferences([rule[1:],inversedRule[1:]])
						
						# if there are no parent variable, we put the swap in a forbidden list
						else:
							if not rule[0] in listOfViolatedRules.keys():
								listOfViolatedRules[rule[0]] = {}
							listOfViolatedRules[rule[0]][rule[1]] = rule[2]
					else:
						if not rule[0] in listOfViolatedRules.keys():
							listOfViolatedRules[rule[0]] = {}
						listOfViolatedRules[rule[0]][rule[1]] = rule[2]
						
					if convergence:
						correctComp = 0
						for comparison in dataset.data:
							if N.preferred(N.returnRule(N.getVariable(comparison[2]),comparison[0],comparison[1])):
								correctComp += 1
						
						if len(convergenceAccuracy) <= cpt:
							convergenceAccuracy.append([correctComp/dataset.numberOfObjects*100])
						else:
							convergenceAccuracy[cpt].append(correctComp/dataset.numberOfObjects*100)
						cpt += 1
				
				# N.displayCPNet()
				# N.displayCPNetInfo()
				# print()
				if trte:
					equivalent,outcome,flipOutcome,rule,trueSwapTr,falseSwapTr,indifferentSwapTr = dataset.EQTr(N,listOfViolatedRules)
					equivalent,outcome,flipOutcome,rule,trueSwap,falseSwap,indifferentSwap = dataset.EQTe(N,listOfViolatedRules)
				else:
					equivalent,outcome,flipOutcome,rule,trueSwap,falseSwap,indifferentSwap = dataset.EQ(N,listOfViolatedRules)
				
				
			# print()
			
			timeAfter = time.clock()
			tt = timeAfter - timeBefore
			timeSmooth += timeAfter - timeBefore
			
			if tt > maxT:
				maxT = tt
			if tt < minT:
				minT = tt
			
			swap = trueSwap + falseSwap + indifferentSwap
			accuracy = trueSwap/swap*100
			indifferenceAccuracy = indifferentSwap/swap*100
			
			if accuracy < minAccuracy:
				minAccuracy = accuracy
			if accuracy > maxAccuracy:
				maxAccuracy = accuracy
				
			acc.append(accuracy)
			temps.append(tt)
			
			averageSwap += swap
			averageTrueSwap += trueSwap
			averageFalseSwap += falseSwap
			averageIndifferentSwap += indifferentSwap
			averageAccuracy += accuracy
			averageIndifferenceAccuracy += indifferenceAccuracy
	
	totalSmooth = smooth*smooth2
	
	moyenneAcc = 0
	moyenneT = 0
	for i in range(totalSmooth):
		moyenneAcc += acc[i]
		moyenneT += temps[i]
	moyenneAcc /= totalSmooth
	moyenneT /= totalSmooth
	
	ecA = 0
	ecT = 0
	
	for i in range(totalSmooth):
		ecA += (acc[i] - moyenneAcc)**2
		ecT += (temps[i] - moyenneT)**2
	ecA /= (totalSmooth-1)
	ecT /= (totalSmooth-1)
	
	averageAccuracy /= totalSmooth
	averageIndifferenceAccuracy /=totalSmooth
	averageSwap /= totalSmooth
	averageTrueSwap /= totalSmooth
	averageIndifferentSwap /= totalSmooth
	averageFalseSwap /= totalSmooth
	
	
	meanConvergenceAccuracy = []
	sdConvergenceAccuracy = []
	if convergence:
		maxLenIt = -1
		if len(convergenceAccuracy)>maxLenIt:
			maxLenIt = len(convergenceAccuracy)
		lastIt = convergenceAccuracy[-1]
		while len(convergenceAccuracy) < maxLenIt:
			convergenceAccuracy.append(lastIt)
			
		meanConvergenceAccuracy = [0 for i in range(len(convergenceAccuracy))]
		sdConvergenceAccuracy = [0 for i in range(len(convergenceAccuracy))]
		for j in range(len(meanConvergenceAccuracy)):
			for i in range(len(convergenceAccuracy[j])):
				meanConvergenceAccuracy[j] += convergenceAccuracy[j][i]
			meanConvergenceAccuracy[j] /= len(convergenceAccuracy[j])
			for i in range(len(convergenceAccuracy[j])):
				sdConvergenceAccuracy[j] += (convergenceAccuracy[j][i] - meanConvergenceAccuracy[j])**2
			if len(convergenceAccuracy[j]) != 1:
				sdConvergenceAccuracy[j] /= (len(convergenceAccuracy[j]) - 1)
				sdConvergenceAccuracy[j] = sqrt(sdConvergenceAccuracy[j])
	
	print("For the last last CP-Net :")
	print("We obtain the following learned CP-Net (with",str(falseSwap) + "/" + str(swap),"violated swap(s), thus",str(accuracy) + "% of accuracy and",str(indifferenceAccuracy) + "% of indifference accuracy) :")
	# N.displayCPNet()
	# print()
	N.displayCPNetInfo()
	
	# print("\n The average accuracy of the entire procedure (we smooth the accuracy by repeating",totalSmooth,"times the procedure) is " + str(averageAccuracy) + "% (accuracy min = " + str(minAccuracy) + "%, and accuracy max = " + str(maxAccuracy) + "%), with",str(averageIndifferenceAccuracy) + "% of average indifference accuracy, for an average of",str(int(averageFalseSwap)) + "/" + str(int(averageSwap)),"violated swap(s)")
	
	littleComputeTime = int(timeSmooth / totalSmooth)
	ct = timeSmooth
	
	hour = ""
	littleHour = ""
	if timeSmooth > 3600:
		hour += str(int(timeSmooth/3600)) + " hour(s), "
		timeSmooth %= 60
	if timeSmooth > 60:
		hour += str(int(timeSmooth/60)) + " minute(s), and "
		timeSmooth %= 60
		
	if littleComputeTime > 3600:
		littleHour += str(int(littleComputeTime/3600)) + " hour(s), "
		littleComputeTime %= 60
	if littleComputeTime > 60:
		littleHour += str(int(littleComputeTime/60)) + " minute(s), and "
		littleComputeTime %= 60
	# print("The program takes", hour + str(int(timeSmooth)) + " second(s) to learn all the CP-Net (thus, an average time of", littleHour + str(int(littleComputeTime)),"second(s) to learn one CP-Net)")
	# print("\n")
	return averageAccuracy,sqrt(ecA),minAccuracy,maxAccuracy,moyenneT,sqrt(ecT),minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy

# name, numberOfVariables, numberOfEdges, numberOfParentsForCPNetToLearn, numberOfParentsForLearnedCPNet, numberOfRoundsForFileGenerating, numberOfRoundsForLearningProcedure, true = learnFromARandomCPNet and false = learnFromDataset, true = autorizeCyclicCPNets and false = forbidCyclicCPNets, numberOfObjects, numberOfDifferentScores, true = useAFile and false = generateRandomDataset 







# n = [3,4,5,6,7,8,9,10,11,12]
# e = [1,3,-1]

# file = open("results1.dat","w")
# print("1st experience")
# file.write("\n1st experience (learn from random CPNet):\n")
# for i in n:
	# for j in e:
		# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",i,j,5,5,10,3,True,False,500,15,5,False,False,True,0)
		# file.write("for " + str(i) + " variables, with 5 parents, delta = " + str(j) + " and acyclicity (10 x 3 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.close()





prob = 10

# file = open("results_" + str(prob) + ".dat","w")
# p = [0,1,2,3,4,5,6,7]
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",8,-1,-1,j,10,3,True,False,5000,8,-1,False,False,True,prob)
	# file.write(str(j) + " " + str(a) + " " + str(ecA) + "\n")
# file.close()

# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",8,-1,-1,-1,10,3,True,False,5000,8,-1,False,True,False,prob)
# convfile = open("test_conv_" + str(prob) + ".dat","w")
# convfile.write("0 100 0\n")
# for i,v in enumerate(meanConvergenceAccuracy):
	# convfile.write(str(i+1) + " " + str(100-v) + " " + str(sdConvergenceAccuracy[i]) + "\n")
# convfile.write("\n")
# convfile.close()

# file = open("results_trte_" + str(prob) + ".dat","w")
# p = [0,1,2,3,4,5,6,7]
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",8,-1,-1,j,10,3,True,False,5000,8,-1,False,False,True,prob)
	# file.write(str(j) + " " + str(a) + " " + str(ecA) + "\n")
# file.close()








# file = open("results3.dat","w")
# print("3rd experience")
# file.write("\n3rd experience (learn from dataset):\n")
# p = [0,1,2,3,4,5,6]
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,j,5,10,True,False,50,-1,5,False,False,True,prob)
	# file.write("for 50 objects, with " + str(j) + " parents and acyclicity (5 x 10 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("1")
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("hotels_fca_binarisation.dat",1,1,-1,j,5,10,False,False,-1,-1,5,True,False,False,prob)
	# file.write("for hotels_fca_binarisation.data, with " + str(j) + " parents and acyclicity (5 x 10 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("2")
# p = [0,1,2,3,4,5,6,7,8,9]
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,j,5,10,True,False,500,-1,5,False,False,True,prob)
	# file.write("for 500 objects, with " + str(j) + " parents and acyclicity (5 x 10 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("3")
# p = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
# for j in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,j,5,10,True,False,10000,-1,5,False,False,True,prob)
	# file.write("for 10000 objects, with " + str(j) + " parents and acyclicity (5 x 10 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.close()


# file = open("results4.dat","w")
# print("4th experience")
# file.write("\n4th experience (fix the number of variables):\n")
# p = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
# for i in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,i,2,5,False,False,500,15,5,False,False,True,prob)
	# file.write("for 500 objects and 15 attributes, with " + str(i) + " parents and acyclicity (2 x 5 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("1")
# for i in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,i,2,5,False,False,1000,15,5,False,False,True,prob)
	# file.write("for 1000 objects and 15 attributes, with " + str(i) + " parents and acyclicity (2 x 5 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("2")
# for i in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,i,2,5,False,False,5000,15,5,False,False,True,prob)
	# file.write("for 5000 objects and 15 attributes, with " + str(i) + " parents and acyclicity (2 x 5 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("3")
# for i in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,i,2,5,False,False,10000,15,5,False,False,True,prob)
	# file.write("for 10000 objects and 15 attributes, with " + str(i) + " parents and acyclicity (2 x 5 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.write("\n")
# print("4")
# p = [0,1,2,3,4,5,6,7,8,9,10,11,12]
# for i in p:
	# a,ecA,minA,maxA,t,ecT,minT,maxT,meanConvergenceAccuracy,sdConvergenceAccuracy = learningCPNet("",1,1,-1,i,2,5,False,False,20000,15,5,False,False,True,prob)
	# file.write("for 20000 objects and 15 attributes, with " + str(i) + " parents and acyclicity (2 x 5 rounds), we have " + str(a) + "% of agreement (ecart-type = " + str(ecA) + ") and computation takes " + str(t) + " seconds (ecart-type = " + str(ecT) + ").\n")
# file.close()





# learningCPNet("",3,-1,-1,-1,1,100,True,False,1000,15,5,False)

# learningCPNet("../50Obj_7Attr_560.data",3,-1,-1,10,10,True,False,1000,5,False)
# learningCPNet("../hotels_fca_binarisation.data",4,-1,5,30,True,True)
# learningCPNet("../hotels_fca_binarisation.data",6,-1,5,30,True,True)
# learningCPNet("../hotels_fca_binarisation.data",8,-1,5,30,True,True)
# learningCPNet("../hotels_fca_binarisation.data",10,-1,5,30,True,True)
# learningCPNet("../hotels_fca_binarisation.data",12,-1,5,30,True,True)
# learningCPNet("../500Obj_10Attr_109.data",2,-1,-1,10,False,False)
# learningCPNet("../500Obj_10Attr_190.data",2,-1,-1,10,False,False)
# learningCPNet("../500Obj_10Attr_923.data",2,-1,-1,10,False,False)
# learningCPNet("../2000Obj_12Attr_411.data",-1,10)
# learningCPNet("../test_database.data",2,-1,-1,1,False,False)
# learningCPNet("../500Obj_10Attr_923.data",-1,100)
# learningCPNet("../10000Obj_15Attr_527.data",1,1,-1,100,False,False)
# learningCPNet("../50Obj_7Attr_560.data",-1,10)
# learningCPNet("50Obj_7Attr_560.data",1)
# learningCPNet("50Obj_7Attr_560.data",2)
# learningCPNet("50Obj_7Attr_560.data",3)
# learningCPNet("../50Obj_7Attr_560.data",10)
# learningCPNet("test_database.data")
