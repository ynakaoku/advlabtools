#! /bin/bash
#
pid=$(pgrep -x ab | awk '{ print $1 }')
if [ "$pid" ]; then 
    echo true
else
    echo false
fi
