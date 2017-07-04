import sys
sys.path.insert(0,"util/")
sys.path.insert(0,"core/")
import click
from EmulatorInterface import EmulatorInterface
from Logger import Logger
import os
from Controller import Controller
import re

##This class start the DataCollection.
#It search for folders that contain an apk file inside the workspacePath.
#Each apk is executed n times and data are saved into a file with a user-defined name
#inside the apk folder.

class DataCollection:

	numberOfRun = 0;
	numberOfEvents = 0;
	workspacePath = ""
	resultName = ""
	playerPath = ""
	apk_regex = ""
	VMName = ""
	logger = "";
	emulator = "";
	rndSeed = "";
	throttle = "";



	def __init__(self,workspacePath,resultName,emulator,playerPath,VMName,apk_regex,run,event,rndSeed,throttle):
		self.workspacePath = workspacePath;
		self.resultName = resultName;
		self.playerPath = playerPath;
		self.VMName = VMName;
		self.apk_regex = apk_regex;
		self.numberOfRun = run;
		self.numberOfEvents = event;
		self.rndSeed = rndSeed;
		self.emulator = emulator;
		self.throttle = throttle;
		self.logger = Logger(3);
		self.logger.log("INFO","CREATED NEW EPERIMENT:  \n\
						\t Workspace Path: {}\n\
						\t Result Prefix: {}\n\
						\t Emulator: {} \n \
						\t Player Path: {}\n\
						\t Virtual Machine Name: {} \n\
						\t APK Regex: {} \n\
						\t Number Of Run per Packet: {} \n\
						\t Number of Event per Run: {} \n\\".format(workspacePath,resultName,emulator,playerPath,VMName,apk_regex,run,event));

	def runExperiment(self):
		self.logger.log("INFO","STARTING EXPERIMENT");
		dir = os.listdir(self.workspacePath);
		for item in dir:
			if(os.path.isdir(self.workspacePath + item)):
				print("--------------------------------------")
				self.logger.log("INFO","TESTING PACKAGE: " + item); 
				path = self.workspacePath + item + "/";
				apkDir = os.listdir(path)
				for apk_item in apkDir:
					regex = re.compile(self.apk_regex);
					if(os.path.isfile(path + apk_item)  and regex.match(apk_item) != None):
						self.logger.log("INFO","TESTING PACKAGE: " + item); 
						for i in range(0,self.numberOfRun):
							self.logger.log("INFO","RUN: " + str(i) + " OF: " + str(self.numberOfRun)); 
							fileName = path + str(self.numberOfEvents)+self.resultName+str(i)+".csv";
							fileNameErr = path + str(self.numberOfEvents)+self.resultName+str(i)+".csv.err";
							if(os.path.exists(fileName) == False and os.path.exists(fileNameErr) == False): 
								self.logger.log("INFO","RUN: " + str(i) + " OF: " + str(self.numberOfRun)); 
								emulatorInterface = EmulatorInterface(self.playerPath,self.VMName,self.emulator);
								emulatorInterface.restoreSnapshot("Snap1");
								emulatorInterface.runEmulator();
								controller = Controller(self.numberOfEvents,self.throttle);
								controller.run(path+apk_item,fileName,self.rndSeed);
								emulatorInterface.stopEmulator();
							else:
								self.logger.log("INFO","FILENAME: " + fileName + " ALREADY EXIST -- SKIPPPING");
		self.logger.log("INFO","FINISH EXPERIMENT");
	
@click.command()
@click.option("--workspacepath",default="",help="Workspace path of apk")
@click.option("--resultname",default="",help="Prefix of data files")
@click.option("--emulator",default="",help="Name of emulator: vbox|geny")
@click.option("--playerpath",default="",help="Path of genymotion player")
@click.option("--vmname",default="",help="Name of virtual machine")
@click.option("--apk_regex",default="\w{64}.apk",help="Regex for apk files (optional)")
@click.option("--run",default=0,help="Number of run for each packet")
@click.option("--event",default=0,help="Number of event for each run")
@click.option("--rndseed",default=False,help="True if you want change the simulated event every run")
@click.option("--throttle",default=1,help="Delay in microsecond between inputs events")
def hello(workspacepath,resultname,emulator,playerpath,vmname,apk_regex,run,event,rndseed,throttle):
	experiment = DataCollection(workspacepath,resultname,emulator,playerpath,vmname,apk_regex,run,event,rndseed,throttle);
	experiment.runExperiment();

if __name__ == "__main__":
	hello();
 