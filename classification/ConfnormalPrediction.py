from Logger import Logger;
import numpy as np
import os;
import pickle
import random
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.feature_selection import mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectPercentile
from Classifier import Classifier
from pathos.multiprocessing import ProcessingPool
from pathos.parallel import ParallelPool as Pool

class ConfnormalPrediction:
    
    train_x = ' ';
    train_y = ' ';
    model = ' ';
    classes = ' ';
    
    
    def __init__(self,model,train_x,train_y):
        self.model = model;
        self.train_x = train_x;
        self.train_y = train_y;
        self.classes = np.unique(train_y);
        
    def nc_score(self,x,x_pos,model):
        
        nc = 0;
        if(x_pos in model.support_):
            idx = np.where(model.support_ == x_pos)[0][0]
            nc = np.max(abs(model.dual_coef_[:,idx]))
                        
        return(nc)
        
    def p_value(self,obj):
        x = obj["x"]
        y = obj["y"]
        j = obj["j"]
       
        train_x = np.vstack([self.train_x, x])
        x_pos = self.train_x.shape[0]
        train_y = np.hstack([self.train_y, y])
        my_model = self.model
        my_model.fit(train_x, train_y)
        
        nc_x = self.nc_score(x,x_pos,my_model);
        
        nc = []
        for i,item in enumerate(self.train_x):
            if(self.train_y[i] == y):
                nc.append(float(self.nc_score(item,i,my_model)));
        
        count = 0
        for item in nc:
            if(item > nc_x):
                count += 1;
                
        p = count / len(nc)
        
        return(p)

    def predict(self,x):
        n_train = self.train_x.shape[0]
        p = np.zeros([self.classes.size,])
        param = []
        result = []
        for j,cl in enumerate(self.classes):
            param.append({"x":x,"y":cl,"j":j})
            #result.append(self.p_value(param[j]));
        result = ProcessingPool().map(self.p_value, param)
        for i,item in enumerate(result):
            p[i] = item;
        rp = np.copy(p)
        
        label = p.argmax(axis=0)
        credibility = p.max(axis=0)
        p[label] = -np.inf
        confidence = 1 - p.max(axis=0)
        pred = self.classes[label]
        conf_score = np.array([pred, confidence, credibility]).T
        
        return {"pred":rp,"score":conf_score}
        #return(p)
        
    def predictFromPValue(self,p):
        label = p.argmax(axis=0)
        credibility = p.max(axis=0)
        p[label] = -np.inf
        confidence = 1 - p.max(axis=0)
        pred = self.classes[label]
        conf_score = np.array([pred, confidence, credibility]).T
        return conf_score
        
    def predict_confidence(self,p,trueClass):
        idx = np.where(self.classes == trueClass);
        thresh = p[idx]
        upperThresh = p > thresh;
        credibility = p[idx]

        for i,item in enumerate(upperThresh):
            if(item):
                p[i] = -np.inf
        confidence = 1 - p.max(axis=0)
        
        pred = trueClass
        conf_score = np.array([pred, confidence, credibility]).T
        return conf_score
        
    def predict_confidence_threshold(self,p,threshold):
        upperThresh = p > threshold;
        label = p.argmax(axis=0)
        pred = p.argmax(axis=0)
        credibility = p.max(axis=0)

        for i,item in enumerate(upperThresh):
            if(item):
                p[i] = -np.inf
        confidence = 1 - p.max(axis=0)
        
        conf_score = np.array([pred, confidence, credibility]).T
        
        pred_set = []
        for i,item in enumerate(upperThresh):
            if(item):
                pred_set.append(self.classes[i]);
        
        return {"score":conf_score,"pred":pred_set,"label":label}