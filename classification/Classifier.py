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

import itertools
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn import svm
from sklearn.linear_model import SGDClassifier


##This method implements the training of different classifier using cross validation and 
# grid search

class Classifier:         

	##This method train using cross validation an svm model with an rbf kernel.
	#It return an object with two keys:
	# - svc: the trained model
	# - score: score on cross validation of the trained model
	# @param trainData = data for training the model
	# @param trainTarget = label of the training data
    def svmRBF(self,trainData,trainTarget):
        c_grid = [0.1,1,10,100,1000];
        gamma_grid = [0.1,10,100,1000];
        scoreMax = 0;
        bestC = 0;
        bestGamma = 0;
        combinations = list(itertools.product(c_grid,gamma_grid))
        count = 0;
        for C,GAMMA in combinations:
            svc = svm.SVC(kernel='rbf',C=C,gamma=GAMMA,decision_function_shape='ovo');
            score = np.mean(cross_val_score(svc, trainData, trainTarget,cv=5,n_jobs=-1));
            if(score > scoreMax):
                bestC  = C
                bestGamma = GAMMA;
                scoreMax = score
            count += 1;
            #print(str(count));
        bestSvc = svm.SVC(kernel='rbf',C=bestC,gamma=bestGamma,probability=True,\
                          decision_function_shape='ovo',verbose=False,random_state=1234,\
						  cache_size=100).fit(trainData, trainTarget,);
        res = {"svc":bestSvc,"score":scoreMax};
        return(res);

	##This method train using cross validation a linear svm model.
	#It return an object with two keys:
	# - svc: the trained model
	# - score: score on cross validation of the trained model
	# @param trainData = data for training the model
	# @param trainTarget = label of the training data
    def svmLinear(self,trainData,trainTarget):
        print("LINEAR")
        c_grid = [0.1,1,10,50,100,500,1000];
        scoreMax = 0;
        bestC = 0;
        for  C in c_grid:
            svc = svm.SVC(C=C,probability = True);
            score = np.mean(cross_val_score(svc, trainData, trainTarget,cv=5,n_jobs=-1))
            if(score > scoreMax):
                bestC = C;
                scoreMax = score
        bestSvc = svm.LinearSVC(C=bestC).fit(trainData, trainTarget);
        res = {"svc":bestSvc,"score":scoreMax};
        return(res);

	##This method train using cross validation a linear svm model using sub gradient 
	# descend algorithm. (TBD)
	#It return an object with two keys:
	# - svc: the trained model
	# - score: score on cross validation of the trained model
	# @param trainData = data for training the model
	# @param trainTarget = label of the training data
    def sgdSvm(self,trainData,trainTarget):    
        #print("USING SGD SVM")
        n_iter = 1000;
        svc = SGDClassifier(alpha=0.0001, average=False, class_weight=None, epsilon=0.1,\
                               eta0=0.0, fit_intercept=True, l1_ratio=0,\
                               learning_rate='optimal', loss='log', \
                               n_iter=n_iter, n_jobs=2,\
                               penalty='l1', power_t=0.5, random_state=None, \
                               shuffle=True,\
                               verbose=0, warm_start=False)
        score = np.mean(cross_val_score(svc, trainData, trainTarget,cv=5))
        svc.fit(trainData, trainTarget);  
        res = {"svc":bestSvc,"score":score}; 
        return(res);

	##This method train using cross validation a polynomial svm model 
	# It return an object with two keys:
	# - svc: the trained model
	# - score: score on cross validation of the trained model
    def svmPoly(self,trainData,trainTarget):
        c_grid = [0.1,1,10,50,100,500,1000];
        gamma_grid = [0.1,10,50,100,500,1000];
        scoreMax = 0;
        bestC = 0;
        bestGamma = 0;
        combinations = list(itertools.product(c_grid,gamma_grid))
        for C,GAMMA in combinations:
            svc = svm.SVC(kernel='poly',degree=5,C=C,gamma=GAMMA);
            score = np.mean(cross_val_score(svc, trainData, trainTarget,cv=5));
            if(score > scoreMax):
                bestC  = C
                bestGamma = GAMMA;
                scoreMax = score
        bestSvc = svm.SVC(kernel='rbf',C=bestC,gamma=bestGamma).fit(trainData, trainTarget);
        res = {"svc":bestSvc,"score":scoreMax}; 
        return(score);

    ##This method a random forest model 
	# It return an object with two keys:
	# - svc: the trained model
	# - score: in this case is fixed to 1
	# @param n = number of estimators to use in the random forest model
    def randomForest(self,trainData,trainTarget,n):
        clf = ensemble.RandomForestClassifier(n_estimators=n)
        clf = clf.fit(trainData, trainTarget)
        res = {"svc":bestSvc,"score":1};
        return(clf)
    
    
        