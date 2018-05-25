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
if $RENEW ; then
    ssh-keygen -t rsa
fi

# copy generated public key to all hosts.

for host in "${hosts[@]}" ; do
    echo "copy public key to host ${host}..."
    scp ~/.ssh/id_rsa.pub root@"${host}":/tmp
    ssh root@"${host}" 'sh -s' < $SCRIPT_DIR/optlib/activate_esx_opt.bash
done
