import matplotlib.pyplot as plt
import pickle
import itertools
import numpy as np


metricsLabel = ["u_cpu","n_cpu","s_cpu","i_cpu","io_cpu","irq_cpu","sirq_cpu","st_cpu",\
				"utime","stime","cutime","cstime", \
				"vss","rss","rmsize","shared", \
				"thread","processor", \
				"min","cmin","maj","cmaj",\
				"receive_byte","receive_packet","transmit_byte","transmit_packet"]

class ClassifierPlotter:


     def plotAccuracyResult(self,fig,axes,rpp,result):
        axes.errorbar(rpp,result["accuracyMean"],result["accuracyStd"]);
        axes.set_xlim([8,32])
        axes.set_ylim([0,1])
        axes.grid()
        ax.set_xlabel('Repetition per package')
        ax.set_ylabel('Accuracy')
        ax.set_title('Accuracy vs repetition per package')
        fig.savefig('Accuracy_RPP.png')
        
        
     def plotStatistic(self,result,classLabels,repNum,prop,classifier):
        N = result["recall"].shape[0];
        #plt.figure();
        fig, ax = plt.subplots();
        plt.tight_layout();
        ind = np.arange(N)      # the x locations for the groups
        width = 1 / (3)         # the width of the bars
        eps = 1/(25)
        
        size = 20
        
        #recall
        if(len(result["recall"].shape)>1):
            recall = np.mean(result["recall"],axis = 1);
            recallStd = np.std(result["recall"],axis = 1);
            for i,r in enumerate(recallStd):
                if(recall[i] + recallStd[i] > 1):
                    recallStd[i] = 1 - recall[i];
            rects1 = ax.bar(ind, recall, width-eps, color='0.8', yerr=recallStd,ecolor="black",hatch="/")
        else:
            rects1 = ax.bar(ind, result["recall"], width-esp, color='w',hatch="/")
        #precision
        ind = ind+width+eps
        if(len(result["precision"].shape)>1):
            precision = np.mean(result["precision"],axis = 1);
            precisionStd = np.std(result["precision"],axis = 1);
            for i,r in enumerate(precisionStd):
                if(precision[i] + precisionStd[i] > 1):
                    precisionStd[i] = 1 - precision[i];
            rects2 = ax.bar(ind, precision, width-eps, yerr=precisionStd,ecolor="black", color='0.6', hatch = ".")
        else:
            rects2 = ax.bar(ind, result["precision"], width-eps, color='w',hatch = ".")
      
