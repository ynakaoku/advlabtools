#! /bin/bash
#
pid=$(ps -eaf | grep iperf | grep -v grep | awk '{ print $2 }')
if [ "$pid" ]; then 
    kill $pid
fi
stat=$(systemctl status httpd.service | grep Active | awk '{print $2 }')
if [ $stat = "active" ]; then
    systemctl stop httpd.service
fi
