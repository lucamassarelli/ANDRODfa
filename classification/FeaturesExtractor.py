import click
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
import warnings

import time



class FeaturesExtractor:
    
    logger = "";
    drebinUtil = "";
    workspacePath = "";
    algorithm = "";
    dataRegexStr = ""
    resObj = ""
    ncpus = 1;
    
    def __init__(self,dictionaryPath,workspacePath,algorithm,regex,ncpus):
        self.logger = Logger(3);
        self.drebinUtil = DrebinUtil(" "," ",dictionaryPath);
        self.workspacePath = workspacePath;
        self.algorithm = algorithm;
        self.dataRegexStr = regex;
        self.ncpus = ncpus;
        
    def prepareMetrics(self,metrics):  
        #u_cpu,n_cpu,s_cpu,i_cpu,io_cpu,irq_cpu,sirq_cpu,st_cpu,utime,stime,cutime,cstime
        cpuData = np.concatenate((metrics[:,range(0,8)],metrics[:,range(16,20)]),axis=1)
        cpuTotal = np.sum(cpuData,axis=1)
        cpuTotalDiff = np.diff(cpuTotal);
        cpuDataDiff = np.diff(cpuData,axis = 0);
        cpuZero = np.where(cpuTotalDiff == 0)
        cpuTotalDiff = np.delete(cpuTotalDiff,cpuZero);
        cpuDataDiff = np.delete(cpuDataDiff,cpuZero,axis=0);
        cpuPerc = np.divide(cpuDataDiff,cpuTotalDiff.reshape(cpuTotalDiff.shape[0],1).repeat(12,axis=1));
                                                             
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
        
    def consumption(self,metrics):
        cpuData = np.concatenate((metrics[:,range(0,8)],metrics[:,range(16,20)]),axis=1)
        cpuTotal = np.sum(cpuData,axis=1);
        totalTimeCpu = np.sum(cpuTotal);
        
        ret = np.empty([cpuData.shape[1],1])
        for i in range(0,cpuData.shape[1]):
            ret[i] = np.sum(cpuData[:,i]) / totalTimeCpu; 
        return(ret);
        
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
                     feature[i] = nolds.sampen(data[:,i],emb_dim=2, tolerance=0.2*np.std(data[:,i]));
                     
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
            self.logger.log("ERROR","ERROR EXTRACTING FEATURE {} FROM FILE: {}, SKIPPING".format(self.algorithm,file));
            print(e);
            traceback.print_exc();
            for i in range(0,feature.shape[0]):
                feature[i] = 0;
        return(feature)

        
    def parallelProcessDataFile(self,path):
        N = 0
        files = os.listdir(path);
        regex = re.compile(self.dataRegexStr);
        selectedFiles = []
        for file in files:
            if(regex.match(file) != None):
                selectedFiles.append(file)                
        results = Parallel(n_jobs=self.ncpus)(delayed(self.processSingleFile)(path+file) for file in selectedFiles)
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

        return({"featureMatrix":featureMatrix,"packetLabel":packetLabelArray,"familyLabel":familyLabelArray})
    
    
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
            obj = {"featureMatrix":features,"familyLabels":familyLabels,"packetLabels":packetLabels}
            self.resObj = obj;
            return(self.resObj)
                        
        
    def saveData(self,filename):
        with open(filename, 'wb') as output:
             pickle.dump(self.resObj, output, pickle.HIGHEST_PROTOCOL)       
             
    def extractConsumptionOfFamily(self,family):
        dirs = os.listdir(self.workspacePath);
        for item in dirs:
            if(os.path.isdir(self.workspacePath + item)):
                path = self.workspacePath + item + "/";
                #self.logger.log("INFO","PROCESSING PACKAGE: " + packetName);
                dataFiles = os.listdir(path);
                malwareFamily = "undefined"
                #search for malware family
                for apk in dataFiles:
                    regex = re.compile('\w{64}.apk')
                    if(regex.match(apk) != None):
                        name = apk.split(".")
                        self.logger.log("DEBUG",name[0]);
                        malwareFamily = self.drebinUtil.readMalwareFamily(name[0]);
                        if(malwareFamily == family):
                            files = os.listdir(path);
                            regex = re.compile(self.dataRegexStr);
                            for file in files:
                                if(regex.match(file) != None):
                                    res = self.readFile(path+file);
                                    if(not res["error"]):
                                        res = self.consumption(res["data"]);
                                        if('resMatrix' not in locals()):
                                            resMatrix = res;
                                        else:
                                            resMatrix = np.hstack([resMatrix,res])
        return(resMatrix)
                    

@click.command()
@click.option('--dictionarypath', default="", help='Path of Drebin Dataset Dictionary')
@click.option('--workspacepath', default="",help='Path of framework workspace')
@click.option('--algorithm', default="",help='Feature extraction algorithm: sampen,dfa')
@click.option('--filename', default="",help='filename for saving feature (optional)')
@click.option('--regex',default="\w*5000_result_\d+.csv",help='regex for file name')
@click.option('--ncpus',default=1,help='number of cpus for parallel processing')
#@click.argument('dictionaryPath',required=1)
def mymain(dictionarypath,workspacepath,algorithm,filename,regex,ncpus):
    featuresExtractor = FeaturesExtractor(dictionarypath,workspacepath,algorithm,regex,ncpus);
    featuresExtractor.extractFeature();
    featuresExtractor.saveData(filename);


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    dictionarypath = "/Users/lucamassarelli/Documents/CloudStation/TESI/workspace/dataset/drebin-0/dictionary.txt"
    workspacepath = "/Users/lucamassarelli/Documents/CloudStation/TESI/workspace/std/"
    algorithm = "dfa"
    regex = "\w*5000_result_\d+.csv"
    ncpus = 4
    
    featuresExtractor = FeaturesExtractor(dictionarypath,workspacepath,algorithm,regex,ncpus);
    #res = featuresExtractor.extractConsumptionOfFamily("DroidKungFu\\n\'")
    featuresExtractor.extractFeature();
    featuresExtractor.saveData("std.pkl");
    
    
    
    #mymain()
    
    