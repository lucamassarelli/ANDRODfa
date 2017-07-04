from AndroidToolInterface import AndroidToolInterface
from datetime import datetime;
from Logger import Logger;
from MetricsCollector import MetricsCollector
from MetricsCollector import ProcMetrics
import queue as Queue;
import random
import subprocess
import threading;
import time;
import re


##This class implements the controller that handle the application execution and the data
#collection. Data are also printed in a file during collection. The file is located in the
#same folder of the apk file that is being executed

class Controller:
	
	logLevel = 1;
	logger = ""	
	q  = ""
	start_time = 0;	
	runMeasurement = False
	measurementError = 0;
	PID = -1
	numberOfEvent = 0
	throttle = 0;
	monkeyThread = 0;
	androidToolInterface = 0;
	appTracer = 0;
	packageName = "";
	samplingTime = 0.25
	monkeyError = False;
	c = "";
	throttle = "";

	##The constructor
	# @param numberOfEvent = number of event to simulate to the application
	# @param throttle = millisecond delay between simulated events
	def __init__(self,numberOfEvent,throttle):
		self.logger = Logger(self.logLevel);
		self.numberOfEvent = numberOfEvent;
		self.throttle = throttle;
		self.androidToolInterface = AndroidToolInterface();

	##This method perform the measurement of the 26 different metrics.
	def measure(self):
		metricCollector = MetricsCollector(self.PID);
		procResult = metricCollector.measureMetrics();
		if(procResult != -1 and procResult != None):
			csvResult = procResult.formatCsv();
			self.q.put(csvResult);
			
			if(procResult.error != 0):
				self.measurementError = self.measurementError + 1;
				self.logger.log("ERROR","ERROR IN MEASUREMENT");
				self.PID = self.getPID(self.packageName);	
			elif(self.measurementError > 0):
				self.measurementError = 0;
				self.logger.log("INFO","RESUMING MEASUREMENT");
		else:
			self.measurementError = self.measurementError + 1;
			self.logger.log("ERROR","ERROR IN MEASUREMENT");
			self.PID = self.getPID(self.packageName);
			
		
	##This print to a csv file the measured data read from the queue
	# @param resultName = name of the where result are printed
	# @param packageName = name of the package that is executed
	# @param apkName = name of the apk that is being executed
	def printToFile(self,resultName,packageName,apkName):
		out_file = open(resultName,"w")
		self.logger.log("INFO","PRINTING RESULT IN FILE: " + resultName);
		out_file.write("#" + packageName + "\n");
		out_file.write("#" + apkName + "\n");
		out_file.write("#" + ProcMetrics.header() + "\n");
		t = threading.currentThread()
		
		while getattr(t, "do_run", True):
			try:
				self.logger.log("VERBOSE DEBUG","DO RUN: " + str(getattr(t, "do_run", True)))
				item = self.q.get(False)
				out_file.write(item+"\n");
				self.q.task_done();
			except Queue.Empty:
				self.logger.log("VERBOSE DEBUG","EMPTY")	
				
		self.logger.log("VERBOSE DEBUG","CLOSING FILE");
		out_file.close();
		self.logger.log("INFO","FILE CLOSED");

	##This method wake up the thread that do the measurement with a frequency given by 
	#static defined samplingTime of this class
	def startMeasureThread(self):
		timer = threading.Timer(self.samplingTime,self.startMeasureThread)
		timer.start();
		#print(datetime.now())
		self.c.acquire();
		runMeasurement = self.runMeasurement
		self.c.release();
		if(runMeasurement):
			try:			
				thread = threading.Thread(target=self.measure);
				thread.start();
			except:
				self.logger.log("ERROR","THREAD ERROR");
		else:
			timer.cancel();
			
	##This method start the monkey tool 
	def monkeyThread(self,monkeyOptionRun):
		res = self.androidToolInterface.runApplication(self.packageName,monkeyOptionRun);
		if(res == -1):
			self.logger.log("ERROR","ERROR RUNNING APPLICATION");
			self.monkeyError = True

	##This method run the top command and return the output as a string
	def runTopCommand(self):
		bashCommand = ['adb shell top -d 0 -n 1']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
                  self.logger.log("DEBUG", "TOP DONE")
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR TOP");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);	

	##This method get the PID of a running package
	# @param packageName = package to get the PID
	def getPID(self,packageName):
		pid = -1;
		topResult = self.runTopCommand();
		if(topResult == -1):
			return(-1);
		#topResult = topResult.split("\n");
		regexApp = re.compile("\d*\s*\d*\s*\d*%\s*\w*\s*\d*\s*\d*K\s*\d*K\s*\w*\s*\w*\s*\w*\s*"+packageName); 
		appLine = re.findall(regexApp,topResult);
		if(appLine):
			lineSplitted = appLine[0].split();
			pid = lineSplitted[0];		
			self.logger.log("DEBUG","PACKAGE: " + packageName + " PID: " + pid);
			return(pid);
		else:
			self.logger.log("ERROR", "CANNOT FIND PID OF PACKAGE: " + packageName);
			return(-1);
			
	##This method handle all the workflow to execute the application and to measure data
	# @param apkName = name of the apk will be be executed
	# @param resultName = name of the file where result are printed
	def run(self,apkName,resultName,rnd):
		monkeyOptionOnlyStart = "-c android.intent.category.LAUNCHER 1" 
		self.packageName = self.androidToolInterface.findPackageName(apkName);
		if(self.packageName == -1):
			self.logger.log("ERROR","CANNOT FIND PACKAGE NAME");
			return(-1);		
		res = self.androidToolInterface.installAPK(apkName);
		if(res == -1):
			self.logger.log("ERROR","ERROR INSTALLING APK");
			return(-1);
		runningRes = self.androidToolInterface.runApplication(self.packageName,monkeyOptionOnlyStart);
		if(runningRes == -1):
			self.logger.log("ERROR","ERROR STARTING APPLICATION");
			return(-1)
		time.sleep(1);
		self.start_time = datetime.now();
		remainingEvent = self.numberOfEvent;
		if(rnd == True):
			seed = random.randint(1200, 1300)
		else:
			seed = 1234

		monkeyOptionRun = "--throttle " + str(self.throttle) + " --pct-syskeys 0 --ignore-crashes --ignore-timeouts --ignore-security-exceptions --ignore-native-crashes -s " + str(seed) + " " + str(remainingEvent);
		self.PID = self.getPID(self.packageName);
		if(self.PID == -1):
			self.logger.log("ERROR","CANNOT FIND PID, ABORTING");
			return(-1);
		self.logger.log("INFO","PID: " + self.PID)
		
		self.runMeasurement = True;	
		
		self.c = threading.Condition();
		
		self.q = Queue.Queue()			
		self.startMeasureThread();
			
		printingThread = threading.Thread(target = self.printToFile, args = [resultName,self.packageName,apkName]);
		printingThread.do_run = True
		printingThread.start()
		
		monkeyThread =  threading.Thread(target = self.monkeyThread, args = [monkeyOptionRun]);
		monkeyThread.start();
		monkeyThread.join(300);
		
		if(monkeyThread.isAlive()):
			self.logger.log("INFO", "MONKEY THREAD TIMEOUT");
			self.monkeyError = True
		
		self.c.acquire();
		self.runMeasurement = False;
		self.c.release();
		
		self.q.join();

		self.logger.log("VERBOSE DEBUG","QUEUE EMPTY");
		printingThread.do_run = False
		
		while(printingThread.isAlive()):
			printingThread.do_run = False
			self.logger.log("VERBOSE DEBUG","WAITING FOR PRINTING THREAD TO EXIT");
			time.sleep(0.2);

		self.androidToolInterface.uninstallApplication(self.packageName);
		time.sleep(0.1)
		if(self.monkeyError or self.measurementError > 0):
			self.logger.log("INFO","APPLICATION THROW ERROR DURING RUNNING: " + self.packageName)
			bashCommand = "mv " + resultName +" " + resultName + ".err";
			print(bashCommand)
			try:
				subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
				self.logger.log("INFO","RESULT FILE RENAMED");
			except subprocess.CalledProcessError:
				self.logger.log("ERROR","ERROR REMOVING RESULT FILE");
		else:
			self.logger.log("INFO","APPLICATION RUN SUCCESSFUL: " + self.packageName)
		return(0);
		
