#!/bin/sh

# AGIS cvmfs
echo "[`date`] Calling agis-cvmfs --ce $1"
agis-cvmfs --ce "$1"

exit $?
