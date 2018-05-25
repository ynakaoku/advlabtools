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


# stop esxtop in all ESXi hosts.
for host in "${hosts[@]}" ; do
    echo "Stop ESXTOP on host ${host}..."
    ssh root@"${host}" 'sh -s' < $SCRIPT_DIR/optlib/esxtop_stop_opt.bash
done
echo 'Finished.'
