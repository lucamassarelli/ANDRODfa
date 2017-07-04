from datetime import datetime;
from Logger import Logger;
import subprocess
import threading
import time;

##This class implement an interface with an android device emulator, it supports
# Virtual Box with an AndroidX86 virtual machine or
# Virtual Box with genymotion emulator;
# This class automatically start your VM with 4 cpus, 3 GB of ram 
# and 320px X 480px screen with 160 dpi


class EmulatorInterface:
    playerPath = ""
    VMName = ""
    emulator = ""
    __logger = ""
    geny = "";
    stopBoot= False;
 
    ##The Constructor;
    # @param playerPath = the path of the genymotion player;
    # @VMName = the name of the virtual machine to start;
    # @emulator = the type of emulator to use: "vbox" for virtual box with android_x86
    # or "geny" for genymotion
    def __init__(self,playerPath,VMName,emulator):
        self.playerPath = playerPath;
        self.VMName = VMName;
        self.logger = Logger(1);
        self.emulator = emulator;

    ##This method launch the chosen emulator;    
    def runEmulator(self):
        
        self.logger.log("INFO","LAUNCHING EMULATOR: " + self.emulator)
        
        if(self.emulator == "geny"):
            self.runGenymotion();
        elif(self.emulator == "vbox"):
            self.runVirtualBoxVM();
        else:
            self.logger.log("ERROR","ERROR CHOOSING EMULATOR");
            
    ##This method stops the chose emulator;        
    def stopEmulator(self):
        if(self.emulator == "geny"):
            self.killGenymotion();
        elif(self.emulator == "vbox"):
            self.stopVirtualBoxVM();
            
    ##This method restore a snapshot of the virtual machine;
    # @param snapshotName = name of the snapshot to restore;
    def restoreSnapshot(self,snapshotName):
        bashCommand = ["VBoxManage snapshot " + self.VMName + " restore " +  snapshotName]
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "RESTORE SNAPSHOT DONE");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR RESTORING SNAPSHOT");
            self.logger.log("ERROR",str(e.output));
            return(-1);

    ##This method start the process of the genymotion emulator;	
    def startGenymotion(self):
        bashCommand = "vboxmanage modifyvm {} --memory 3000".format(self.VMName); 
        try:
            proc = subprocess.check_call(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "MODIFY VM -- MEMORY SET");
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR MODIFY VM -- MEMORY SET");
            self.logger.log("ERROR",str(e.output));
        
        bashCommand = "vboxmanage modifyvm {} --cpus 4".format(self.VMName);
        try:
            proc = subprocess.check_call(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "MODIFY VM -- CPUS SET");
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR MODIFY VM -- CPUS SET");
            self.logger.log("ERROR",str(e.output));            
            
        bashCommand =  "vboxmanage guestproperty set {} vbox_graph_mode 320x480-16".format(self.VMName);
        try:
            proc = subprocess.check_call(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "GUEST PROPERTY VM -- VBOX GRAPH MODE");
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR GUEST PROPERTY VM -- VBOX GRAPH MODE");
            self.logger.log("ERROR",str(e.output));
            
        bashCommand =  "vboxmanage guestproperty set {} vbox_dpi 160".format(self.VMName);
        try:
            proc = subprocess.check_call(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "GUEST PROPERTY VM -- VBOX DPI");
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR GUEST PROPERTY VM -- VBOX DPI");
            self.logger.log("ERROR",str(e.output));
        
        bashCommand = self.playerPath + "/player --vm-name " + self.VMName;
        try:
            proc = subprocess.Popen(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "PLAYER START DONE");
            return(proc);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR STARTING PLAYER");
            self.logger.log("ERROR",str(e.output));
            return(-1);
            
             
    def killProcess(self,process):
        process.kill();
        self.logger.log("ERROR","TIMEOUT KILLING PROCESS");
        self.obfError = True;
    
    #T#his method wait for a device to be connected to adb        
    def waitForDevice(self):
        bashCommand = ["adb wait-for-device"]
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "ADB CONNECTED");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR WAITING FOR DEVICE");
            self.logger.log("ERROR",str(e.output));
            return(-1);
            
    ##This method refresh device logcat buffer;			
    def clearBufLogcat(self):
        bashCommand = ["adb shell logcat -c"]
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "LOGCAT BUFFER CLEARED");
            return(0);
        except subprocess.CalledProcessError as e:
            #self.logger.log("ERROR","ERROR CLEANING LOGCAT BUFFER");
            #self.logger.log("ERROR",str(e.output));
            return(-1);
   
    ##This method check if the device has booted and is ready;        
    def checkBootCompleted(self):
        bashCommand = ["adb shell logcat -d | grep BOOT_COMPLETED"]
        try:
            proc = subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "LOGCAT DONE");
            if(proc):
                return(0);
                self.logger.log("VERBOSE DEBUG", "BOOT COMPLETED");
            else:
                self.logger.log("VERBOSE DEBUG", "BOOT NOT COMPLETED");
                return(-1);
        except subprocess.CalledProcessError as e:
  		 #self.logger.log("ERROR","ERROR LOGCAT COMMAND");
  		 #self.logger.log("ERROR",str(e.output));
            return(-1);
            
    ##This method force the adb to connect to localhost:5555;
    def adbConnect(self):
        bashCommand = ["adb connect localhost:5555"]
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "ADB CONNECTED");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR CONNECTING TO DEVICE");
            self.logger.log("ERROR",str(e.output));
            return(-1);
	
    def genymotionThread(self):
        self.geny = self.startGenymotion();
        if(self.geny != -1):
            self.logger.log("DEBUG", "START DONE");
            self.waitForDevice();
            self.clearBufLogcat();
            res = -1
            self.stopBoot = False;
            while(res == -1 and self.stopBoot == False):
                res = self.checkBootCompleted();
                time.sleep(0.1);
               
            
    ##This method run genymotion emulator and wait until device is ready;
    #Timeout is one minute, after that it close the old process and try to 
    #restart genymotion    
    def runGenymotion(self):
        genyThread = threading.Thread(target = self.genymotionThread);
        genyThread.start();
        genyThread.join(120);
        
        if(genyThread.isAlive()):
            genyThread.join(0.150);
            self.logger.log("INFO", "GENYMOTION THREAD TIMEOUT");
            self.stopBoot = True
            self.logger.log("INFO", "RESTARTING GENYMOTION");    
            self.killGenymotion();
            self.runGenymotion();

    ##This method kill genymotion emulator and shutdown virtual machine;                
    def killGenymotion(self):
        self.geny.kill();
        bashCommand = ["VBoxManage controlvm " + self.VMName + " poweroff"]
        try:
            subprocess.check_output(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "STOP VM DONE");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR STOPPING VM");
            self.logger.log("ERROR",str(e.output));
            return(-1);
   
    ##This method start virtual box process;       
    def startVirtualBoxVM(self):
        bashCommand = "vboxmanage startvm " + self.VMName
        try:
            subprocess.call(bashCommand.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE) # continue immediately
            self.logger.log("DEBUG", "VIRTUAL MACHINE START DONE");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR STARTING PLAYER");
            self.logger.log("ERROR",str(e.output));
            return(-1);

    ##This method stop virtual box emulator;        
    def stopVirtualBoxVM(self):
        bashCommand = ["VBoxManage controlvm " + self.VMName + " poweroff"]
        try:
            subprocess.call(bashCommand,stderr=subprocess.STDOUT,shell=True)
            self.logger.log("DEBUG", "STOP VM DONE");
            return(0);
        except subprocess.CalledProcessError as e:
            self.logger.log("ERROR","ERROR STOPPING VM");
            self.logger.log("ERROR",str(e.output));
            return(-1);
           
    ##This method start a virtual machine with android x86 on virtual box and 
    #and wait for the device to be ready, in case of timeout(60 second) it kill
    #old process and try to restart virtual box;        
    def runVirtualBoxVM(self):
        self.logger.log("DEBUG", "STARTING VIRTUAL BOX VM");
        res = self.startVirtualBoxVM();
        if(res == 0):
            self.logger.log("DEBUG", "START DONE");
            self.adbConnect();
            self.waitForDevice();
            #self.clearBufLogcat();
            res = -1
            startTime = datetime.now();
            timeout = False;
            while(res == -1 and not timeout):
                res = self.checkBootCompleted();
                time.sleep(0.1);
                t = datetime.now() - startTime;
                if(t.total_seconds() > 60):
                    timeout = True
                if(not timeout):
                    self.logger.log("VERBOSE DEBUG", "RUN VIRTUAL BOX DONE");
                else:
                    self.logger.log("VERBOSE DEBUG", "RUN VIRTUAL BOX TIMEOUT");
                    self.stopVirtualBoxVM();
                    self.runVirtualBoxVM();
		
		
		
		
		
		
		