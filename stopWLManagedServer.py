from java.io import FileInputStream
import sys

sys.path.append("/usr/local/lib/python3.6/site-packages")
sys.path.append('/usr/lib/python3.6/site-packages')

import java.lang
import os
import string
import requests
import json

if len(sys.argv)<1:
   print "Usage  createWLManagedServer.py"
   exit()

propInputStream = FileInputStream("/opt/wls-autoscaling/scripts/managedServer.properties")
configProps = Properties()
configProps.load(propInputStream)

serverUrl = configProps.get("serverUrl")
userName = configProps.get("username")
password = configProps.get("password")
clusterName = configProps.get("clusterName")
msPort = configProps.get("msPort")
msSSLPort =  configProps.get("msSSLPort")

def connectToAdmin():
    connect(userName, password,serverUrl)

def disconnectFromAdmin():
    disconnect()

def getManagedServersList():
    domainConfig()
    svrs = cmo.getServers()
    domainRuntime()
    serverList = []
    for s in svrs:
        serverList.append(s.getName())

    return serverList

def getServerName(machineName):
    nameList = machineName.split("-")
    serverName = ""
    if(len(nameList)>0):
      serverName = nameList[len(nameList)-1]
    return serverName

def createMachine(machineName, hostName):
    domainConfig()
    cd("/")
    mName = getMBean('/Machines/'+machineName)
    print(mName) 
    if(mName == None):
      edit()  
      startEdit()
      try:
        myMachine = cmo.createUnixMachine(machineName)
        if(myMachine):
          myMachine.getNodeManager().setNMType('SSL')  
          myMachine.getNodeManager().setListenAddress(hostName)
        save()  
        activate(block="true")    
      except Exception as e:
        print(e)
        cancelEdit('y')
        undo('true','y')
def createManagedServer(msName,hostName,msPort,msSSLPort,msCluster,msMachine):
    domainConfig()
    cd("/")
    mName = getMBean('/Servers/'+msName)
    if(mName == None): 
      edit()
      startEdit()
      cd('/')
      try:
        myServer = cmo.createServer(msName)
        if(myServer):
          cd('/Servers/'+msName)
          cmo.setListenAddress(hostName)
          cmo.setListenPort(int(msPort))
          
          cd('/Servers/'+msName)
          cmo.setCluster(getMBean('/Clusters/'+msCluster))
          # Enable SSL. Attach the keystore later.
          cd('/Servers/' + msName + '/SSL/' + msName)
          cmo.setEnabled(true)
          cmo.setListenPort(int(msSSLPort))
          # Associated with a node manager.
          cd('/Servers/' + msName)
          cmo.setMachine(getMBean('/Machines/' + msMachine))

          # Manage logging.
          cd('/Servers/' + msName + '/Log/' + msName)
          cmo.setRotationType('byTime')
          cmo.setFileCount(30)
          cmo.setRedirectStderrToServerLogEnabled(true)
          cmo.setRedirectStdoutToServerLogEnabled(true)
          cmo.setMemoryBufferSeverity('Debug')
          cmo.setLogFileSeverity('Notice')
      
        save()
        activate(block="true")
      except Exception as e:
        print(e)
        cancelEdit('y')
        undo('true','y')

def getDomainStatus():
    domainConfig() 
    servers =  cmo.getServers()
    print("\t"+cmo.getName()+" domain current status")
    for server in servers:
        status = state(server.getName(), server.getType())

def startManagedServer(msName):
    domainConfig()
    servers=cmo.getServers()
    domainRuntime()
    for server in servers:
      bean="/ServerLifeCycleRuntimes/"+server.getName()
      serverbean=getMBean(bean)
      if serverbean.getState() in ("SHUTDOWN", "FAILED_NOT_RESTARTABLE") and server.getName()==msName:
	print "Starting the servers which are in SHUTDOWN and FAILED_NOT_RESTARTABLE status"
	print "Starting the Server ",server.getName()
	start(server.getName(),server.getType())

    serverConfig()        


def stopManagedServer(msName):
    servers=cmo.getServers()
    domainRuntime()
    for server in servers:
      bean="/ServerLifeCycleRuntimes/"+server.getName()
      serverbean=getMBean(bean)
      if serverbean.getState() in ("RUNNING") and server.getName()==msName:
        print "Stopping the "+msName+" managed server"
        shutdown(server.getName(),server.getType(),force= "true")

    serverConfig()

def resourceExists(resourceType, resourceName):
    domainConfig()
    cd("/")
    bean="/"+resourceType+"/"+resourceName
    resourceBean = getMBean(bean)
    if(resourceBean!=None):
      return true
    else:
      return false

def deleteServer(serverName):
    domainConfig()
    edit()
    startEdit()
    cd("/")
    cd("/Servers/"+serverName)
    cmo.setCluster(None)
    cmo.setMachine(None)
    editService.getConfigurationManager().removeReferencesToBean(getMBean('/Servers/' + serverName))
    cd("/")
    cmo.destroyServer(getMBean('/Servers/' + serverName))
    activate() 

def deleteMachine(machineName):
    domainConfig()
    edit()
    startEdit()
    editService.getConfigurationManager().removeReferencesToBean(getMBean('/Machines/' + machineName))
    cd("/")
    cmo.destroyMachine(getMBean('/Machines/' + machineName))
    activate()

def getInstanceMetaData():
    headers = {"Authorization":"Bearer Oracle"}
    r = requests.get("http://169.254.169.254/opc/v2/instance/", headers=headers)
    return r.json()


connectToAdmin()

#serverList = getManagedServersList()

#stream = os.popen("hostname")
#machineName = stream.read()

#msNameIndex = getServerName(machineName).rstrip()
#machineName=machineName.rstrip().lstrip()

instanceId = getInstanceMetaData()["id"]


getDomainStatus()
stopManagedServer("WLS-"+instanceId[-5:])

#if(resourceExists("Servers","WLS-"+msNameIndex)):
#  deleteServer("WLS-"+msNameIndex)

#if(resourceExists("Machines","machine-"+msNameIndex)):
#  deleteMachine("machine-"+msNameIndex)
 
disconnectFromAdmin()

