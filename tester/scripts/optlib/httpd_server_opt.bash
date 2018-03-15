#! /bin/bash
#
RES=$(systemctl status httpd.service | grep Active | grep -v grep | awk '{ print $2 }')

if [ $RES = "active" ]; then
    echo "httpd server is already running on the VM."
else
    systemctl start httpd.service
fi
