import time

#LOG LEVEL 0 PRINT ONLY INFO TAG
#LOG LEVEL 1 PRINT INFO TAG AND DEBUG TAG
#LOG LEVEL 2 PRINT INFO TAG, DEBUG TAG, VERBOSE DEBUG TAG

##This class implements a logger with various level of logging;
#the log level with the binded tag are:
# 0 - error
# 1 - info
# 2 - debug
# 3 - verbose debug
#once choosed the log level all messages with the same level or below will be
#printed;
class Logger:
    
	
	logLevel = 0;
	
	logType = ["ERROR","INFO","DEBUG","VERBOSE DEBUG"];
	
      ##The constructor:
      # @param logLevel = log level for logging
	def __init__(self,logLevel):
		self.logLevel = logLevel;
	
      ##This method print a message in the log;
      # @param tag = tag of message;
      # @param text = text of the message;
	def log(self,tag,text):
		localtime = time.asctime( time.localtime(time.time()));
		if(tag == self.logType[0]):
			print(str(localtime) + " [" + tag + "] - " + text);
			return;
		if(self.logLevel >= 0):
			if(tag == self.logType[1]):
				print(str(localtime) + " [" + tag + "] - " + text);
				return;
		if(self.logLevel >= 1):
			if(tag == self.logType[2]):
				print(str(localtime) + " [" + tag + "] - " + text);
				return;
		if(self.logLevel >= 2):
			if(tag == self.logType[3]):
				print(str(localtime) + " [" + tag + "] - " + text);
				return;	
	
	