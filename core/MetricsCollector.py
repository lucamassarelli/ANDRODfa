#Copyright (C) 2017  Luca Massarelli
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
# any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime;
from Logger import Logger;
import re;
import subprocess;
import time;


##This class implements a structure to handle data read by metrics collector. 
# Its method contains the name of the metrics and function to format the metrics in csv style

class ProcMetrics:

	time="0";
	
	error = "0";

	#from proc/stat
	user_cpu = "-1"
	nice_cpu = "-1"
	system_cpu = "-1"
	idle_cpu = "-1"
	iowait_cpu = "-1"
	irq_cpu = "-1"
	softirq_cpu = "-1"
	steal_cpu = "-1"
	
	#from proc/net/dev
	receive_byte = "-1"
	receive_packet = "-1"
	transmit_byte = "-1"
	transmit_packet = "-1"
	
	#from proc/PID/stat
	state = "-1"
	minflt = "-1"
	cminflt = "-1"
	majflt = "-1"
	cmajflt = "-1"
	utime = "-1"
	stime = "-1"
	cutime = "-1"
	cstime = "-1"
	numthreads = "-1"
	vss = "-1"
	rss = "-1"
	processor = "-1"
	
	#from proc/PID/statm
	rmsize = "-1"
	vmsize = "-1"
	shared = "-1"
	text = "-1"
	data = "-1"
	
	def __init__(self):
		a = 1;
		
	##This static method return a ordered list of name of the metrics readed by ProcInterface;
	@staticmethod
	def header():
		str = "time,user_cpu,nice_cpu,system_cpu,idle_cpu,iowait_cpu,irq_cpu,softirq_cpu," + \
			"steal_cpu,receive_byte,receive_packet,transmit_byte,transmit_packet," + \
			"state,minflt,cminflt,majflt,cmahflat,utime,stime,cutime,cstime,numthread,"+\
			"vss,rss,processor,rmsize,vmsize,shared,text,data"
		return(str);
	
	##This method return a csv formatted string of the measured metrics;
	def formatCsv(self):
		str = self.time + "," + self.user_cpu+","+self.nice_cpu+","+self.system_cpu+","+self.idle_cpu+","+\
		self.iowait_cpu+","+self.irq_cpu+","+self.softirq_cpu+","+self.steal_cpu+","+\
		self.receive_byte+","+self.receive_packet+","+self.transmit_byte+"," +\
		self.transmit_packet+","+self.state+","+self.minflt+","+self.cminflt+","+\
		self.majflt+","+self.cmajflt+","+self.utime+","+self.stime+","+self.cutime+","+\
		self.cstime+","+self.numthreads+","+self.vss+","+self.rss+","+self.processor+","+\
		self.rmsize+","+self.vmsize+","+self.shared+","+self.text+","+self.data;		
		return(str);
		
#This class implements commands to read from some /proc/ file:
# - /proc/stat 
# - /proc/net/dev 
# - /proc/[pid]/stat
# - /proc/[pid]/statm
# it implements also a parser to read from this files 26 different metrics:
# CPU: user_cpu,nice_cpu,sytem_cpu,idle_cpu,iowait_cpu,irq_cpu,softirq_cpu,steal_cpu
# CPU (pid): state,minflt,cminflt,majflt,cmajflt,utime,stime,cutime,cstime,numthreads
#			 vss,rss,processor;
# NETWORK: tx_byte,rx_byte,tx_packet,rx_packet;
# MEMORY (pid): rmsize,vmsize,shared,text,data
# this class contrain a procMetrics object where all data are stored

