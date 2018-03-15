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
DATE=$(date +%g%m%d-%H%M%S)

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
OPTIONS_S=""
OPTIONS_C=""

if [ $INTERVAL ]; then
    OPTIONS_S="$OPTIONS_S -i $INTERVAL"
    OPTIONS_C="$OPTIONS_C -i $INTERVAL"
fi

if [ $TIME ]; then
    OPTIONS_S="$OPTIONS_S -t $(($TIME+5))"
    OPTIONS_C="$OPTIONS_C -t $TIME"
else
    TIME=10
    OPTIONS_S="$OPTIONS_S -t $(($TIME+5))"
fi

if [ $BANDWIDTH ]; then
    OPTIONS_C="$OPTIONS_C -b $BANDWIDTH"
fi

if $UDP ; then
    OPTIONS_S="$OPTIONS_S -u"
    OPTIONS_C="$OPTIONS_C -u"
else
    if [ "$proto" = "udp" ] ; then
        OPTIONS_S="$OPTIONS_S -u"
        OPTIONS_C="$OPTIONS_C -u"
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
    OPTIONS_S="$OPTIONS_S -y C"
    OPTIONS_C="$OPTIONS_C -y C"
fi

if [ $TESTNAME ]; then
    OPTIONS_S="$OPTIONS_S > /tmp/$TESTNAME-sv-$DATE"
    OPTIONS_C="$OPTIONS_C > /tmp/$TESTNAME-cl-$DATE"
else
    echo "Test name is not specified, exit..."
    exit 1
fi

echo 'Starting iperf servers on VMs...'
for i in $(seq 0 ${max}) ; do
    echo "iperf -s $OPTIONS_S" | ssh -T root@"${servers[i]}" &
done
sleep 2

echo 'Executing iperf clients on VMs...'
for i in $(seq 0 ${max}) ; do
    echo "iperf -c ${testips[i]} $OPTIONS_C" | ssh -T root@"${clients[i]}" &
done
sleep $(($TIME+10))

echo 'Collecting iperf result files...'
dirname=$REPORT_DIR/$TESTNAME-iperf-$DATE
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
    scp root@"${clients[i]}":/tmp/$TESTNAME-cl-$DATE $dirname/$TESTNAME-cl-${clients[i]}.$ext
    scp root@"${servers[i]}":/tmp/$TESTNAME-sv-$DATE $dirname/$TESTNAME-sv-${servers[i]}.$ext
    echo -e "$TESTNAME-cl-${clients[i]}.$ext : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: iperf -c ${testips[i]} $OPTIONS_C" >> $repfile
    echo -e "$TESTNAME-sv-${servers[i]}.$ext : \n  Server: ${servers[i]}\n  Command: iperf -s $OPTIONS_S" >> $repfile
done
echo 'End.'
