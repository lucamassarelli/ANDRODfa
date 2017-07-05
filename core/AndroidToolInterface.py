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

from Logger import Logger;
import subprocess
import threading;


##This class implements android debug bridge interface to install, obfuscate,
#execute and uninstall an android apk. \n
#N.B. the adb has to be already connected to a device before to call any method
#of this class;     

class AndroidToolInterface:
    
    logLevel = 3;
    __logger = "";           
    __monkeyProcess = 0;
    __obfError = False;

     

    ##the constructor
    def __init__(self):
        self.logger = Logger(self.logLevel);
  
    ##This method finds the package name given an apk file, it use aapt utility;
    # @param fileName = The name of the apk to investigate;
    def findPackageName(self,fileName):
         bashCommand = "aapt dump badging " + fileName + " |grep package";
         try:
              proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
              commandSplit = str(proc).split();
              if(len(commandSplit) >= 2):
                  name = commandSplit[1].split("=");
                  if(len(name) >= 2):
                          name = name[1].replace("'","");
                  else:
                          self.logger.log("ERROR","ERROR RETRIEVING PACKAGE NAME: " + fileName);
                          return(-1)
              else:
                  self.logger.log("ERROR","ERROR RETRIEVING PACKAGE NAME: " + fileName);
                  return(-1)
              self.logger.log("INFO","FIND PACKAGE NAME: " + name);
              return(name);
         except subprocess.CalledProcessError:
             self.logger.log("ERROR","ERROR CALLING AAPT");
             return(-1);
             
    def killProcess(self,process):
        process.kill();
        self.logger.log("ERROR","OBFUSCATOR TIMEOUT");
        self.obfError = True;
		
    ##This method implements an interface to use shield4J obfuscator to 
    #obfuscate an apk file.
    # @param fileName = the apk to obfuscate;
    # @param obfuscatedName = the name of the obfuscate apk;
    # @param mapName = the name of the mapping file;
    # @param obfuscatorPath = the path to shield4J jar file;
    def makeObfuscation(self,fileName,obfuscatedName,mapName,obfuscatorPath):
        self.logger.log("INFO","STARTING OBFUSCATION: " + fileName);
        baseCmd = "java -Xms512m -Xmx768m  -jar " + obfuscatorPath + "shield4j-1.0.5-beta.jar"
        inCmd   = " --in " + fileName;
        outCmd  = " --out " + obfuscatedName;
        mapCmd  = " --mappingFile " + mapName;
        signCmd = " --signingMode DEMO_KEYS"
        bashCommand = baseCmd + inCmd + outCmd + mapCmd + signCmd;
        
        try:
            self.obfError = False;
            proc = subprocess.Popen(bashCommand,stderr=subprocess.STDOUT, shell=True)
            timer = threading.Timer(60,self.killProcess,args=[proc])
            timer.start();
            proc.wait();    
        except subprocess.CalledProcessError as e:
            print(e)
            self.logger.log("ERROR","ERROR OBFUSCATING FILE: " + fileName);
            return(-1);
        
        timer.cancel();    
        (proc,err) = proc.communicate();
        
        if("error" in str(proc)):
            self.logger.log("ERROR","ERROR OBFUSCATING FILE: " + fileName);
            return(-1);
        if(self.obfError):
            self.logger.log("ERROR","ERROR OBFUSCATING FILE: " + fileName);
            return(-1);
        
        self.logger.log("INFO","OBFUSCATION COMPLETED: " + fileName);
        return(0);
			
    ##This method install an apk to the connected device:
    # @param fileName = name of apk to install;
    def installAPK(self,fileName):
        self.logger.log("INFO","INSTALLING APK: " + fileName);	
        bashCommand = "adb install " + fileName;
        try:
            subprocess.check_call(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO", "APK CORRECTLY INSTALLED: " + fileName);
            return(0);
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR INSTALLING APK");
            return(-1);		
    
    ##This method read the package name from a shield4j map file
    # @param mapName = name of the map file;        
    def readPackageNameFromMap(self,mapName):
        self.logger.log("INFO","READING MAPPING FILE");
        bashArray = ["grep","Current Manifest package attribute:",mapName];
        process = subprocess.Popen(bashArray, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output, error = process.communicate();
        if(error):
            self.logger.log("ERROR","ERROR READING MAPPING FILE");
            return(-1)
        else:
            res = output.split(":");
		 #VERIFICO CHE RES ABBIA DIMENSIONE DUE
            if(len(res) != 2):
                self.logger.log("ERROR","ERRORE NELLA DIMENSIONE DI RES");
                return(-1);
            else:	
                packageName = res[1];
                packageName = packageName.replace("\r"," ");
                packageName = packageName.replace("\n"," ");
                self.logger.log("INFO","FOUND PACKAGE NAME: " + packageName);
                return(packageName);
            
                
    ##This method start the execution of a packet with monkey tool; 
    #N.B. the packet has to be already installed;
    # @param packageName = the name of the package to run;
    # @param monkeyOption = the option for monkey tool;
    def runApplication(self,packageName,monkeyOption):
        self.logger.log("INFO","STARTING APPLICATION: " + packageName);
        bashCommand = "adb shell monkey -p " +  packageName + " " + monkeyOption;
        try:
            monkeyProcess = subprocess.Popen(bashCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
            monkeyProcess.wait();
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR LAUNCHING APPLICATION");
            return(-1);   
            
        (proc,err) = monkeyProcess.communicate();

	   #catch no activity error 	
        if("No activities found to run, monkey aborted" in str(proc)):
            self.logger.log("ERROR","MONKEY ERROR NO ACTIVITY FOUND");
            self.logger.log("DEBUG",str(proc));
            return(-1);
            
	   #catch running error	
        if("aborted" in str(proc)):
            proc = str(proc).split("\n");
            for substr in proc :
                if("Events injected: " in substr):
                    errEvent = substr;
                    errEvent = errEvent.split(": ");
            self.logger.log("ERROR","ERROR LAUNCHING APPLICATION");
            return(-1);	
            
        self.logger.log("DEBUG","MONKEY STARTED: " + packageName);
        return(0);
        
    ##This method kill the process that was started with runApplication method;    
    def killMonkey(self):
        if(self.monkeyProcess != 0):
            self.monkeyProcess.kill();
	
    ##This method force the stop of a package that is running;
    # @param packageName = the name of the package to close;
    def closeApplication(self,packageName):
        self.logger.log("INFO","ENDING APPLICATION: " + packageName);
        bashCommand = "adb shell am force-stop" +  packageName;
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE,stderr=subprocess.PIPE);
        output, error = process.communicate();
        if(error):
            self.logger.log("ERROR","ERROR CLOSING APPLICATION " + packageName);
            return(-1);
        else:
            self.logger.log("INFO","APPLICATION CLOSED: " + packageName);
            return(0);
    
    #This method remove from the device a specific package;
    # @param packageName = the name of the package to remove;
    def uninstallApplication(self,packageName):
         self.logger.log("INFO","UNINSTALLING APPLICATION"); 
         bashCommand = "adb uninstall " +  packageName;
         try:
             subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
         except subprocess.CalledProcessError:
  			# There was an error - command exited with non-zero cod
              self.logger.log("ERROR","ERROR UNINSTALLING APPLICATION");
              return(-1);
		
			
	