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

import sys
sys.path.insert(0,"util/")
sys.path.insert(0,"classification/")

from MalwareClassifier import MalwareClassifier
from DataLoader import DataLoader
from Classifier import Classifier
import warnings
import pickle
import os
import click
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import mutual_info_classif

droidScribeFamily = ["Adrd","BaseBridge","DroidDream","DroidKungFu","ExploitLinuxLotoor",\
                     "FakeDoc","FakeInstaller","FakeRun","Gappusin","GinMaster","Glodream",\
                     "Iconosys","Jifake","Kmin","Opfake","Plankton","SMSreg","SendPay",\
                     "Yzhc","MobileTx","Imlog","Boxer","Geinimi"]
                     

@click.command()
@click.option('--f',default="",help='Data file to use. Use multiple times to load multiple files',multiple=True)
@click.option('--experimentname', default="",help='Name of the experiment, used for saving results')
@click.option('--algorithm', default="",help="algorithm for classification: \
											  'linear':linear svm\n \
											  'sgdSvm': linear svm with sgd\n \
											  'rbf': non linear svm with rbf kernel\n \
											  'poly': non linear svm with 3 poly kernel\n \
											  'forest': random forest classifier\n")
@click.option('--repetition',type=int, default="",help='number of experiment repetition')
@click.option('--threshold',type=int,default=0,help="threshold for selecting families. If == 0 use same family as droidscribe")

def mymain(f,experimentname,repetition,algorithm,threshold):
	warnings.filterwarnings("ignore")
	dataLoader = DataLoader();
	malwareClassifier = MalwareClassifier();
	datas = dataLoader.loadDataList(f);
	if(threshold == 0):
		datas = malwareClassifier.selDataByFamily(datas,droidScribeFamily)
	else:
		datas = malwareClassifier.cleanClass(datas,threshold)
	res = malwareClassifier.prepareAndRunExperiment(datas,repetition,algorithm,experimentname);



if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mymain();