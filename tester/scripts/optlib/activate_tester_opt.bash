#! /bin/bash
#
cat id_rsa.pub >> .ssh/authorized_keys
rm id_rsa.pub
chmod 755 ~/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

