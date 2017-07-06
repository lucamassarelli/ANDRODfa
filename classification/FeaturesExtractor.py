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

from DrebinUtil import DrebinUtil
from Logger import Logger
import nolds
import numpy as np
import os
import os.path
import pickle
import re
import traceback;
from joblib import Parallel, delayed
import time


##This class implements features extraction for the data collected during malware
#execution.
#When executed in a workspace this class create a cache. In this way if you want to add 
# more feature it does not require to compute all the old features.

class FeaturesExtractor:
    
    logger = "";
    drebinUtil = "";
    workspacePath = "";
    algorithm = "";
    dataRegexStr = ""
    resObj = ""
    ncpus = 1;
    
	##The constructor
	# @param dictionaryPath = path of the drebin dataset dictionary
	# @param workspacePath = path of the workspace where malware execution data are stored
	# @param algorithm = to use for feature extraction  
	# @param regex = regular expression to select data file
	# @param ncpus = number of cpus to use for feature extraction 
    def __init__(self,dictionaryPath,workspacePath,algorithm,regex,ncpus):
        self.logger = Logger(3);
        self.drebinUtil = DrebinUtil(" "," ",dictionaryPath);
        self.workspacePath = workspacePath;
        self.algorithm = algorithm;
        self.dataRegexStr = regex;
        self.ncpus = ncpus;


	##This methods process the metrics read from data file and prepare them for feature
	# extraction algorithms.
	# It return a matrix with the processed data
	# @param metrics = matrix of the metrics read from the file    
    def prepareMetrics(self,metrics):  
        #u_cpu,n_cpu,s_cpu,i_cpu,io_cpu,irq_cpu,sirq_cpu,st_cpu,utime,stime,cutime,cstime
        cpuData = np.concatenate((metrics[:,range(0,8)],metrics[:,range(16,20)]),axis=1)
        cpuTotal = np.sum(cpuData,axis=1)
        cpuTotalDiff = np.diff(cpuTotal);
        cpuDataDiff = np.diff(cpuData,axis = 0);
        cpuZero = np.where(cpuTotalDiff == 0)
        cpuTotalDiff = np.delete(cpuTotalDiff,cpuZero);
        cpuDataDiff = np.delete(cpuDataDiff,cpuZero,axis=0);
        cpuPerc = np.divide(cpuDataDiff,cpuTotalDiff.reshape(cpuTotalDiff.shape[0],1)\
							.repeat(12,axis=1));
                                                             
        #receive_byte,receive_packet,transmit_byte,transmit_packet
        wifiData = metrics[:,range(8,12)];
        wifiDataDiff = np.diff(wifiData,axis=0);
        wifiDataDiff = np.delete(wifiDataDiff,cpuZero,axis=0);
        
        #thread, processor
        systemData = metrics[:,(20,23)]; 
        systemData = np.delete(systemData,cpuZero,axis=0);
        systemData = np.delete(systemData,0,axis=0);
        
        #vss,rss,rmsize,shared
        memoryData = metrics[:,(21,22,24,26)]; 
        memoryData = np.delete(memoryData,cpuZero,axis=0);
        memoryData = np.delete(memoryData,0,axis=0);
        
        #min,cmin,maj,cmaj
        errorData = metrics[:,(12,13,14,15)];	
        errorData = np.delete(errorData,cpuZero,axis=0);
        errorData = np.delete(errorData,0,axis=0);
        datas = np.concatenate((cpuPerc,memoryData,systemData,errorData,wifiDataDiff),axis=1)
        return(datas);
        
	##This method calculate to percentile resource consumption for cpus metrics
	# It return an array with the percentile of cpu usage for each cpu metrics
	# @param metrics = matrix of the metrics read from the data file	
    def consumption(self,metrics):
        cpuData = np.concatenate((metrics[:,range(0,8)],metrics[:,range(16,20)]),axis=1)
        cpuTotal = np.sum(cpuData,axis=1);
        totalTimeCpu = np.sum(cpuTotal);
        
        ret = np.empty([cpuData.shape[1],1])
        for i in range(0,cpuData.shape[1]):
            ret[i] = np.sum(cpuData[:,i]) / totalTimeCpu; 
        return(ret);
        
	##This method read data registered during application execution
	# It return an object with 3 keys:
	# - data: matrix of the data read
	# - error: true if there was an error reading data
	# - time: timestamp of the each row of the data matrix
	# @param name = name of the file to read
    def readFile(self,name):
        column = list(range(1,13)) + list(range(14,29));
        try:
            my_data = np.genfromtxt(name, delimiter=',',skip_header=3,usecols=column,dtype=float)
            error = False;
        except:
            my_data = np.zeros([27,2])
            error = True;
        
        try:
            rss = np.genfromtxt(name, delimiter=',',skip_header=3,usecols=26,dtype=str)
            for i in range(0,rss.shape[0]):
                rss[i] = rss[i].replace('\\r\\n','')
                my_data[i,24] = int(rss[i])
            error = False;
        except:
            my_data = np.zeros([27,2])
            error = True;
        
        try:
            time = np.genfromtxt(name, delimiter=',',skip_header=3,usecols=[0],dtype=None)
            error = False;
        except:
            time = np.zeros([1,2])
            error = True;    
            
        return({"data":my_data,"error":error,"time":time});
            
	##This method compute the correlation matrix between all the metrics and select the 
	# under diagonal pieces of the matrix.
	# It returns the under diagonal matrix as a one dimensional array
	# @param  data = data matrix to compute correlation
    def correlation(self, data):
        temp = np.corrcoef(data.T)
        numFeat = int(round((temp.shape[0]*temp.shape[0])-temp.shape[0])/2)
        feature = np.zeros([numFeat,1])
        count = 0;
        for i in range(0,temp.shape[0]):
            for j in range(0,temp.shape[0]):
                if(i < j):
                    feature[count] = temp[i,j]
                    count +=1
        return(feature)
        
	##This method handle extraction of the feature with the selected algorithm for a single
	# file.
	# It return an array of features.
	# @param file = name of the file to process
    def processSingleFile(self,file):
        self.logger.log("INFO","EXTRACTING FEATURE {} FROM FILE: {}".format(self.algorithm,file));
         
        res = self.readFile(file);
        
        if(self.algorithm == 'DfaMeanCorr'):
            feature = np.zeros([378,1])
        else:
            feature= np.zeros([26,1]);
                              
        if(res["error"]):
             return(feature);
        if(res["data"].shape[0] == 0):
             return(feature);
        if(res["data"].shape[1] < 10):
             return(feature);
        data = self.prepareMetrics(res["data"]);
        try:
             if(self.algorithm == 'correlation'):
                 feature = self.correlation(data)
                 
             elif(self.algorithm == 'dfa'):
                 feature= np.zeros([26,1]);
                 for i in range(0,data.shape[1]):
                     feature[i] = nolds.dfa(data[:,i]);
                     
             elif(self.algorithm == 'sampen'):
                 feature= np.zeros([26,1]);
                 for i in range(0,data.shape[1]):
                     feature[i] = nolds.sampen(data[:,i],emb_dim=2,\
								  tolerance=0.2*np.std(data[:,i]));
                     
             elif(self.algorithm == 'hurst'):
                 feature= np.zeros([26,1]);
                 for i in range(0,data.shape[1]):
                     feature[i] = nolds.hurst_rs(data[:,i]);
                     
             elif(self.algorithm == 'DfaMeanCorr'):
                 cache_filename = file+".pkl"
                 if(os.path.exists(cache_filename)):
                     self.logger.log("INFO","CACHE FOUND, USING IT")
                     file = open(cache_filename,'rb')
                     cache = pickle.load(file)
                 else:
                     cache = {}
                 if(not "corr" in cache):
                     featureCorr = self.correlation(data)
                     cache["corr"] = featureCorr;
                 else:
                     featureCorr = cache["corr"];
                 if(not "cons" in cache):
                     featureConsump = self.consumption(res["data"])
                     cache["featureConsump"] = featureConsump
                 else:
                     featureConsump = cache["cons"];
                 if(not "dfa" in cache):
                     featureDfa = np.zeros([26,1]);
                     for i in range(0,int(data.shape[1])):
                         featureDfa[i] = nolds.dfa(data[:,i]);
                     cache["dfa"] = featureDfa
                 else:
                     featureDfa = cache["dfa"];
                 if(not "entropy" in cache):
                     featureEntropy = np.zeros([26,1]);
                     for i in range(0,int(data.shape[1])):
                         featureEntropy[i] = nolds.sampen(data[:,i],2);
                     cache["entropy"] = featureEntropy
                 
                 with open(cache_filename, 'wb') as output:
                     pickle.dump(cache, output, pickle.HIGHEST_PROTOCOL)
                 feature = np.vstack([featureDfa,featureConsump,featureEntropy,featureCorr])
                 
        except Exception as e:
            self.logger.log("ERROR","ERROR EXTRACTING FEATURE {} FROM FILE: {}, SKIPPING"\
							.format(self.algorithm,file));
            print(e);
            traceback.print_exc();
            for i in range(0,feature.shape[0]):
                feature[i] = 0;
        return(feature)

	##This method process in parallel using n_cpu all the data file inside the same folder
    # it return the feature matrix in which rows correspond to different file
	# @param path = path of the folder to process    
    def parallelProcessDataFile(self,path):
        N = 0
        files = os.listdir(path);
        regex = re.compile(self.dataRegexStr);
        selectedFiles = []
        for file in files:
            if(regex.match(file) != None):
                selectedFiles.append(file)                
        results = Parallel(n_jobs=self.ncpus)(delayed(self.processSingleFile)(path+file)\
				  for file in selectedFiles)
        if(self.algorithm != "corrcoeff"):
            for feature in results:
                if('featuresMatrix' not in locals()):
                    featuresMatrix = feature;
                else:
                    if(np.sum(feature) != 0 and feature.shape[0] == featuresMatrix.shape[0]):
                        featuresMatrix = np.hstack((featuresMatrix,feature));
                N = featuresMatrix.shape[1]
        else:
            featuresMatrix = results;
            N = len(featuresMatrix)
            
        if('featuresMatrix' in locals()):
            return(featuresMatrix,N)
        else:
            return(np.zeros([1,1]),N)
	
	##This method search in the dictionary the family of a malware inside a single folder
	# then process data inside this folder.
	# It return an object with 3 keys:
	# - featureMatrix: the matrix. in each row there is a feature vector of a malware
	# - packetLabelArray: the array with the name of the package
	# - familyLabelArray: the array with the name of the families	
	# @param path = path of the folder to process
	# @param name = name of the package contained in that folder
    def processPackageFolder(self,path,packetName):
        self.logger.log("INFO","PROCESSING PACKAGE: " + packetName);
        dataFiles = os.listdir(path);
        malwareFamily = "undefined"
        #search for malware family
        for apk in dataFiles:
            regex = re.compile('\w{64}.apk')
            if(regex.match(apk) != None):
                name = apk.split(".")
                self.logger.log("DEBUG",name[0]);
                malwareFamily = self.drebinUtil.readMalwareFamily(name[0]);
        self.logger.log("INFO","MALWARE FAMILY: " + malwareFamily); 
        
        #feature calculation for each data file
        featureMatrix,N = self.parallelProcessDataFile(path)
        
        if(np.all(featureMatrix==0)):
            return({"error":1})

        #labelingData
        packetLabelArray = []
        familyLabelArray = []
        for i in range(0,N):
            packetLabelArray.append(packetName);
            familyLabelArray.append(malwareFamily);

        return({"featureMatrix":featureMatrix,"packetLabel":packetLabelArray,\
				"familyLabel":familyLabelArray})
    
    ## This method handle the process of feature extraction for all the workspace
	# It return on object with three keys:
	# - featureMatrix: the matrix in each row there is a feature vector of a malware
	# - packetLabels: the array with the name of the package
	# - familyLabels: the array with the name of the families
    def extractFeature(self):
        packetLabels = []
        familyLabels = []
        dirs = os.listdir(self.workspacePath);
        for item in dirs:
            if(os.path.isdir(self.workspacePath + item)):
                path = self.workspacePath + item + "/";
                res = self.processPackageFolder(path,item)
                if(not "error" in res):
                    featureMatrix = res["featureMatrix"];
                    packetLabels = packetLabels + res["packetLabel"];
                    familyLabels  = familyLabels + res["familyLabel"];
                    if(self.algorithm == 'corrcoeff'):
                        if('features' not in locals()):
                            features = featureMatrix
                        else:
                            features += featureMatrix
                    else:
                        if('features' not in locals()):
                            features = featureMatrix
                        else:
                            features = np.hstack((features,featureMatrix))
        if('features' not in locals()):
            self.logger.log("ERROR","NOT FOUND ANY DATA....EXITING");
            return({})
        else:
            obj = {"featureMatrix":features,"familyLabels":familyLabels,\
				   "packetLabels":packetLabels}
            self.resObj = obj;
            return(self.resObj)
                        
    ##This method save the result of feature extraction into a file that will be used for 
	# classification.
	# @param filename = name of the file in which save data   
    def saveData(self,filename):
        with open(filename, 'wb') as output:
             pickle.dump(self.resObj, output, pickle.HIGHEST_PROTOCOL)
                    


    
    