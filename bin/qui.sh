#!/bin/sh

source /etc/fdh/fdh.sh

for USER in $*; do
    python /root/fdh/bin/getContact.py -i $USER --getContactFields "username"
done
