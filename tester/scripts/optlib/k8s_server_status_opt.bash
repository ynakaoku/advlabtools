#! /bin/bash
#
# Filename: k8s_server_status_opt.bash, part of advlabtools; https://github.com/ynakaoku/advlabtools
# Author: Yoshihiko Nakaoku; ynakaoku@vmware.com

resp=false
pid=$(kubectl exec -it $1 -- ps -eaf | grep iperf3 | grep -v grep | awk '{ print $2 }')
if [ "$pid" ]; then 
    echo "    "[iperf3] running, pid: $pid
    resp=true
else
    pid=$(kubectl exec -it $1 -- ps -eaf | grep iperf | grep -v grep | awk '{ print $2 }')
    if [ "$pid" ]; then 
        echo "    "[iperf2] running, pid: $pid
        resp=true
    fi
fi
pid=$(kubectl exec -it $1 -- ps -eaf | grep httpd | grep -v grep | awk '{print $2 }')
if [ "$pid" ]; then
    echo "    "[httpd] running, pid: $pid
    resp=true
fi
if ! $resp ; then
    echo "    not running"
fi
address=$(kubectl get pod $1 -o=jsonpath='{.spec.hostname}')
echo "    "[target] $address