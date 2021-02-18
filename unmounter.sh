#!/bin/bash1
busy=true
while $busy
do
 if mountpoint -q "$1"
 then
  umount "$1" 2> /dev/null
  if [ $? -eq 0 ]
  then
   busy=false  # umount successful
  else
   echo -n 'attempting unmount ...'  
   sleep 0.1      
  fi
 else
  busy=false  # not mounted
 fi
done
