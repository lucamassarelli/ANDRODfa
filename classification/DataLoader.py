import numpy as np
import pickle
from sklearn import preprocessing


class DataLoader:

    def prepareData(self,data):
        a = np.where(np.isinf(data) == True);
        data[a] =  0;
        a = np.where(np.isnan(data) == True);
        data[a] = 0;
        a = np.where(data < 0);
        data[a] = 0
        return(data)
    
    def removeClass(self,data,label,family,exclude):
        exclude_matches = []
        for index,l in enumerate(label):
            if(l in exclude):
              exclude_matches.append(index);
        for index,l in enumerate(family):
            if(l in exclude):
              exclude_matches.append(index);
        data = np.delete(data,exclude_matches,axis=1)
        label = [x for index,x in enumerate(label) if index not in exclude_matches]
        family = [x for index,x in enumerate(family) if index not in exclude_matches]
        return(data,label,family)
        
    def cleanFamilyName(self,family):
        new = []
        for item in family:
            i = item.replace('\\n\'','')
            i = i.rstrip()
            new.append(i)
        return(new)
        
        
    def loadData(self,file,exclude=None,selector=None):
        datas = pickle.load( open( file, "rb" ))
        data = datas["featureMatrix"];
        packageStr = datas["packetLabels"];
        familyStr = self.cleanFamilyName(datas["familyLabels"]);
        if(exclude != None):
             data,labelStr,familyStr = self.removeClass(data,packageStr,familyStr,exclude)
        packageEncoder = preprocessing.LabelEncoder();
        package = packageEncoder.fit_transform(packageStr);
        familyEncoder = preprocessing.LabelEncoder();
        family = familyEncoder.fit_transform(familyStr);
        data = self.prepareData(data.T)
        return({'data':data,'package':package,'family':family,\
                'familyEncoder':familyEncoder,'packageEncoder':packageEncoder,\
                'familyStr':familyStr,'packageStr':packageStr});
                
    def mergeData(self,dataList):            
        data = np.concatenate([x["data"] for x in dataList])
        packageStr =  np.concatenate([x["packageStr"] for x in dataList])
        familyStr = np.concatenate([x["familyStr"] for x in dataList])
        familyEncoder = preprocessing.LabelEncoder();
        family = familyEncoder.fit_transform(familyStr);
        packageEncoder = preprocessing.LabelEncoder();
        package = packageEncoder.fit_transform(packageStr);
        return({'data':data,'package':package,'family':family,\
                'familyEncoder':familyEncoder,'packetEncoder':packageEncoder,\
                'familyStr':familyStr,'packetStr':packageStr});

    def loadCorrData(self):           
         clearDataFile0 = "../fromPowerEdge/workspaceDrebinCorr0.pkl"
         clearDataFile1 = "../fromPowerEdge/workspaceDrebinCorr1.pkl"
         clearDataFile2 = "../fromPowerEdge/workspaceDrebinCorr2.pkl"
         clearDataFile3 = "../fromPowerEdge/workspaceDrebinCorr3.pkl"
         clearDataFile4 = "../fromPowerEdge/workspaceDrebinCorr4.pkl"
         clearDataFile5 = "../fromPowerEdge/workspaceDrebinCorr5.pkl"  
         clear0 = self.loadData(clearDataFile0,None,None,[]);
         for i in range(0,len(clear0["packetStr"])):
             clear0["packetStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1,None,None,[]);
         for i in range(0,len(clear1["packetStr"])):
             clear1["packetStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2,None,None,[]);
         for i in range(0,len(clear2["packetStr"])):
             clear2["packetStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3,None,None,[]);
         for i in range(0,len(clear3["packetStr"])):
             clear3["packetStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4,None,None,[]);
         for i in range(0,len(clear4["packetStr"])):
             clear4["packetStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5,None,None,[]);
         for i in range(0,len(clear5["packetStr"])):
             clear5["packetStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4])
         return(datas);
         
    def loadDFAData(self):           
         clearDataFile0 = "../fromPowerEdge/workspaceDrebin0.pkl"
         clearDataFile1 = "../fromPowerEdge/workspaceDrebin1.pkl"
         clearDataFile2 = "../fromPowerEdge/workspaceDrebin2.pkl"
         clearDataFile3 = "../fromPowerEdge/workspaceDrebin3.pkl"
         clearDataFile4 = "../fromPowerEdge/workspaceDrebin4.pkl"
         clearDataFile5 = "../fromPowerEdge/workspaceDrebin5.pkl"  
         clear0 = self.loadData(clearDataFile0,None,None,[]);
         for i in range(0,len(clear0["packetStr"])):
             clear0["packetStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1,None,None,[]);
         for i in range(0,len(clear1["packetStr"])):
             clear1["packetStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2,None,None,[]);
         for i in range(0,len(clear2["packetStr"])):
             clear2["packetStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3,None,None,[]);
         for i in range(0,len(clear3["packetStr"])):
             clear3["packetStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4,None,None,[]);
         for i in range(0,len(clear4["packetStr"])):
             clear4["packetStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5,None,None,[]);
         for i in range(0,len(clear5["packetStr"])):
             clear5["packetStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5])
         
         return(datas);
         
    def loadTesiData(self):           
         clearDataFile0 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin0.pkl"
         clearDataFile1 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin4.pkl"
         clearDataFile5 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin5.pkl"
         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5]);
         #datas = self.mergeData([clear0]);
         return(datas)
    
    def loadTesiDataLocal(self):           
         clearDataFile0 = "workspaceDrebin0.pkl"
         clearDataFile1 = "workspaceDrebin1.pkl"
         clearDataFile2 = "workspaceDrebin2.pkl"
         clearDataFile3 = "workspaceDrebin3.pkl"
         clearDataFile4 = "workspaceDrebin4.pkl"
         clearDataFile5 = "workspaceDrebin5.pkl"
         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5]);
         return(datas)
         
    def loadTesiDataSingle(self):           
         clearDataFile0 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin0.pkl"
         clearDataFile1 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin4.pkl"
         clearDataFile5 = "../../Articolo_Tesi/Dati/espTesi/workspaceDrebin5.pkl"
         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         #datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5]);
         datas = self.mergeData([clear0,clear1]);
         return(datas)
         
    def loadTesi2Data(self):           
         clearDataFile0 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin0.pkl"
         clearDataFile1 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin4.pkl"
         clearDataFile5 = "../../Articolo_Tesi/Dati/espTesi2/workspaceDrebin5.pkl"
         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5]);
         return(datas)
         
    def loadArticoloData(self):
         clearDataFile0 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr0.pkl"
         clearDataFile1 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr4.pkl"
         clearDataFile5 = "../../Articolo_Tesi/Dati/esp1/workspaceDrebinCorr5.pkl"  
         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         datas = self.mergeData([clear0,clear1,clear2,clear3,clear4,clear5])
         return(datas);
         
    def loadMacData(self):
         clearDataFile0 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac0.pkl"
         clearDataFile1 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac4.pkl"
         clearDataFile5 = "../../Articolo_Tesi/Dati/esp1ClearError/workspaceDrebinArtMac5.pkl"
         

         clear0 = self.loadData(clearDataFile0);
         for i in range(0,len(clear0["packageStr"])):
             clear0["packageStr"][i] += "_0";
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
         clear5 = self.loadData(clearDataFile5);
         for i in range(0,len(clear5["packageStr"])):
             clear5["packageStr"][i] += "_5";
         
         datas = self.mergeData([clear1,clear2,clear3,clear4])
         #datas = self.mergeData([clear1,clear2])

         return(datas);
         
    def loadMacDataErr(self):
         clearDataFile1 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtMac1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtMac2.pkl"
         clearDataFile3 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtMac3.pkl"
         clearDataFile4 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtMac4.pkl"
         
         errDataFile1 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtErrMac1.pkl"
         errDataFile2 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtErrMac2.pkl"
         errDataFile3 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtErrMac3.pkl"
         errDataFile4 = "../../Articolo_Tesi/Dati/esp1Mac/workspaceDrebinArtErrMac4.pkl"
         
         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
         clear3 = self.loadData(clearDataFile3);
         for i in range(0,len(clear3["packageStr"])):
             clear3["packageStr"][i] += "_3";
         clear4 = self.loadData(clearDataFile4);
         for i in range(0,len(clear4["packageStr"])):
             clear4["packageStr"][i] += "_4";
             
         err1 = self.loadData(errDataFile1);
         for i in range(0,len(err1["packageStr"])):
             err1["packageStr"][i] += "_1";
         err2 = self.loadData(errDataFile2);
         for i in range(0,len(err2["packageStr"])):
             err2["packageStr"][i] += "_2";
         err3 = self.loadData(errDataFile3);
         for i in range(0,len(err3["packageStr"])):
             err3["packageStr"][i] += "_3";
         err4 = self.loadData(errDataFile4);
         for i in range(0,len(err4["packageStr"])):
             err4["packageStr"][i] += "_4";
             
         datas = self.mergeData([clear1,clear2,clear3,clear4,err1,err2,err3,err4])
         return(datas);
         
    def loadSonyData(self):
         clearDataFile1 = "../../Articolo_Tesi/Dati/espArticolo2/articoloDrebin1.pkl"
         clearDataFile2 = "../../Articolo_Tesi/Dati/espArticolo2/articoloDrebin2.pkl"
         clearDataFile1err = "../../Articolo_Tesi/Dati/espArticolo2/articoloDrebin1err.pkl"
         clearDataFile2err = "../../Articolo_Tesi/Dati/espArticolo2/articoloDrebin2err.pkl"
         

         clear1 = self.loadData(clearDataFile1);
         for i in range(0,len(clear1["packageStr"])):
             clear1["packageStr"][i] += "_1";
         clear2 = self.loadData(clearDataFile2);
         for i in range(0,len(clear2["packageStr"])):
             clear2["packageStr"][i] += "_2";
             
         clear1err = self.loadData(clearDataFile1err);
         for i in range(0,len(clear1err["packageStr"])):
             clear1err["packageStr"][i] += "_1";
         clear2err = self.loadData(clearDataFile2);
         for i in range(0,len(clear2err["packageStr"])):
             clear2err["packageStr"][i] += "_2";
         
         datas = self.mergeData([clear1])
         return(datas);