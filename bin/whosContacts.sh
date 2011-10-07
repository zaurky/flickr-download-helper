#!/bin/bash

getContacts.py --getContactFields "username,nsid" > ../files/contacts_with_names

for UID in $ARGV; do
    echo $UID
done
