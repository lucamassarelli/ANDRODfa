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

import numpy as np
import pickle
from sklearn import preprocessing
import os

## This class handle the loading of the features that can be split in multiple files.
class DataLoader:

	##This method remove nan and inf data
	# It return the cleaned data.
	# @param data = the matrix of data to clean
    def prepareData(self,data):
        a = np.where(np.isinf(data) == True);
        data[a] =  0;
        a = np.where(np.isnan(data) == True);
        data[a] = 0;
        a = np.where(data < 0);
        data[a] = 0
        return(data)
        
	##This method remove bad termination characters from the family name
	# It return the cleaned list of families
	# @param family = list of the family
    def cleanFamilyName(self,family):
        new = []
        for item in family:
            i = item.replace('\\n\'','')
            i = i.rstrip()
            new.append(i)
        return(new)
        
	##This method loads the data from the pickle file created by feature extractor
	# It return a dictionary object with multiple keys:
	# - data: the matrix of feature vectors
	# - package: list of encoded package name
	# - family: list of encoded family
	# - familyEncoder: encoder object for family
	# - packageEncoder: encoder object for package
	# - familyStr: list of family as string
	# - packageStr: list of package as string
	# @param file = name of the file to read
    def loadData(self,file):
        datas = pickle.load( open( file, "rb" ))
        data = datas["featureMatrix"];
        packageStr = datas["packetLabels"];
        familyStr = self.cleanFamilyName(datas["familyLabels"]);
        packageEncoder = preprocessing.LabelEncoder();
        package = packageEncoder.fit_transform(packageStr);
        familyEncoder = preprocessing.LabelEncoder();
        family = familyEncoder.fit_transform(familyStr);
        data = self.prepareData(data.T)
        return({'data':data,'package':package,'family':family,\
                'familyEncoder':familyEncoder,'packageEncoder':packageEncoder,\
                'familyStr':familyStr,'packageStr':packageStr});
                
	##This method merge data loaded from different files
	# It return the same object of load data extended to all data in the dataList
	# @param dataList = list of data object returned by loadData
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
                'familyStr':familyStr,'packageStr':packageStr});

	##This method merge data loaded from different files
	# It return the same object of load data extended to all data in the dataList
	# @param dataList = list of data object returned by loadData
    def loadDataList(self,fileLists):         
        dataLists = []
        for i,filename in enumerate(fileLists):
            if(os.path.isfile(filename)):
                data = self.loadData(filename);
                for j in range(0,len(data["packageStr"])):
                    data["packageStr"][j] += "_"+str(i);
                dataLists.append(data);
            else:
                print("File note found: " + filename)
        if(len(dataLists) > 0):
            datas = self.mergeData(dataLists)
        return(datas);