import itertools
import numpy as np

from sklearn.model_selection import cross_val_score
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier
from sklearn import ensemble
from sklearn import gaussian_process

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier,AdaBoostClassifier


class Classifier:
         

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
                          decision_function_shape='ovo',verbose=False,random_state=1234,cache_size=100).\
                          fit(trainData, trainTarget,);
        res = {"svc":bestSvc,"score":scoreMax};
        return(res);

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
        print("ITER: {} ,SCORE: {}".format(n_iter,score))
        svc.fit(trainData, trainTarget);   
        return(svc);
    
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
        return(bestSvc);
    
    def three(self,trainData,trainTarget):
        clf = ensemble.RandomForestClassifier(n_estimators=1000)
        clf = clf.fit(trainData, trainTarget)
        return(clf)
    
    def gaussianProcess(self,trainData,trainTarget):
        gp = gaussian_process.GaussianProcessClassifier();
        gp = gp.fit(trainData,trainTarget);
        return(gp)
    
    def naiveBayesGauss(self,trainData,trainTarget):
        gnb = GaussianNB();
        gnb = gnb.fit(trainData, trainTarget);
        return(gnb);
        
    def linearDiscriminant(self,trainData,trainTarget):
        clf = LinearDiscriminantAnalysis(solver="svd");
        clf.fit(trainData, trainTarget);
        return(clf)
        
    def quadraticDiscriminant(self,trainData,trainTarget):
        clf = QuadraticDiscriminantAnalysis(reg_param=0.1);
        clf.fit(trainData, trainTarget);
        return(clf)
    
    def KNN(self,trainData,trainTarget):
        clf = KNeighborsClassifier(n_neighbors=10, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=1)
        clf.fit(trainData, trainTarget)
        return(clf);
        
    def voting(self,trainData,trainTarget):
        rbf = self.svmRBF(trainData,trainTarget);
        #KNN = self.KNN(trainData,trainTarget);
        gp = self.gaussianProcess(trainData,trainTarget);
        three = self.three(trainData,trainTarget);
        clf = VotingClassifier(estimators=[('rbf', rbf),('gp',gp), ('three', three)], voting='hard')
        clf.fit(trainData,trainTarget)
        return(clf)
    
    def adaBoost(self,trainData,trainTarget):
        svc = self.svmRBF(trainData,trainTarget)
        clf = AdaBoostClassifier(base_estimator=svc,n_estimators=100)
        clf.fit(trainData,trainTarget);
        return(clf)