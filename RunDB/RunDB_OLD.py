"""
Old Run DB wrapper
"""

import sys, os
pathToUtilities = os.environ["HCALDQMUTILITIES"]
sys.path.append(pathToUtilities)

import Utils.Shell as Shell

class RunDB:
	def __init__(self, msettings):
		self.settings = msettings
	
	def install(self):
		""" install the DB-like structure """
		pass

	def initialize(self):
		""" intialize whatever is needed """
		pass

	def exists(self, runnumber):
		pass

	def mark(self, runnumber, runType, m):
		pass

	def getLast(self, runType):
		""" list the last N runfiles and runnumbers for runType """
		pass
