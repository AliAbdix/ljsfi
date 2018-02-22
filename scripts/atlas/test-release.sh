#!/bin/sh

if [ "$1" = "" -o "$2" = "" ] ; then
  echo "Usage: `basename $0` <release> <install-path of the release>"
  exit -1
fi

# Get the parameters
RELEASE=$1
LOCATION=$2
KVPROJECT=$3
[ "$KVPROJECT" == "AtlasOffline" ] && KVPROJECT=AtlasProduction
[ "$KVPROJECT" != "" -a "$KVPROJECT" != "AtlasRelease" -a "$KVPROJECT" != "release" ] && KVPROJECT_OPTS="--project $KVPROJECT"
[ "$T_POST" == "" ] && export T_POST="yes"    # Send data to the GKV portal
if [ "$KVPROJECT_OPTS" != "" ] ; then
  #if [ "$DBRELPATH" != "" ] ; then
  #  echo "Setting up DB release from $DBRELPATH/setup.sh"
  #  source $DBRELPATH/setup.sh
  #fi
  echo "Setting up SW release from $LOCATION/cmtsite/setup.sh -tag=$RELEASE,$KVPROJECT,opt"
  source $LOCATION/cmtsite/setup.sh -tag=$RELEASE,$KVPROJECT,opt
fi
PACMAN_OPTS="-trust-all-caches -allow unsupported-platforms"
if [ "$platform" != "" -a "$platform" != "auto" ] ; then
  export PACMAN_OPTS="$PACMAN_OPTS -pretend-platform $platform"
fi

date
echo "==============================================="
echo "------ Start testing installed software -------"
echo "==============================================="
echo "Running on:  `/bin/hostname`"
echo "Host info:   `/bin/uname -a`"
echo "Experiment Software Installation Area: ${VO_ATLAS_SW_DIR}"
echo "Experiment Software Installation Area listing:"
#du -sk ${VO_ATLAS_SW_DIR}/*
#du -sk ${VO_ATLAS_SW_DIR}/software/*
ls -la ${VO_ATLAS_SW_DIR}
echo "==============================================="

[ "$PACMAN_VER" == "" ] && PACMAN_VER=3.15
PACMAN_DIR=pacman-${PACMAN_VER}
PACMAN_TAR=${PACMAN_DIR}.tar.gz
PACMAN_URL=http://physics.bu.edu/~youssef/pacman/sample_cache/tarballs

KVCACHE=http://classis01.roma1.infn.it/pacman/cache
#KVCACHE=http://classis01.roma1.infn.it/pacman/unvalidated/cache
#KVCACHE=http://www.roma1.infn.it/atlas/pacman/cache
KVPKG=${RELEASE}/KitValidation
KVPKGPATCHES=${RELEASE}/KitValidationPatches
KVPKGPYJTPATCHES=${RELEASE}/KitValidationPyJTPatches

lcg-cp --vo atlas lfn:/grid/atlas/install/lcg/${PACMAN_TAR} file://${PWD}/${PACMAN_TAR}
if [ $? -ne 0 ] ; then
  echo "Cannot get pacman from the RM, I'll try to download it"
  rm -f ${PACMAN_TAR}
  wget ${PACMAN_URL}/${PACMAN_TAR}
  if [ $? -ne 0 ] ; then
    echo "Cannot get pacman. Giving up..."
    exit -1
  fi
fi

# Unpack and setup pacman
tar xfz $PACMAN_TAR
cd $PACMAN_DIR
source setup.sh
cd ..

# Get the KitValidation package
echo y | pacman $PACMAN_OPTS -get $KVCACHE:$KVPKG
retcode=$?
echo y | pacman $PACMAN_OPTS -get $KVCACHE:$KVPKGPATCHES
[ -s setup.sh ] && source setup.sh
echo y | pacman $PACMAN_OPTS -get $KVCACHE:$KVPKGPYJTPATCHES
if [ -d AtlasProduction ] ; then
  unset CMTPATH
  cd AtlasProduction/*/AtlasProductionRunTime/cmt
  source setup.sh
  cd -
fi
if [ $retcode -ne 0 -o ! -f $PWD/KitValidation/*/share/KitValidation ] ; then
  echo "Error getting KitValidation"
  exit -1
fi

# Start validating
[ "$KVDISABLE" != "" ] && KVDISABLE_OPTS="--disable $KVDISABLE"
echo "Starting KV:"
echo "$PWD/KitValidation/*/share/KitValidation -r $RELEASE -p $LOCATION -kngv --bw -t $PWD $KVDISABLE_OPTS"
$PWD/KitValidation/*/share/KitValidation -r $RELEASE -p $LOCATION \
                                         -kngv --bw -t $PWD $KVDISABLE_OPTS $KVPROJECT_OPTS

exit
