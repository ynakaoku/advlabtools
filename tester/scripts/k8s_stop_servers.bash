#! /bin/bash
#
# Filename: k8s_stop_servers.bash, part of advlabtools; https://github.com/ynakaoku/advlabtools
# Author: Yoshihiko Nakaoku; ynakaoku@vmware.com

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
        if [ -f ${CONFFILE} ]; then
            . $CONFFILE
        else 
            echo "Config file does not exist, exit..." 1>&2
            exit 1
        fi
    fi
fi


# stop both iperf and httpd servers in all server VMs.
for instance in "${servers[@]}" ; do
    echo "Stop server on instances ${instance}..."
    if [ ${stypes[i]} = "kubernetes" ] ; then
        $SCRIPT_DIR/optlib/k8s_server_stop_opt.bash ${instance} ${snamespaces[i]}
    else
        ssh root@"${instance}" 'bash -s' < $SCRIPT_DIR/optlib/server_stop_opt.bash
    fi
done
echo 'Finished.'
