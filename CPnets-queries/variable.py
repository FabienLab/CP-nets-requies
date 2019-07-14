import math as m
import string as s
# import numpy as np
# from igraph import *
from operator import attrgetter
import random
from utility import *
	
# a variable consists of
# an id (unique), for instance 2
# a set (list) of parents variables, for instance [A,B]
# an hashmap of preferences, for instance {0 -> 0, 3 -> 1} which means
# a'b'c' > a'b'c, abc > abc'. For ab' and a'b, we don't know the preference between c and c'
class Variable:
	def __init__(self, id = -1, parents = None, preferences = None):
		self.id = id
		if not parents:
			self.parents = []
		else:
			self.parents = parents
		self.preferences = {}
		if preferences:
			for pref in preferences:
				self.preferences[fromBinToInt(pref[:-1])] = pref[-1]
		
	def __lt__(self,v):
		return self.id < v.id
				
	# return True if rule (of the form [valParents,valVar]) corresponds to an existent rule for the current variable
	def preferred(self,rule):
		if len(self.preferences) != 0 and rule[0] in self.preferences and self.preferences[rule[0]] == rule[1]:
			return True
		return False
	
	# refresh conditionals preferences of current variable
	def setPreferences(self, preferences):
		self.preferences = {}
		if preferences:
			for pref in preferences:
				self.preferences[fromBinToInt(pref[:-1])] = pref[-1]
				
	def addPreference(self, rule):
		self.preferences[rule[0]] = rule[1]
	
	# preferences is an hashmap his the value of parents in keys and the value of the variable in values
	def addPreferences(self, preferences):
		for rule in preferences:
			if len(self.parents) == 0:
				self.preferences[-1] = rule[1]
			self.preferences[rule[0]] = rule[1]
			
	def addPreference(self, rule):
		self.preferences[rule[0]] = rule[1]
	
	def addParents(self,listParents,preferences):
		for par in listParents:
			self.parents.append(par)
		self.parents.sort()
		self.setPreferences(preferences)
		
	def parentsId(self):
		parentsId = []
		for par in self.parents:
			parentsId.append(par.id)
		return parentsId
	
	def deleteParents(self,listParents,preferences):
		for par in listParents:
			if par in self.parents:
				self.parents.remove(par)
		self.setPreferences(preferences)
		
	def stateWithParentsValue(self,state,newPar):
		parentsValues = []
		for par in self.parents:
			parentsValues.append(state[par.id])
		return parentsValues,self.parents.index(newPar)
		