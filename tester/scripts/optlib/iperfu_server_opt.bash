#! /bin/bash
#
RES=$(ps -ef | grep iperf | grep -v grep | awk '{ print $8 }')

if [ "$RES" = "iperf" ] || [ "$RES" = "iperf3" ]; then
    echo "iperf server is already running on the VM."
else
    iperf -D -u -s
fi
