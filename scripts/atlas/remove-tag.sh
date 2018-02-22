#!/bin/sh

VERSION="$1"
HOST_CE="$2"
SWNAME="$3"

if [ "$1" == "" -o "$2" == "" ] ; then
  echo "Usage: `basename` $0 <version> <CE fqdn>"
  exit -1
fi

experiment=atlas
LCG_DIR=${LCG_LOCATION}/bin
SWPROJECT="`echo ${SWNAME} | tr [A-Z] [a-z] | sed 's#^atlas##g'`"
TAG="VO-${experiment}-${SWPROJECT}-${VERSION}"

echo "Running on "/bin/hostname
echo "Executing :"
echo perl ${LCG_DIR}/lcg-ManageVOTag -host $HOST_CE -vo $experiment --remove -tag $TAG
echo yes | perl ${LCG_DIR}/lcg-ManageVOTag -host $HOST_CE -vo $experiment --remove -tag $TAG
retcode=$?

exit $retcode
