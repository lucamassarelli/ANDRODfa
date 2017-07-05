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

import subprocess
from Logger import Logger;

##This class implement some functions that are useful to deal with Drebin dataset;

class DrebinUtil:
	
    datasetPath = ""  #PATH DEL DATASET
    testPath    = ""  #PATH DOVE INSERIRE GLI APK OFFUSCATI
    dictionary  = ""  #PATH DEL DICTIONARY
    logLevel = 3;
    __logger = ""
     
    ##The constructor:
    # @param datasetPath = path of the dataset;
    # @param testPath = path of the workspace;
    # @param dictionaryPath = path of the drebin dictionary;
    def __init__(self,datasetPath,testPath,dictionaryPath):
        self.datasetPath = datasetPath;
        self.testPath = testPath;
        self.dictionary = dictionaryPath;
        self.logger = Logger(self.logLevel);

    ##This method read from the dictionary the family of a sample;
    # @param fileName = the name of the sample to find the family  ;  
    def readMalwareFamily(self,fileName):
        bashArray = ["grep",fileName,self.dictionary];
        process = subprocess.Popen(bashArray, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate();
        output = str(output);
        if(error or not output):
            malwareFamily = "UKNOWN";
        else:
            malwareFamilyList = output.split(",");
            malwareFamily = malwareFamilyList[1];
            malwareFamily = malwareFamily.replace("\r"," ");
            malwareFamily = malwareFamily.replace("\n"," ");
            self.logger.log("INFO", "MALWARE FAMILY: " + malwareFamily);
            return(malwareFamily);
        
    ##This method  change the name of a file (used to add .apk extension);
    # @param fileName = the original filename;
    # @param newName = the new name;
    def prepareFile(self,fileName,newName):
        bashCommand = "mv " + self.datasetPath + fileName + " " + self.testPath + newName;
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE);
        output, error = process.communicate();
        if(error):
            self.logger.log("ERROR","ERROR PREPARING APK FILE");
            return(-1);
        else:
            self.logger.log("INFO","ADD APK EXTENSION: " + newName);
            return(0);
		
    
    def cleanBadApk(self,newName,mapName,obfuscatedName,packageName):
        bashCommand = "rm " + self.testPath + newName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","REAL APK REMOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR REMOVING REAL APK");
        bashCommand = "rm " + self.testPath + mapName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","MAP FILE REMOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR REMOVING MAP FILE");
        bashCommand = "rm " + self.testPath + obfuscatedName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","OBFUSCATED APK REMOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR REMOVING OBFUSCATED APK");
		
    def moveGoodApk(self,newName,mapName,obfuscatedName,packageName,goodAPKPath):
        self.logger.log("INFO","THIS APK IS GOOD, MOVING TO NEW LOCATION");
        folder = goodAPKPath + "/" + packageName;
        bashCommand = "mkdir " + folder;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","CREATED DIRECTORY: " + folder);
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR CREATING DIRECTORY: " + folder);
		
        bashCommand = "mv " + self.testPath + newName + " " + folder + "/" + newName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","REAL APK MOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR MOVING REAL APK");
        
        bashCommand = "mv " + self.testPath + mapName + " " + folder + "/" + mapName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","MAP FILE MOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR MOVING MAP FILE");
        
        bashCommand = "mv " + self.testPath + obfuscatedName + " " + folder + "/" + obfuscatedName;
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT, shell=True)
            self.logger.log("INFO","OBFUSCATED APK MOVED");
        except subprocess.CalledProcessError:
            self.logger.log("ERROR","ERROR MOVING OBFUSCATED APK");
  			
