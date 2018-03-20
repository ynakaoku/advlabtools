#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-N testname] [-i interval] [-b bandwidth(K|M|G)] [-t time] [-u] [-J] [-s]" 1>&2
    exit 1
}

echo_switch() {
    if [ "$2" = "false" ] ; then
        echo "$1"
    fi
}

WORK_DIR=$(pwd)
REPORT_DIR=$WORK_DIR/reports
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null
UDP=false
JSON=false
SILENT=false
DATE=$(date +%g%m%d-%H%M%S)

# parsing command option.
while getopts C:N:i:b:t:uJsh OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "N")  TESTNAME=$OPTARG ;;
        "i")  INTERVAL=$OPTARG ;;
        "b")  BANDWIDTH=$OPTARG ;;
        "t")  TIME=$OPTARG ;;
        "u")  UDP=true ;;
        "J")  JSON=true ;;
        "s")  SILENT=true ;;
        "h")  usage_exit ;;
        \?) usage_exit ;;
    esac
done

# config file existency check.
if [ -f ${WORK_DIR}/${CONFFILE} ]; then
#    echo $CONFFILE
    . $WORK_DIR/$CONFFILE
else
    if [ -f ${WORK_DIR}/../${CONFFILE} ]; then
        . $WORK_DIR/../$CONFFILE
    else
        echo "Config file does not exist, exit..." 1>&2
        exit 1
    fi
fi

len=${#servers[@]}
max=$(($len-1))
OPTIONS=""

if [ $INTERVAL ]; then
    OPTIONS="$OPTIONS -i $INTERVAL"
fi

if [ $TIME ]; then
    OPTIONS="$OPTIONS -t $TIME"
else
    TIME=10
fi

if [ $BANDWIDTH ]; then
    OPTIONS="$OPTIONS -b $BANDWIDTH"
fi

if $UDP ; then
    OPTIONS="$OPTIONS -u"
else
    if [ "$proto" = "udp" ] ; then
        OPTIONS="$OPTIONS -u"
    fi
fi

if $JSON ; then
    OPTIONS="$OPTIONS -J"
fi
    
if [ $TESTNAME ]; then
    OPTIONS="$OPTIONS > /tmp/$TESTNAME-cl-$DATE"
else
    echo "Test name is not specified, exit..." 1>&2
    exit 1
fi

echo_switch 'Executing iperf3 clients on VMs...' $SILENT
for i in $(seq 0 ${max}) ; do
    echo "iperf3 -c ${testips[i]} $OPTIONS" | ssh -T root@"${clients[i]}" &
done
sleep $(($TIME+5))

echo_switch 'Collecting iperf3 result files...' $SILENT
dirname=$REPORT_DIR/$TESTNAME-iperf3-$DATE
mkdir $dirname
if [ -d $dirname ]; then
    repfile=$dirname/TestReport.txt
    echo "##############################################################################" > $repfile
    echo "Test Report for $dirname" >> $repfile
    echo "##############################################################################" >> $repfile
else
    echo "Report directory creation failed, exit..." 1>&2
    exit 1
fi

for i in $(seq 0 ${max}) ; do
    if $JSON ; then
        ext="json"
    else
        ext="result"
    fi
    scp root@"${clients[i]}":/tmp/$TESTNAME-cl-$DATE $dirname/$TESTNAME-cl-${clients[i]}.$ext
    echo -e "$TESTNAME-cl-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: iperf3 -c ${testips[i]} $OPTIONS" >> $repfile
done

if $SILENT ; then
    echo $dirname
fi

echo_switch 'End.' $SILENT