class MetricsCollector:
      
	pid = ""
	procMetrics = ""
	logger = ""
	android_version=4

    ##The constructor
	#@param pid = process id of the process to trace;   
	def __init__(self,pid):
		self.procMetrics = ProcMetrics();
		self.logger = Logger(1);
		self.pid = pid;
	
	##This method read data from the /proc/stat file
	#it return the file as a string or -1 if error occurs
	def readProcStat(self):
		bashCommand = ['adb shell cat /proc/stat']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
                  self.logger.log("DEBUG", "READ proc/stat DONE");
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR READING proc/stat");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);	
	
	##This method parse data from the /proc/stat file
	#it register the parsed value in the object procMetric declared in this class
	#it return 0 if parse went ok or -1 it there was an error
	# @param procOut = string of the read /proc/stat file
	def parseProcStat(self,procOut):
		regex = re.compile("cpu\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+")
		procOut = regex.findall(procOut);
		if(len(procOut) == 0):
			self.logger.log("ERROR","ERROR PARSING proc/net/dev, LENGHT: 0");
			return(-1);
		procOut = procOut[0].split();
		if(len(procOut) != 11):
			self.logger.log("ERROR","ERROR PARSING proc/stat, LENGHT: " + str(len(procOut)));
			return(-1);
		self.procMetrics.user_cpu = procOut[1]; 	#user cpu
		self.procMetrics.nice_cpu = procOut[2];		#nice cpu
		self.procMetrics.system_cpu = procOut[3];	#system cpu
		self.procMetrics.idle_cpu = procOut[4];		#idle cpu
		self.procMetrics.iowait_cpu = procOut[5];	#iowait cpu
		self.procMetrics.irq_cpu = procOut[6];		#irq cpu
		self.procMetrics.softirq_cpu = procOut[8];	#soft irq cpu
		self.procMetrics.steal_cpu = procOut[8];	#steal cpu
		return(0)

	##This method read data from the /proc/net/dev file
	#it return a string with the content of the file or -1 if there was an error
	def readProcNetDev(self):
		bashCommand = ['adb shell cat /proc/net/dev']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
                  self.logger.log("DEBUG", "READ proc/net/dev DONE");
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR READING proc/net/dev");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);

	##This method parse data from the /proc/net/dev file
	#it register the parsed value in the object procMetric declared in this class
	#it return 0 if all went ok or -1 if there was an error
	# @param procOut = string containing the content of /proc/net/dev file	
	def parseProcNetDev(self,procOut):
		regex = re.compile("eth0:\s+\d+\s+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+");
		procOut = regex.findall(procOut)
		if(len(procOut) == 0):
			self.logger.log("ERROR","ERROR PARSING proc/net/dev, LENGHT: 0");
			return(-1);
		procOut = procOut[0].split()
		if(len(procOut) != 17):
			self.logger.log("ERROR","ERROR PARSING proc/net/dev, LENGHT: " + str(len(procOut)));
			return(-1);
		self.procMetrics.receive_byte = procOut[1];
		self.procMetrics.receive_packet = procOut[2];
		self.procMetrics.transmit_byte = procOut[9];
		self.procMetrics.transmit_packet = procOut[10];
		
	##This method read data from the /proc/[pid]/stat file
	#it return a string with the content of the file or -1 if there was an error	
	def readProcPidStat(self):
		bashCommand = ['adb shell cat /proc/' + str(self.pid) + '/stat']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
                  self.logger.log("DEBUG", "READ proc/pid/stat DONE");
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR READING proc/pid/stat");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);	
	
	##This method parse data from the /proc/[pid]/stat file
	#it register the parsed value in the object procMetric declared in this class
	#it return 0 if all went ok or -1 if there was an error
	# @param procOut = string containing the content of /proc/[pid]/stat file	
	def parseProcPidStat(self,procOut):
           defLen = 0;
           if(self.android_version==4):
               defLen = 47;
           elif(self.android_version==6):
               defLen = 52;
		
           procOut = procOut.split();
           if(len(procOut) != defLen):
               self.logger.log("ERROR","ERROR PARSING proc/pid/stat, LENGHT: " + str(len(procOut)));
               self.procMetrics.state = "0"; 		#status
               self.procMetrics.minflt = "0"; 		#minor fault
               self.procMetrics.cminflt = "0";		#children minor fault
               self.procMetrics.majflt = "0";		#major fault
               self.procMetrics.cmajflt = "0";		#children major fault
               self.procMetrics.utime = "0";			#user time
               self.procMetrics.stime = "0";			#system time
               self.procMetrics.cutime = "0";		#children user time
               self.procMetrics.cstime = "0";		#children system time
               self.procMetrics.numthreads ="0";	#num thread
               self.procMetrics.vss = "0";			#vss
               self.procMetrics.rss = "0";			#rss
               self.procMetrics.processor = "0";		#processor
               return(-1)
		
           self.procMetrics.state = procOut[2]; 		#status
           self.procMetrics.minflt = procOut[9]; 		#minor fault
           self.procMetrics.cminflt = procOut[10];	#children minor fault
           self.procMetrics.majflt = procOut[11];		#major fault
           self.procMetrics.cmajflt = procOut[12];	#children major fault
           self.procMetrics.utime = procOut[13];		#user time
           self.procMetrics.stime = procOut[14];		#system time
           self.procMetrics.cutime = procOut[15];		#children user time
           self.procMetrics.cstime = procOut[16];		#children system time
           self.procMetrics.numthreads = procOut[19];	#num thread
           self.procMetrics.vss = procOut[22];		#vss
           self.procMetrics.rss = procOut[23]			#rss
           self.procMetrics.processor = procOut[38]	#processor
           return(0);

	##This method read data from the /proc/[pid]/statm file
	#it return a string with the content of the file or -1 if there was an error
	def readProcPidStatM(self):
		bashCommand = ['adb shell cat /proc/' + str(self.pid) + '/statm']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
                  self.logger.log("DEBUG", "READ proc/pid/statm DONE");
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR READING proc/pid/statm");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);	

	##This method parse data from the /proc/[pid]/statm file
	#it register the parsed value in the object procMetric declared in this class
	#it return 0 if all went ok or -1 if there was an error
	# @param procOut = string containing the content of /proc/[pid]/statm file	
	def parseProcPidStatM(self,procOut):
		procOut = procOut.split();
		if(len(procOut) != 7):
			self.logger.log("ERROR","ERROR PARSING proc/pid/statm, LENGHT: "+str(len(procOut)));
			self.procMetrics.rmsize = "0"; 		#total size
			self.procMetrics.vmsize = "0";
			self.procMetrics.shared = "0";
			self.procMetrics.text = "0";
			self.procMetrics.data = "0";
			return(-1)
			
		self.procMetrics.rmsize = procOut[0]; 		#total size
		self.procMetrics.vmsize = procOut[1];
		self.procMetrics.shared = procOut[2];
		self.procMetrics.text = procOut[3];
		self.procMetrics.data = procOut[4];

	##This method read data from the files:
	# - /proc/stat 
	# - /proc/net/dev 
	# - /proc/[pid]/stat
	# - /proc/[pid]/statm
	# it return a string with the concatenated content of the file or -1 if there was an error
	def readAll(self):
		bashCommand = ['adb shell cat /proc/stat zz /proc/net/dev zz /proc/'+ \
						str(self.pid)+'/stat zz /proc/'+str(self.pid)+'/statm']
		try:
                  proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
                  #self.logger.log("DEBUG", "READ ALL COMMAND DONE");
                  return(str(proc));
		except subprocess.CalledProcessError as e:
                  self.logger.log("ERROR","ERROR READING FILE IN proc/pid/fd DONE");
                  self.logger.log("ERROR",str(e.output));
                  return(-1);	
		
	##This method parse the concatenated content of files:
	# - /proc/stat 
	# - /proc/net/dev 
	# - /proc/[pid]/stat
	# - /proc/[pid]/statm
	# and it register the parsed value in the object procMetric declared in this class
	# it return a procMetrics object if all went ok
	def measureMetrics(self):
		self.procMetrics.time = str(datetime.now())
		res = self.readAll();
		if(res != -1):
			cmd = res.split("/system/bin/sh: cat: zz: No such file or directory");
			self.procMetrics.error = 0;
			if(self.parseProcStat(cmd[0]) == -1): return(-1);
			if(self.parseProcNetDev(cmd[1]) == -1): return(-1);
			if(self.parseProcPidStat(cmd[2]) == -1): self.procMetrics.error =  self.procMetrics.error +1;
			if(self.parseProcPidStatM(cmd[3]) == -1): self.procMetrics.error =  self.procMetrics.error +1;
			return(self.procMetrics);
		else:
			self.logger.log("ERROR","ERROR READING FROM PROC");
			return(-1)







			
	
	
	
	
	