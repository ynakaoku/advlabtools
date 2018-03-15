#! /bin/bash
#
RES=$(ps -ef | grep iperf | grep -v grep | awk '{ print $8 }')

if [ "$RES" = "iperf3" ] || [ "$RES" = "iperf" ]; then
    echo "iperf server is already running on the VM."
else
    iperf3 -D -s
fi
