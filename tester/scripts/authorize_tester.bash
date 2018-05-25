#! /bin/bash
#

usage_exit() {
    echo "Usage: $0 [-C config_file] [-R]" 1>&2
    exit 1
}

WORK_DIR=$(pwd)
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $WORK_DIR

CONFFILE=null
RENEW=false

# parsing command option.
while getopts C:Rh OPT
do
    case $OPT in
        "C")  CONFFILE=$OPTARG ;;
        "R")  RENEW=true ;;
        "h")  usage_exit ;;
        \?) usage_exit ;;
    esac
done

# config file existency check.
if [ -f ${WORK_DIR}/${CONFFILE} ]; then
    . $WORK_DIR/$CONFFILE
else
    echo "Config file does not exist, exit..."
    exit 1
fi

# generate secret key and public key of control VM (this machine).
if [ $RENEW ]; then
    ssh-keygen -t rsa
fi

# copy generated public key to all test VMs.

for vm in "${servers[@]}" ; do
    echo "copy public key to VM ${vm}..."
    ssh-copy-id root@"${vm}":
done

for vm in "${clients[@]}" ; do
    echo "copy public key to VM ${vm}..."
    ssh-copy-id root@"${vm}":
done

# set active the copied public key in all test VMs.
#
#for vm in "${servers[@]}" ; do
#    echo "activating public key on VM ${vm}..."
#    ssh root@"${vm}" 'bash -s' < $SCRIPT_DIR/optlib/activate_tester_opt.bash
#done
#
#for vm in "${clients[@]}" ; do
#    echo "activating public key on VM ${vm}..."
#    ssh root@"${vm}" 'bash -s' < $SCRIPT_DIR/optlib/activate_tester_opt.bash
#done
