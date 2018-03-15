#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [ -D ] [-N testname] [ -c count ] [-i interval] [ -l preload ] [ -q ] [ -Q tos ] [ -R ] [ -s packetsize ]" 1>&2
    exit 1
}

WORK_DIR=$(pwd)
REPORT_DIR=$WORK_DIR/reports
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null
COUNT=5               # defaultly ping count is set to 5 times.
INTERVAL=1            # defaultly ping interval is set to 1 sec.
TIMESTAMP=false
QUIET=false
RROUTE=false

# parsing command option.
while getopts C:N:c:D:i:l:qQ:Rs:h OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "N")  TESTNAME=$OPTARG ;;
        "c")  COUNT=$OPTARG ;;
        "D")  TIMESTAMP=true ;;
        "i")  INTERVAL=$OPTARG ;;
        "l")  PRELOAD=$OPTARG ;;
        "q")  QUIET=true ;;
        "Q")  TOS=$OPTARG ;;
        "R")  RROUTE=true ;;
        "s")  PACKETSIZE=$OPTARG ;;
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
OPTIONS="$OPTIONS -c $COUNT -i $INTERVAL"

if $TIMESTAMP ; then
    OPTIONS="$OPTIONS -D"
fi

if [ $PRELOAD ]; then
    OPTIONS="$OPTIONS -l $PRELOAD"
fi

if $QUIET ; then
    OPTIONS="$OPTIONS -q"
fi

if [ $TOS ]; then
    OPTIONS="$OPTIONS -Q $TOS"
fi

if $RROUTE ; then
    OPTIONS="$OPTIONS -R"
fi

if [ $PACKETSIZE ]; then
    OPTIONS="$OPTIONS -s $PACKETSIZE"
fi

if [ $TESTNAME ]; then
    OPTIONS="$OPTIONS > /tmp/$TESTNAME"
else
    echo "Test name is not specified, exit..."
    exit 1
fi

TIME=$(expr $INTERVAL \* $COUNT)

echo 'Executing ping on Client VMs...'
for i in $(seq 0 ${max}) ; do
    echo "ping ${testips[i]} $OPTIONS" | ssh -T root@"${clients[i]}" &
done
sleep $(($TIME+5))

echo 'Collecting ping result files...'
dirname=$REPOPRT_DIR/$TESTNAME-ping-$(date +%g%m%d-%H%M%S)
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
    scp root@"${clients[i]}":/tmp/$TESTNAME $dirname/$TESTNAME-${clients[i]}.result
    echo -e "$TESTNAME-${clients[i]}.result : \n  Client: ${clients[i]}\n  Server: ${servers[i]}\n  Command: ping ${testips[i]} $OPTIONS" >> $repfile
done
echo 'End.'
