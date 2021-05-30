#!/bin/sh
cp /u01/oracle/config/domains/autoscalingDomain/nodemanager/nodemanager.properties /opt/wls-autoscaling/nodemanager
listenAddress=$(sed -rn 's/^ListenAddress=([^\n]+)$/\1/p' /opt/wls-autoscaling/nodemanager/nodemanager.properties)
newListenAddress=$(hostname)
sed -i "s/$listenAddress/$newListenAddress/g" /opt/wls-autoscaling/nodemanager/nodemanager.properties
currentFolder=$(pwd)

nohup /u01/oracle/config/domains/autoscalingDomain/bin/startNodeManager.sh >/opt/wls-autoscaling/nodemanager/nodemanager.log 2>&1 &

