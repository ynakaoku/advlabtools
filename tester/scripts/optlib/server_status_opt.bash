#! /bin/bash
#
resp=false
pid=$(ps -eaf | grep iperf3 | grep -v grep | awk '{ print $2 }')
if [ "$pid" ]; then 
    echo "    "[iperf3] running, pid: $pid
    resp=true
else
    pid=$(ps -eaf | grep iperf | grep -v grep | awk '{ print $2 }')
    if [ "$pid" ]; then 
        echo "    "[iperf2] running, pid: $pid
        resp=true
    fi
fi
stat=$(systemctl status httpd.service | grep Active | awk '{print $2 }')
if [ $stat = "active" ]; then
    echo "    "[httpd] active
    resp=true
fi
if ! $resp ; then
    echo "    not running"
fi
address=$(nmcli c show ens160 | grep ipv4.addresses | awk '{print $2 }')
echo "    "[test address] $address
