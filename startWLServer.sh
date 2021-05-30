#!/bin/sh
/opt/wls-autoscaling/scripts/startNM.sh
/u01/oracle/product/fmw/oracle_common/common/bin/wlst.sh /opt/wls-autoscaling/scripts/createWLManagedServer.py
