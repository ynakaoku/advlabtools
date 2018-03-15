#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-N testname] [-i interval] [-b bandwidth(K|M|G)] [-t time] [-u] [-y C|c]" 1>&2
    exit 1
}

WORK_DIR=$(pwd)
REPORT_DIR=$WORK_DIR/reports
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null
UDP=false
CSV=false

# parsing command option.
while getopts C:N:i:b:t:uy:h OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "N")  TESTNAME=$OPTARG ;;
        "i")  INTERVAL=$OPTARG ;;
        "b")  BANDWIDTH=$OPTARG ;;
        "t")  TIME=$OPTARG ;;
        "u")  UDP=true ;;
        "y")  if [ $OPTARG = "C" ] || [ $OPTARG = "c" ]; then CSV=true; fi ;;
        "h")  usage_exit ;;
        \?) usage_exit ;;
    esac
done

# config file existency check.
if [ -f ${WORK_DIR}/${CONFFILE} ]; then
#    echo $CONFFILE
    . $WORK_DIR/$CONFFILE
else
    echo "Config file does not exist, exit..."
    exit 1
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

#if [ $REPSTYLE ]; then
#    if [ $REPSTYLE = "C" ] || [ $REPSTYLE = "c" ]; then
#        OPTIONS="$OPTIONS -y C"
#    else
#        echo "Unexpected report style (-y option) is given, exit..."
#        exit 1
#    fi
#fi

if $CSV ; then
    OPTIONS="$OPTIONS -y C"
fi

if [ $TESTNAME ]; then
    OPTIONS="$OPTIONS > /tmp/$TESTNAME"
else
    echo "Test name is not specified, exit..."
    exit 1
fi

echo 'Executing iperf clients on VMs...'
for i in $(seq 0 ${max}) ; do
    echo "iperf -c ${testips[i]} $OPTIONS" | ssh -T root@"${clients[i]}" &
done
sleep $(($TIME+5))

echo 'Collecting iperf result files...'
dirname=$REPORT_DIR/$TESTNAME-iperf-$(date +%g%m%d-%H%M%S)
mkdir $dirname
if [ -d $dirname ]; then 
    repfile=$dirname/TestReport.txt
    echo "##############################################################################" > $repfile
    echo "Test Report for $dirname" >> $repfile
    echo "##############################################################################" >> $repfile
else 
    echo "Report directory creation failed, exit..."
    exit 1
fi

for i in $(seq 0 ${max}) ; do
    if $CSV ; then
        ext="csv"
    else
        ext="result"
    fi
    scp root@"${clients[i]}":/tmp/$TESTNAME $dirname/$TESTNAME-${clients[i]}.$ext
    echo -e "$TESTNAME-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: iperf -c ${testips[i]} $OPTIONS" >> $repfile
done
echo 'End.'
