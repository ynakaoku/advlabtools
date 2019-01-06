#! /bin/bash
#
# Filename: k8s_server_stop_opt.bash, part of advlabtools; https://github.com/ynakaoku/advlabtools
# Author: Yoshihiko Nakaoku; ynakaoku@vmware.com

pid=$(kubectl exec -it $1 -- ps -eaf | grep iperf | grep -v grep | awk '{ print $2 }')
if [ "$pid" ]; then 
    kubectl exec -it $1 -- kill $pid
fi
pid=$(kubectl exec -it $1 -- ps -eaf | grep httpd | grep -v grep | awk '{print $2 }')
if [ "$pid" ]; then
    kubectl exec -it $1 -- kill $pid
fi
