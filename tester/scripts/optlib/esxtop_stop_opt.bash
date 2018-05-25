#! /bin/bash
#
pid=$(ps | grep esxtop | grep -v grep | awk '{ print $1 }')
if [ "$pid" ]; then 
    kill $pid
fi
