#!/bin/sh
sudo mount 172.17.3.249:/wl-filesystem /u01/oracle
/opt/wls-autoscaling/scripts/startWLServer.sh
