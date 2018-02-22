#!/bin/sh

VERSION="$1"
DBREL="$2"
HOST_CE="$3"

if [ "$1" == "" -o "$2" == "" -o "$3" == "" ] ; then
  echo "Usage: `basename` $0 <version> <db release> <CE fqdn>"
  exit -1
fi

experiment=atlas
LCG_DIR=$LCG_LOCATION/bin
TAG="VO-${experiment}-dbrelease-${DBREL}-${VERSION}"

echo "Executing :"
echo perl ${LCG_DIR}/lcg-ManageVOTag -host $HOST_CE -vo $experiment --remove -tag $TAG
perl ${LCG_DIR}/lcg-ManageVOTag -host $HOST_CE -vo $experiment --remove -tag $TAG
retcode=$?

exit $retcode
