"""
Old Run DB wrapper
"""

import sys, os
pathToUtilities = os.environ["HCALDQMUTILITIES"]
sys.path.append(pathToUtilities)

import Utils.Shell as Shell

class RunDB:
	def __init__(self, msettings, logfile):
		self.settings = msettings
		self.logfile = logfile
	
	def install(self):
		""" install the DB-like structure. Assume dbpool exists """
		if Shell.exists(Shell.join(self.settings.dbpool, 
			self.settings.processingtype)):
			for runtype in self.settings.runtypes:
				if Shell.exists(Shell.join(self.settings.dbpool,
					self.settings.processingtype.upper()+"/"+runtype.upper())):
					pass
				else:
					self.installStructure()
					return
		else:
			self.installStructure()

	def installStructure(self):
		#	build top directory of db for the specified ptype
		Shell.mkdir(Shell.join(self.settings.dbpool, 
			self.settings.processingtype.upper()))
		if self.settings.processingtype.upper()=="LOCAL":
			for runtype in self.settings.runtypes:
				Shell.mkdir(Shell.join(self.settings.dbpool, 
					self.settings.processingtype.upper()+"/"+runtype.upper()))
		else:
			pass


	def exists(self, runnumber):
		dbpool = self.settings.dbpool
		self.logfile.write("RunDB::check if %d exists\n" % runnumber)
		if self.settings.processingtype.upper()=="LOCAL":
			ptype = "LOCAL"
			for runtype in self.settings.runtypes:
				if Shell.exists(Shell.join(dbpool, 
					ptype+"/"+runtype.upper()+"/"+str(runnumber))):
					return True
		else:
			return False

		return False

	def mark(self, runnumber, runType, m):
		self.logfile.write("marking %d %s as %s\n" % (
			runnumber, runType.upper(),m))
		dbpool = self.settings.dbpool
		ptype = self.settings.processingtype.upper()
		self.logfile.write("ptype: "+ptype.upper()+"\n")
		if m=="processing":
			#	new run number - create a folder for it
			s = ptype+"/"+runType.upper()+"/"+str(runnumber)
			self.logfile.write("check s: "+s+"\n")
			Shell.mkdir(Shell.join(dbpool, s))
			Shell.touch(Shell.join(dbpool, ptype+"/"+runType.upper()+"/"+
				str(runnumber)+"/"+m))
		elif m=="processed:" or m=="failed" or m=="uploaded":
			if Shell.exists(Shell.join(dbpool, ptype+"/"+runType.upper()+"/"+
				str(runnumber))):
					Shell.touch(Shell.join(dbpool, ptype+"/"+runType.upper()
						+"/"+str(runnumber)+"/"+m))

	def getLast(self, runType):
		""" list the last N runfiles and runnumbers for runType """
		lfiles = []
		lruns = []
		dbpool = self.settings.dbpool
		ptype = self.settings.processingtype.upper()
		dqmiopool = self.settings.dqmiopool

		if ptype=="LOCAL":
			runpathlist = Shell.ls_glob(Shell.join(dbpool, ptype+"/"
				+runType.upper()+"/*"))
			print runpathlist
			for runpath in runpathlist:
				runpath = runpath.split("/")
				lruns[len(lruns):] = [int(runpath[len(runpath)-1])]
			print lruns
			for run in lruns:
				runfileslist = Shell.ls_glob(Shell.join(dbpool, 
					ptype+"/*%d*%s*%s*" % (run, runType.upper(), 
					self.settings.localrunlabel)))
				if len(runfileslist)==0 or len(runfileslist)>1:
					raise IndexError(runfileslist, run)
				lfiles[len(lfiles)] = runfileslist
			
		# return last n runs,files
		return (lruns[-self.settings.numrunsForTrend:],
			lfiles[-self.settings.numrunsForTrend:])

if __name__=="__main__":
	pass
