#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi


wget https://bindfs.org/downloads/bindfs-1.15.1.tar.gz
tar xzvf bindfs-1.15.1.tar.gz 
cd bindfs-1.15.1
./configure && make && sudo make install
cd ..
rm bindfs-1.15.1.tar.gz 
rm -rf bindfs-1.15.1

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )" # get script location

echo "https://www-dav.uio.no/studier/emner/ $SCRIPT_DIR/.mntParent davfs noauto,user,gid=1000,uid=1000 0 0" | sudo tee -a "/etc/fstab"
echo "$SCRIPT_DIR/.mntParent $SCRIPT_DIR/.mnt none bind,rw,user,noauto 0 0" | sudo tee -a "/etc/fstab"

echo "done"