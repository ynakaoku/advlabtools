#! /bin/bash
#
# Filename: k8s_iperf_peer.bash, part of advlabtools; https://github.com/ynakaoku/advlabtools
# Author: Yoshihiko Nakaoku; ynakaoku@vmware.com

function usage_exit() {
    echo "Usage: $0 [-C config_file] [-N testname] [-i interval] [-b bandwidth(K|M|G)] [-t time] [-u] [-J] [-M tcp segment size] [-P streams num] [-G] [-E] [-s]" 1>&2
    exit 1
}

function echo_switch() {
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
while getopts C:N:i:b:t:uJM:P:sGEh OPT
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
        "G")  SERVER_OUTPUT=true ;;
        "E")  ESXTOP=true ;;
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
        if [ -f ${CONFFILE} ]; then
            . $CONFFILE
        else 
            echo "Config file does not exist, exit..." 1>&2
            exit 1
        fi
    fi
fi

esxlen=${#hosts[@]}
esxmax=$(($esxlen-1))
len=${#servers[@]}
max=$(($len-1))
OPTIONS_S=""
OPTIONS_C=""
OUTPUT_S=""
OUTPUT_C=""
COMMAND_S=""
COMMAND_C=""
OPTIONS_ESX=""

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

if [ $SERVER_OUTPUT ]; then
    OPTIONS_C="$OPTIONS_C --get-server-output"
fi

if [ $TESTNAME ]; then
    OPTIONS_ESX="$OPTIONS_ESX -c esxtop-null.conf -d 5 > /tmp/$TESTNAME-esxtop-$DATE"
else
    echo "Test name is not specified, exit..." 1>&2
    exit 1
fi

if [ $ESXTOP ]; then
    echo_switch 'Starting ESXTOP on hosts...' $SILENT
    for i in $(seq 0 ${esxmax}) ; do
        echo "touch esxtop-null.conf" | ssh root@"${hosts[i]}"
        echo "esxtop $OPTIONS_ESX" | ssh root@"${hosts[i]}" &
    done
fi

echo_switch 'Starting iperf servers on containers...' $SILENT
for i in $(seq 0 ${max}) ; do
    OUTPUT_S="/tmp/$TESTNAME-sv-${servers[i]}-$DATE"
    if [ ${stypes[i]} = "kubernetes" ] ; then
        COMMAND_S="kubectl exec -it ${servers[i]} -n ${snamespaces[i]} -- iperf3 -s $OPTIONS_S"
        $COMMAND_S > $OUTPUT_S &
    else
        COMMAND_S="iperf3 -s $OPTIONS_S"
        echo "$COMMAND_S > $OUTPUT_S" | ssh -T root@"${servers[i]}" &
    fi
done
sleep 2

echo_switch 'Executing iperf clients on VMs...' $SILENT
for i in $(seq 0 ${max}) ; do
    OUTPUT_C="/tmp/$TESTNAME-cl-${clients[i]}-$DATE"
    if [ ${ctypes[i]} = "kubernetes" ] ; then
        COMMAND_C="kubectl exec -it ${clients[i]} -n ${cnamespaces[i]} -- iperf3 -c ${targets[i]} $OPTIONS_C"
        $COMMAND_C > $OUTPUT_C &
    else
        COMMAND_C="iperf3 -c ${targets[i]} $OPTIONS_C"
        echo "$COMMAND_C > $OUTPUT_C" | ssh -T root@"${clients[i]}" &
    fi
done
#sleep $(($TIME+10))
while true
do
    echo_switch 'Checking iperf3 status on instances...' $SILENT
    sleep 5

    ipfstat=false
    for i in $(seq 0 ${max}) ; do
        if [ ${ctypes[i]} = "kubernetes" ] ; then
            pid=$(kubectl exec -it "${clients[i]}" -- pgrep -x iperf3)
            if [ "$pid" ]; then 
                stat=true
            else
                stat=false
            fi
        else
            stat=$(ssh root@"${clients[i]}" 'bash -s' < $SCRIPT_DIR/optlib/iperf3_status_opt.bash)
        fi
        if $stat ; then
            ipfstat=true
        fi
    done
    if ! $ipfstat ; then
        break
    fi
done

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

$SCRIPT_DIR/k8s_stop_servers.bash -C $CONFFILE > /dev/null

if [ $ESXTOP ]; then
    $SCRIPT_DIR/stop_esxtop.bash -C $CONFFILE > /dev/null

    for i in $(seq 0 ${esxmax}) ; do
        scp root@"${hosts[i]}":/tmp/$TESTNAME-esxtop-$DATE $dirname/$TESTNAME-esxtop-${hosts[i]}.csv
        echo -e "$TESTNAME-esxtop-${hosts[i]}.csv : \n  Host: ${hosts[i]}\n  Command: esxtop $OPTIONS_ESX" >> $repfile
    done
fi

for i in $(seq 0 ${max}) ; do
    if $JSON ; then
        ext="json"
    else
        ext="result"
    fi
    if [ ${ctypes[i]} = "kubernetes" ] ; then 
        cp -p /tmp/$TESTNAME-cl-${clients[i]}-$DATE $dirname/$TESTNAME-cl-${clients[i]}.$ext > /dev/null
    else
        scp root@"${clients[i]}":/tmp/$TESTNAME-cl-${clients[i]}-$DATE $dirname/$TESTNAME-cl-${clients[i]}.$ext > /dev/null
    fi
    if [ ${stypes[i]} = "kubernetes" ] ; then 
        cp -p /tmp/$TESTNAME-sv-${servers[i]}-$DATE $dirname/$TESTNAME-sv-${servers[i]}.$ext > /dev/null
    else
        scp root@"${servers[i]}":/tmp/$TESTNAME-sv-{servers[i]}-$DATE $dirname/$TESTNAME-sv-${servers[i]}.$ext > /dev/null
    fi
    echo -e "$TESTNAME-cl-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: iperf -c ${targets[i]} $OPTIONS_C" >> $repfile
    echo -e "$TESTNAME-sv-${servers[i]}.$ext : \n  Server: ${servers[i]}\n  Command: iperf -s $OPTIONS_S" >> $repfile
done

if $SILENT ; then
    echo $dirname
fi

echo_switch 'End.' $SILENT