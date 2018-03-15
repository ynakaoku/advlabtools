#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file]" 1>&2
    exit 1
}

WORK_DIR=$(pwd)
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null

# parsing command option.
while getopts C:h OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
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


# stop both iperf and httpd servers in all server VMs.
for vm in "${servers[@]}" ; do
    echo "Stop server on VM ${vm}..."
    ssh root@"${vm}" 'bash -s' < $SCRIPT_DIR/optlib/server_stop_opt.bash
done
echo 'Finished.'
