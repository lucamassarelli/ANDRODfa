from MalwareClassifier import MalwareClassifier
from DataLoader import DataLoader
from FamilyCorrector import FamilyCorrector
from Classifier import Classifier
import warnings
import pickle
import os

from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import mutual_info_classif

droidScribeFamily = ["Adrd","BaseBridge","DroidDream","DroidKungFu","ExploitLinuxLotoor",\
                     "FakeDoc","FakeInstaller","FakeRun","Gappusin","GinMaster","Glodream",\
                     "Iconosys","Jifake","Kmin","Opfake","Plankton","SMSreg","SendPay",\
                     "Yzhc","MobileTx","Imlog","Boxer","Geinimi"]
                     
warnings.filterwarnings("ignore")
dataLoader = DataLoader();
malwareClassifier = MalwareClassifier();

cacheData = False

if(cacheData and os.path.exists("datas.pkl")):
    print("LOADING DATAS FILE")
    file = open("datas.pkl",'rb')
    datas = pickle.load(file)
    print("DONE")

else:
    print("LOADING DATA ... " )
    datas = dataLoader.loadTesiData();
    print(datas["data"].shape)
    print("DONE")
    
    print("SELECTING FAMILIES ... ")
    datas = malwareClassifier.selDataByFamily(datas,droidScribeFamily)
    print("DONE")
    
    #malwareClassifier.listDataOnFile(datas,"dataList.txt");
    #malwareClassifier.selMeanDataPerPackage(datas)
    
#    print("CORRECTING FAMILIES ... ")
#    familyCorrector = FamilyCorrector();
#    datas = familyCorrector.correctFamily(datas)
#    print("DONE")
    
    filename = "datas.pkl"
    with open(filename, 'wb') as output:
                 pickle.dump(datas, output, pickle.HIGHEST_PROTOCOL)


#
experimentName = "exp_finale_svm";
sampleThreshold = 1;
numOfRepetition = 20;
classifierName = "linear";
#
res = malwareClassifier.prepareAndRunExperiment(datas,sampleThreshold,\
                              numOfRepetition,classifierName, experimentName);