#        #f1
#        ind = ind+width
#        if(len(result["f1"].shape)>1):
#            f1 = np.mean(result["f1"],axis = 1);
#            f1Std = np.std(result["f1"],axis = 1);
#            for i,r in enumerate(f1Std):
#                if(f1[i] + f1Std[i] > 1):
#                    f1Std[i] = 1 - f1[i];
#            rects3 = ax.bar(ind, f1, width, color='0.4',ecolor="black", yerr=f1Std,hatch = "\\")
#        else:
#            rects3 = ax.bar(ind, result["f1"], width, color='w',hatch = "\\")
#        #falsePositiveRate
#        ind = ind+width
#        if(len(result["falsePositiveRate"].shape)>1):
#            falsePositiveRate = np.mean(result["falsePositiveRate"],axis = 1);
#            falsePositiveRateStd = np.std(result["falsePositiveRate"],axis = 1);
#            rects4 = ax.bar(ind, falsePositiveRate, width, color='0.2',ecolor="black", yerr=falsePositiveRateStd,hatch = "x")
#        else:
#            rects4 = ax.bar(ind, result["falsePositiveRate"], width, color='0.2',hatch = "x")
    
        ind = np.arange(N)
        #print("{} , {}".format(ind.shape,classLabels.shape))
        ax.set_ylim([0,1.05])
        ax.set_xlim([0,23])
        #ax.set_ylabel('Scores')
        #ax.set_title('{} CLASSIFIER WITH {}, DATA PER PACKAGE: {}'.format(classifier,prop,repNum))
        ax.set_xticks(ind + width)
        ax.set_yticklabels([0,0.2,0.4,0.6,0.8,1],fontsize=size)
        ax.set_xticklabels(classLabels,rotation=45, rotation_mode="anchor",ha='right',fontsize=size);
        #ax.text(0.5, 1.25,'Overall accuracy: \n-Mean: {:10.2f} \n-Std:{:10.2f}'.format(result['accuracyMean'],result['accuracyStd']),ha='left', va='center')
        #ax.set_xticklabels()
        #ax.legend((rects1[0],rects2[0],rects3[0],rects4[0]), ('recall', 'precision','f1score','falsePositiveRate'))
        plt.legend((rects1[0],rects2[0]), \
                   ('recall', 'precision','f1score','falsePositiveRate'),\
                    bbox_to_anchor=(0.0, 1.03, 1., 1.03), loc=3,ncol=2,\
                    mode='right',borderaxespad=0.,fontsize=size)

        fig.savefig('{}_{}_statistic.png'.format(prop,repNum), bbox_inches='tight')
 
        
     def plotFeatureOfFamily(self,ax,datas,family):
        label = datas["family"];
        data = datas["data"];
        a = np.where(label == package);
        features = data[a[0],:];
        mean = np.mean(features,0);
        std = np.std(features,0);
        ax.bar(np.arange(mean.shape[0]), mean, width=0.5, color='r', yerr=std)
        ax.set_title(datas["familyEncoder"].inverse_transform([package])[0],size=18)
        ax.set_ylim([0,2.2])
        ax.set_xlim([0,mean.shape[0]])
        ax.set_xticks(range(0,26));
        ax.set_xticklabels(metricsLabel,rotation=90, rotation_mode="anchor",ha='right',size=14);
        ax.set_ylabel("dfa exponent",size=14)
        
     def plotFeatureOfPackage(self,datas,package):
        label = datas["packetLabels"];
        data = datas["featureMatrix"];
        a = [i for i,x in enumerate(label) if (x == package)]
        features = data[:,a];
        mean = np.mean(features,axis=1);
        std = np.std(features,axis=1);
        plt.bar(np.arange(mean.shape[0]), mean, width=0.5, color='0.8', ecolor = "0", yerr=std)
        #plt.title(datas["familyEncoder"].inverse_transform([package])[0],size=18)
        plt.ylim([0,2.1])
        plt.xlim([0,mean.shape[0]])
        i = np.arange(26) + 0.25
        plt.xticks(i,metricsLabel,rotation=45, rotation_mode="anchor",ha='right',size=14);
        plt.ylabel("Dfa exponent",size=14)
        
     def plotFeatureOfPackageBox(self,datas,package):
        label = datas["packetLabels"];
        data = datas["featureMatrix"];
        a = [i for i,x in enumerate(label) if (x == package)]
        features = data[:,a] - 0.1;
        mean = np.mean(features,axis=1);
        std = np.zeros([26,2])
        #std[:,0] = mean + np.std(features,axis=1)
        #std[:,1] = mean - np.std(features,axis=1)
        i = np.arange(26)
        box = plt.boxplot(features.T, sym = 'o',labels = metricsLabel,patch_artist=True,positions = i, widths = 0.5,whis=1)
        plt.ylim([0,2.0])
        plt.xlim([-1,26])
        plt.grid(linestyle='--', alpha = 0.15)
        i = np.arange(26)
        plt.xticks(i,metricsLabel,rotation=45, rotation_mode="anchor",ha='right',size=20);
        plt.yticks([0,0.5,1,1.5,2],size = 20)
        plt.ylabel("Dfa exponent",size=20)
        for patch in box['boxes']:
            patch.set_facecolor("0.2")
            patch.set_edgecolor("0.2")
            patch.set_linewidth(3)
        for patch in box['whiskers']:
            patch.set_color("0.2")
            patch.set_linestyle("-")
            patch.set_linewidth("1.5")
        for patch in box["caps"]:
            patch.set_color("0.2")
            patch.set_linewidth(2)
        for patch in box["medians"]:
            patch.set_color("0.9");
            patch.set_linewidth(2.5)
        for patch in box["fliers"]:
            patch.set_markerfacecolor("0.2")
        


     def plotAllFeature(self,datas):
        numClass = np.unique(datas["label"]).shape[0];
        if(numClass > 4):
            column = 4;
            row = int(numClass / 4)
        else:
            column = numClass;
            row = 1
            
        f, axar = plt.subplots(row,column)
        for i in range(0,numClass):
            self.logger.log("INFO","PRINTING AXES " + str(i))
            rowIndex = int(math.floor(i/column));
            columnIndex = int(math.fmod(i,column));
            if(row > 1):
                ax = axar[rowIndex,columnIndex]
            elif(column > 1):
                ax = axar[columnIndex]
            elif(column == 1):
                ax = axar
            self.plotFeatureOfPackage(ax,datas,i)
        
     def plot_confusion_matrix(self,cm, classes,normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
        fig = plt.figure(figsize=(15, 15), dpi=80)
        
        print(classes)
        newClasses = []
        for item in classes:
            i = item
            newClasses.append(i)
        print(newClasses)
        classes = newClasses
     
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')
            
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Greys)
        bar = plt.colorbar(ticks=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
        #plt.title(title)
        #plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=90)
        plt.yticks(tick_marks, classes)
        np.set_printoptions(precision=2)
    
        print(cm)
        thresh = cm.max() / 2.
        #for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            #plt.text(j, i, "{:1.2f}".format(cm[i,j]),
            #         horizontalalignment="center",
            #         verticalalignment="center",
            #         color="white" if cm[i, j] > thresh else "black",fontsize=7)
    
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        fig.savefig(title + '.png',bbox_inches='tight')
        
     def plotFromPkl(self,filename):
        datas = pickle.load( open( filename, "rb" ))
        cm = datas["cnf_matrix"];
        classes = datas["classes"];
        self.plot_confusion_matrix(cm, classes,True)
        #self.plotStatistic(datas,classes,'20','dfa','svm')
        #self.plotFeatureOfPackageBox(datas,"com.extend.battery")
        
        
cl = ClassifierPlotter()
#cl.plotFromPkl("std.pkl")
cl.plotFromPkl("exp_finale_svm_0.pkl")