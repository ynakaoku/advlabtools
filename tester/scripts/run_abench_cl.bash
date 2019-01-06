#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-N testname] [ -n total requests ] [ -c concurency ] [-t timelimit] [-s]" 1>&2
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
while getopts C:N:n:c:i:b:t:uJsh OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "N")  TESTNAME=$OPTARG ;;
        "n")  NUMBER=$OPTARG ;;
        "c")  CONCUR=$OPTARG ;;
        "t")  TIME=$OPTARG ;;
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

esxlen=${#hosts[@]}
esxmax=$(($esxlen-1))
ablen=${#clients[@]}
abmax=$(($ablen-1))
OPTIONS=""
OPTIONS_ESX=""

if [ $NUMBER ]; then
    OPTIONS="$OPTIONS -n $NUMBER"
fi

if [ $CONCUR ]; then
    OPTIONS="$OPTIONS -c $CONCUR"
fi

if [ $TIME ]; then
    OPTIONS="$OPTIONS -t $TIME"
else
    TIME=10
fi

if [ $TESTNAME ]; then
    OPTIONS="$OPTIONS > /tmp/$TESTNAME-ab-$DATE"
    OPTIONS_ESX="$OPTIONS_ESX -c esxtop-null.conf -d 5 > /tmp/$TESTNAME-esxtop-$DATE"
else
    echo "Test name is not specified, exit..." 1>&2
    exit 1
fi

echo_switch 'Starting ESXTOP on hosts...' $SILENT
for i in $(seq 0 ${esxmax}) ; do
    echo "touch esxtop-null.conf" | ssh root@"${hosts[i]}"
    echo "esxtop $OPTIONS_ESX" | ssh root@"${hosts[i]}" &
done
sleep 2

echo_switch 'Executing Apache Bench on VMs...' $SILENT
for i in $(seq 0 ${abmax}) ; do
    echo "ab $OPTIONS http://${testips[i]}/" | ssh -T root@"${clients[i]}" &
done

while true
do
    echo_switch 'Checking Apache Bench status on VMs...' $SILENT
    sleep 5

    abstat=false
    for i in $(seq 0 ${abmax}) ; do
        stat=$(ssh root@"${clients[i]}" 'bash -s' < $SCRIPT_DIR/optlib/abench_status_opt.bash)
        if $stat ; then
            abstat=true
        fi
    done
    if ! $abstat ; then
        break
    fi
done


echo_switch 'Collecting Apache Bench and ESXTOP result files...' $SILENT
dirname=$REPORT_DIR/$TESTNAME-ab-$DATE
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

$SCRIPT_DIR/stop_esxtop.bash -C $CONFFILE > /dev/null

for i in $(seq 0 ${esxmax}) ; do
    scp root@"${hosts[i]}":/tmp/$TESTNAME-esxtop-$DATE $dirname/$TESTNAME-esxtop-${hosts[i]}.csv
    echo -e "$TESTNAME-esxtop-${hosts[i]}.csv : \n  Host: ${hosts[i]}\n  Command: esxtop $OPTIONS_ESX" >> $repfile
done

for i in $(seq 0 ${abmax}) ; do
    if $JSON ; then
        ext="json"
    else
        ext="result"
    fi
    scp root@"${clients[i]}":/tmp/$TESTNAME-ab-$DATE $dirname/$TESTNAME-ab-${clients[i]}.$ext
    echo -e "$TESTNAME-ab-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: ab $OPTIONS http://${testips[i]}/" >> $repfile
done

if $SILENT ; then
    echo $dirname
fi

echo_switch 'End.' $SILENT

