#! /bin/bash
#
pid=$(pgrep -x iperf3 | awk '{ print $1 }')
if [ "$pid" ]; then 
    echo true
else
    echo false
fi
