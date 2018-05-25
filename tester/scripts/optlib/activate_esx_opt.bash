#! /bin/bash
#
cat /tmp/id_rsa.pub >> /etc/ssh/keys-root/authorized_keys
rm /tmp/id_rsa.pub
#chmod 755 ~/
#chmod 700 ~/.ssh
#chmod 600 ~/.ssh/authorized_keys

