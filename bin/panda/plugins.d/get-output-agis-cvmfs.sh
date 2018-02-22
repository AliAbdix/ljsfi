#!/bin/sh

# AGIS cvmfs
echo "[`date`] Calling agis-cvmfs --panda-resource $1"
agis-cvmfs --panda-resource "$1"
#agis-cvmfs --api --panda-resource "$1"

exit $?
