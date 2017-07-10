# Android Malware Family Classification Based on Resource Consumption Metrics Over Time

This project had been used for the paper: 
"Android Malware Family Classification Based on Resource Consumption Metrics"
It contain code to automatically execute malware on genymotion emulator and to collect 
resources consumption metrics during the execution.
It is provided also the code to extract features from collected data and to classify 
malware using it.

The file testedAPKList.txt contains SHA256 of all the apk that have been used in the 
results of the paper.

## Getting Started

To use this code first install all dependencies then download the code and enjoy!
It works on OSX or Linux.

### Prerequisites

#### External tools:

```
Virtual Box: https://www.virtualbox.org
```

```
Genymotion: https://www.genymotion.com
```

```
Android Debug Bridge: https://developer.android.com/studio/command-line/adb.html
```

```
Aapt: https://developer.android.com/studio/command-line/index.html
```

```
Shield4J: http://shield4j.com
```

#### Python package:

```
numpy: http://www.numpy.org
```

```
scipy: http://scipy.org
```

```
sklearn: http://scikit-learn.org/stable/
```

```
matplotlib: https://matplotlib.org
```

```
nolds: https://cschoel.github.io/nolds/nolds.html#
```

```
click: http://click.pocoo.org/5/
```

#### Data:

```
Drebin Dataset: https://www.sec.cs.tu-bs.de/~danarp/drebin/
```


### Installing and Running

- First install all dependencies.

- Download the Drebin dataset.

- Use the module util/WorkspacePreparator.py to create a workspace in which run experiments
  (type "python util/WorkspacePreparator.py --help" for help). This module will prepare a 
  workspace. It will create a folder for each package in the dataset. 

- Use the module LaunchDataExperiment.py to start executing application and collecting data
  (type "python LaunchDataExperiment.py --help" for help). This module will execute n times
  the applications in the workspace. It will create a file with the data of each execution
  in the same folder of the package.

- Use the module LaunchFeatureExtraction.py to extract the feature from the data file in 
  the workspace (type "python LaunchFeatureExtraction.py --help" for help). This will create
  a new file with all the feature from all the execution.

- Use the module LaunchClassification.py to classify the applications 
  (type "python LaunchFeatureExtraction.py --help" for help). It will create a file with 
  the result of the classification.

- Use the module classifier/ClassiferPlotter.py to visualize classification results.


## Built With

* [Python]

## Authors

Luca Massarelli (massarelli@dis.uniroma1.it)

## License

GNU GENERAL PUBLIC LICENSE Version 3.0