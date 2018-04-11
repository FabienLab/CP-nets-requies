from variable import *
from random import *

# a CP-Net constists of
# a name, usually a letter
# a list of variables
# a cpGraph (represented by an adjacency matrix)
# an outcome graph (represented by a adjacency list)
class CPNet:
	def __init__(self, nbVar = -1,lbd = -1,nbMaxParents = -1, name = "", variables = None, empty = False, random = False):
		self.name = name
		if not random:
			if not variables:
				self.variables = []
				if empty == False:
					x = input("Combien voulez-vous de variables ?")
					for i in range(int(x)):
						self.variables.append(Variable(id = i, preferences = [[1]]))
			else:
				self.variables = variables
				for i,var in enumerate(self.variables):
					var.id = i
					
		else:
			self.variables = []
			
			# create variables
			for i in range(nbVar):
				self.variables.append(Variable(id = len(self.variables)))
			
			nbMaxEdges = int(nbVar * (nbVar - 1)/2)
			if lbd == -1:
				nbEdges = nbMaxEdges
			else:
				nbEdges = lbd * nbVar
				if nbEdges > nbMaxEdges:
					nbEdges = nbMaxEdges
			nbEdgesToDelete = nbMaxEdges - nbEdges
			
			# create parents variables
			for i in range(len(self.variables)):
				var1 = self.getVariable(i)
				for j in range(i+1,len(self.variables)):
					var2 = self.getVariable(j)
					self.addParentVariables(var2,[var1])
					
			t = self.depassParent(nbMaxParents)
			shuffle(t)
			if nbMaxParents != -1:
				for var in t:
					while len(var.parents) > nbMaxParents:
						par = var.parents[randint(0,len(var.parents)-1)]
						self.deleteParentVariables(var,[par])
						nbEdgesToDelete -= 1
			
			while nbEdgesToDelete > 0:
				var = self.variables[randint(0,len(self.variables)-1)]
				if len(var.parents) != 0:
					par = var.parents[randint(0,len(var.parents)-1)]
					self.deleteParentVariables(var,[par])
					nbEdgesToDelete -= 1
			
			# create preferences
			for var in self.variables:
				pref = []
				for i in range(2**len(var.parents)):
					pref.append([i,randint(0,1)])
				var.addPreferences(pref)
	
	def depassParent(self,nbPar):
		t = []
		for var in self.variables:
			if len(var.parents) > nbPar:
				t.append(var)
		return t
	
	# return True if state with var is preferred to state with var', False else
	def preferred(self,rule):
		return self.variables[rule[0]].preferred(rule[1:])
	
	# return the variable which has the correspondant varId
	def getVariable(self, varId):
		for var in self.variables:
			if var.id == varId:
				return var
		return -1
		
	def addVariables(self, numberOfVariables = 1):
		for i in range(numberOfVariables):
			self.variables.append(Variable(len(self.variables)))
		self.updateCPGraph()
		
	def addParentVariables(self,var,listParents,pref = None):
		self.variables[self.variables.index(var)].addParents(listParents,preferences = pref)
		self.updateCPGraph()
	
	def deleteParentVariables(self,var,listParents,pref = None):
		self.variables[self.variables.index(var)].deleteParents(listParents,preferences = pref)
		self.updateCPGraph()
	
	def updateGraphs(self,setOfOutcomes):
		self.updateCPGraph()
		self.updateGraph(setOfOutcomes)
		
	def updateCPGraph(self):
		self.CPGraph = {}
		self.fillCPGraph()
		
	def updateGraph(self,setOfOutcomes):
		self.graph = {}
		self.fillGraph(setOfOutcomes)
		
	def displayCPNetInfo(self):
		print("This CP-Net",self.name,"has", len(self.variables), "variable(s)")
		for var in self.variables:
			p = ""
			for par in var.parents:
				p += " " + str(par.id)
			print("Var." + str(var.id),"has",len(var.parents),"parents variable(s) :" + p)				
			
	def displayCPNet(self):
		print("This CP-Net",self.name,"has", len(self.variables), "variable(s).")
		noPreferences = True
		for var in self.variables:
			if var.parents == [] and var.preferences:
				noPreferences = False
				print("Var." + str(var.id), ":", var.preferences[-1], "is preferred than", int(not(var.preferences[-1])))
			if var.parents != []:
				for key in var.preferences.keys():
					parentsVect = fromIntToBin(key,len(var.parents))
					noPreferences = False
					string = "with"
					for i,elt in enumerate(parentsVect):
						if i < len(var.parents):
							string += " Var." + str(var.parents[i].id) + " = " + str(elt)
					print("Var." + str(var.id), string, "as parents :", int(var.preferences[key]), "is preferred than", int(not(var.preferences[key])))
		if noPreferences:
			print("Without any preference yet.")

	def displayGraph(self,setOfOutcomes):
		self.updateGraph(setOfOutcomes)
		
		for k,v in self.graph.items():
			print(str(k) + " : " + str(v))
		
		# display real graph
		# gr = []
		# g = Graph()
		# g.add_vertices(2**len(self.variables))
		# for i in range(2**len(self.variables)):
			# for j in range(2**len(self.variables)):
				# if self.graph[i][j] == 1:
					# gr.append((i,j))
		# g.to_directed(False)
		# g.add_edges(gr)
		# for i in range(2**len(self.variables)):
			# tab = fromIntToBin(i,len(self.variables))
			# s = ""
			# for j in range(len(self.variables)):
				# s += str(tab[len(self.variables) - 1 - j])
			# g.vs[i]["label"] = s
		# g.vs["label_size"] = 12
		# g.vs["size"] = 30
		# g.vs["shape"] = "rectangle"
		# layout = g.layout("kk")
		# plot(g, layout = layout, bbox = (600, 600),target = str(random.randint(0,10000000))+".png")
		# plot(g, layout = layout, bbox = (600, 600))
		
	def displayCPNetAndGraph(self,setOfOutcomes):
		self.displayCPNet()
		self.displayGraph(setOfOutcomes)
		
	def fillCPGraph(self):
		for var in self.variables:
			self.CPGraph[var.id] = []
		for var in self.variables:
			for par in var.parents:
				self.CPGraph[par.id].append(var.id)
	
	# return True iff CPGraph has a cycle, False else
	# we delete each "puits" node until we cannot
	def cycle(self):
		CPGraph = self.CPGraph.copy()
		b = True
		while b:
			var = -1
			for v in CPGraph.keys():
				if CPGraph[v] == []:
					var = v
			if var != -1:
				for v in CPGraph.keys():
					if var in CPGraph[v]:
						CPGraph[v].remove(var)
				del CPGraph[var]
			else:
				b = False
		if len(CPGraph) != 0:
			return True
		return False
		
	def fillGraph(self,setOfOutcomes):
		# stock all real vertices
		setOfOutcomesNumbers = []
		for outcome in setOfOutcomes:
			setOfOutcomesNumbers.append(fromBinToInt(outcome))
		
		# fill the adjacency list of our graph
		for outcome in setOfOutcomes:
			outcomeNumber = fromBinToInt(outcome)
			
			# list of outcomes that are less preferred than 'outcome'
			listOfLessPrefOutcomes = []
			
			# test the preference between each flip
			for var in self.variables:
				preferred,flipOutcome = var.preferred(outcome)
				flipOutcomeNumber = fromBinToInt(flipOutcome)
				if preferred and flipOutcomeNumber in setOfOutcomesNumbers:
					listOfLessPrefOutcomes.append(flipOutcomeNumber)
			if len(listOfLessPrefOutcomes) != 0:
				self.graph[outcomeNumber] = listOfLessPrefOutcomes
							
		# transitive reduction
		for outcome1 in self.graph.keys():
			for outcome2 in self.graph.keys():
				if outcome2 in self.graph[outcome1] and self.existPath(outcome1,outcome2):
					self.graph[outcome1].remove(outcome2)					

	def existPath(self,firstOutcome,lastOutcome):
		path = False
		if firstOutcome in self.graph.keys():
			for middleOutcome in self.graph[firstOutcome]:
				if middleOutcome != lastOutcome:
					path = path or self.existPathRec(middleOutcome,lastOutcome)
		return path
		
	def existPathRec(self,firstOutcome,lastOutcome):
		if (firstOutcome == lastOutcome):
			return True
		path = False
		if firstOutcome in self.graph.keys():
			for middleOutcome in self.graph[firstOutcome]:
				path = path or self.existPathRec(middleOutcome,lastOutcome)
		return path
	
	# rule = [varId,parentsValue,valVar]
	def returnRule(self,flipVar,outcome1,outcome2):
		tab = []
		if flipVar.parents == []:
			return [self.variables[flipVariable(outcome1,outcome2)].id,-1,outcome1[flipVar.id]]
		for par in flipVar.parents:
			tab.append(outcome1[par.id])
		return [self.variables[flipVariable(outcome1,outcome2)].id,fromBinToInt(tab),outcome1[flipVar.id]]
		
		


# A = Variable(parents = [], preferences = [[1]])
# B = Variable(parents = [A], preferences = [[1,1],[0,0]])
# C = Variable(parents = [], preferences = [[1]])
# C = Variable("C",[A,B],[[1,1,1],[1,0,0],[0,1,1],[0,0,1]])
# D = Variable("D",[A,C],[[1,1,1],[1,0,1],[0,1,0],[0,0,1]])
# E = Variable("E",[])
# F = Variable("F",[E])
# C = Variable(0,"C",[A,B],[[1,1,1],[0,1,0],[1,0,0],[0,0,1]])



# N = CPNet("N",[A,B,C])

# N.displayCPNetAndGraph([[1,1,1],[1,1,0],[1,0,1],[1,0,0],[0,0,0]])
