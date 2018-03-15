#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-u] [-m mode]" 1>&2
    exit 1
}

WORK_DIR=$(pwd)
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null
UDP=false

# parsing command option.
while getopts C:um:h OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "u")  UDP=true ;;
        "m")  MODE=$OPTARG ;;
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

# if $MODE is not decalred as command option, uses $mode configuration.
if [ ! $MODE ]; then
    MODE=$mode
#    echo $MODE
fi

# if $UDP is not decalred as command option, uses $proto configuration.
if ! $UDP ; then
    if [ "$proto" = "udp" ] ; then
        UDP=true
    fi
fi

# start defined server software in all VMs.
case $MODE in
    iperf)
        if $UDP ; then 
            SCRIPT="$SCRIPT_DIR/optlib/iperfu_server_opt.bash"
            echo 'Starting iperf servers with UDP mode...'
        else
            SCRIPT="$SCRIPT_DIR/optlib/iperf_server_opt.bash"
            echo 'Starting iperf servers with TCP mode...'
        fi
        for vm in "${servers[@]}" ; do
            echo "Start iperf server on VM ${vm}..."
            ssh root@"${vm}" 'bash -s' < $SCRIPT &
        done
        sleep 5
        echo 'Finished.'
        ;;
    iperf3)
        echo 'Starting iperf3 servers...'
        for vm in "${servers[@]}" ; do
            echo "Start iperf3 server on VM ${vm}..."
            ssh root@"${vm}" 'bash -s' < $SCRIPT_DIR/optlib/iperf3_server_opt.bash &
        done
        sleep 5
        echo 'Finished.'
        ;;
    httpd)
        echo 'Enable httpd servers...'
        for vm in "${servers[@]}" ; do
            echo "Start httpd server on VM ${vm}..."
            ssh root@"${vm}" 'bash -s' < $SCRIPT_DIR/optlib/httpd_server_opt.bash
        done
        sleep 5
        echo 'Finished.'
        ;;
    *) 
        echo "mode is not valid, exit..."
        exit 1
        ;;
esac

