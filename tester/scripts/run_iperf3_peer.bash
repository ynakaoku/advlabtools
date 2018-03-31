#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-N testname] [-i interval] [-b bandwidth(K|M|G)] [-t time] [-u] [-J] [-M tcp segment size] [-P streams num] [-s]" 1>&2
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
while getopts C:N:i:b:t:uJM:P:sh OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "N")  TESTNAME=$OPTARG ;;
        "i")  INTERVAL=$OPTARG ;;
        "b")  BANDWIDTH=$OPTARG ;;
        "t")  TIME=$OPTARG ;;
        "u")  UDP=true ;;
        "J")  JSON=true ;;
        "M")  MSS=$OPTARG ;;
        "P")  PARALLEL=$OPTARG ;;
        "s")  SILENT=true ;;
        "h")  usage_exit ;;
        \?) usage_exit ;;
    esac
done

# config file existency check.
if [ -f ${WORK_DIR}/${CONFFILE} ]; then
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
OPTIONS_S=""
OPTIONS_C=""

if [ $INTERVAL ]; then
    OPTIONS_S="$OPTIONS_S -i $INTERVAL"
    OPTIONS_C="$OPTIONS_C -i $INTERVAL"
fi

if [ $TIME ]; then
#    OPTIONS_S="$OPTIONS_S -t $(($TIME+5))"
    OPTIONS_C="$OPTIONS_C -t $TIME"
else
    TIME=10
#    OPTIONS_S="$OPTIONS_S -t $(($TIME+5))"
fi

if [ $BANDWIDTH ]; then
    OPTIONS_C="$OPTIONS_C -b $BANDWIDTH"
fi

if $UDP ; then
    OPTIONS_C="$OPTIONS_C -u"
else
    if [ "$proto" = "udp" ] ; then
        OPTIONS_C="$OPTIONS_C -u"
    fi
fi

if $JSON ; then
    OPTIONS_S="$OPTIONS_S -J"
    OPTIONS_C="$OPTIONS_C -J"
fi

if [ $MSS ]; then
    OPTIONS_C="$OPTIONS_C -M $MSS"
fi

if [ $PARALLEL ]; then
    OPTIONS_C="$OPTIONS_C -P $PARALLEL"
fi

if [ $TESTNAME ]; then
    OPTIONS_S="$OPTIONS_S > /tmp/$TESTNAME-sv-$DATE"
    OPTIONS_C="$OPTIONS_C > /tmp/$TESTNAME-cl-$DATE"
else
    echo "Test name is not specified, exit..." 1>&2
    exit 1
fi

echo_switch 'Starting iperf servers on VMs...' $SILENT
for i in $(seq 0 ${max}) ; do
    echo "iperf3 -s $OPTIONS_S" | ssh -T root@"${servers[i]}" &
done
sleep 2

echo_switch 'Executing iperf clients on VMs...' $SILENT
for i in $(seq 0 ${max}) ; do
    echo "iperf3 -c ${testips[i]} $OPTIONS_C" | ssh -T root@"${clients[i]}" &
done
sleep $(($TIME+10))

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

$SCRIPT_DIR/stop_servers.bash -C $CONFFILE > /dev/null

for i in $(seq 0 ${max}) ; do
    if $JSON ; then
        ext="json"
    else
        ext="result"
    fi
    scp root@"${clients[i]}":/tmp/$TESTNAME-cl-$DATE $dirname/$TESTNAME-cl-${clients[i]}.$ext > /dev/null
    scp root@"${servers[i]}":/tmp/$TESTNAME-sv-$DATE $dirname/$TESTNAME-sv-${servers[i]}.$ext > /dev/null
    echo -e "$TESTNAME-cl-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: iperf -c ${testips[i]} $OPTIONS_C" >> $repfile
    echo -e "$TESTNAME-sv-${servers[i]}.$ext : \n  Server: ${servers[i]}\n  Command: iperf -s $OPTIONS_S" >> $repfile
done

if $SILENT ; then
    echo $dirname
fi

echo_switch 'End.' $SILENT
