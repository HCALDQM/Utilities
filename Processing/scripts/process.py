"""
Process runs
"""

import os, sys
import importlib
pathToUtilities = os.environ["HCALDQMUTILITIES"]
sys.path.append(pathToUtilities)

import Utils.Shell as Shell
import WBM.Wrapper as wbm
import RunDB.RunDB_OLD as rundb
import Processing.scripts.run_AnalysisTrend as run

def locked(lockpath):
	if Shell.exists(lockpath):
		return True

	Shell.touch(lockpath)
	return False

#	this should be redone based on the input name
#	for local runs it's 4to10 
def runNumber(filename):
	return int(filename[4:10])

def getRunType(wbmdb, runnumber, settings):
	o,e,rt = wbmdb.query(runnumber, "CONFIG_NEW")
	if o=="":
		o,e,rt = wbmdb.query(runnumber, "CONFIG_OLD")
	if rt>0 or e!="" or o=="":
		return None

	# if all went good - return the type
	return wbm.runinfo_config2runtype(o)



#	this is the where processing starts
def process():
	""" processes runs """
	settings = importlib.import_module(sys.argv[1])
	logfile = open(settings.logfilename, "a")
	logfile.write("Started running at %s %s\n" % (Shell.gettimedate()))
	rdb = rundb.RunDB(settings, logfile); rdb.install()
	
	if locked(settings.lockpath): # return if the same process is running
		logfile.write("lock exists. Exiting...\n")
		return
	try:
		wbmdb = wbm.Wrapper(settings.runinfo_db_name,
			settings.runinfo_db_querytemplate, logfile)
		runlist = Shell.ls_glob(settings.poolsource+"/USC*.root")
		for f in runlist:
			runnumber = runNumber(Shell.split(f)[1])
			filesize = Shell.getsize(f)
			if filesize>settings.filesizelimit or \
				runnumber<settings.firstRunToProcess:
				continue
			
			#	if this guy is already present in the db
			#	go to the next guy
			if rdb.exists(runnumber):
				continue
			else:
				runType = getRunType(wbmdb, runnumber, settings)
				if runType==None:
					continue
	
				#	get the list of last runs before you mark this run
#				listLastRuns,listLastRunFiles = rdb.getLast(runType.upper())
				harvestRunList = rdb.getLast(runType)
				#	mark and process
				rdb.mark(runnumber, runType.upper(), "processing")
				isGood = False
				for i in range(5):
					try:
						#
						#	Try to process for 5 times.
						#	Transferring files might not be optimal and that 
						#	influences  the processing...
						#
						rt = run.process(f, runType.upper(), settings, 
							harvestRunList, logfile)
						if rt==0: # all is good
							rdb.mark(runnumber, runType.upper(), "processed")
							isGood=True
							break
						else:
							isGood=False
							continue
					except Exception as exc:
						isGood=False
						continue
				if not isGood:
					rdb.mark(runnumber, runType.upper(), "failed")
	except NameError as exc:
		logfile.write("NameErorr has occured. Exiting...\n")
		logfile.write("Error Message: "+str(exc.args)+'\n')
	except Exception as exc:
		logfile.write("Exception has been caught. Exiting... \n")
		logfile.write("ErrorName: %s ErrorMessage: %s\n" % (
			type(exc).__name__, str(exc.args)))
	finally:
		logfile.write("Finished running at %s %s\n" % (Shell.gettimedate()))
		Shell.rm(settings.lockpath)

if __name__=="__main__":
	process()
