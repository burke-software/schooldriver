#!/bin/bash
# jnm 20120625
if [ $# -ne 1 ]
then
	echo "Usage: $0 school" 1>&2
	exit 1
fi
sugar="sugar_$1"
sword="sword_$1"
sed "s/!!!SUGAR DB!!!/$sugar/g" sword_sync.sql | sed "s/!!!SWORD DB!!!/$sword/g"
