#!/bin/sh

if [ "$1" = "" -o "$2" = "" ] ; then
  echo "Usage: `basename $0` <release> <install-path of the release>"
  exit -1
fi

# Get the parameters
RELEASE=$1
LOCATION=$2
PACMAN_OPTS="-trust-all-caches -allow unsupported-platforms"
if [ "$platform" != "" -a "$platform" != "auto" ] ; then
  export PACMAN_OPTS="$PACMAN_OPTS -pretend-platform $platform"
fi

date
echo "==============================================="
echo "------ Start testing installed software -------"
echo "==============================================="
echo "Running on:  `/bin/hostname`"
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
KVPKG=${RELEASE}/KitValidation
KVPKGPATCHES=${RELEASE}/KitValidationPatches

ATLASGEOM=http://atlas.web.cern.ch/Atlas/GROUPS/DATABASE/pacman4/Geometry

lcg-cp --vo atlas lfn:${PACMAN_TAR} file://${PWD}/${PACMAN_TAR}
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
[ $? -eq 0 ] && source setup.sh
if [ $retcode -ne 0 -o ! -f $PWD/KitValidation/*/share/KitValidation ] ; then
  echo "Error getting KitValidation"
  exit -1
fi

# Get the SQlite geometry db
echo y | pacman $PACMAN_OPTS -get $ATLASGEOM:GeomDBSQLite
export T_SQLITEGEOM=$PWD/geomDB_sqlite

# Start validating
[ "$KVDISABLE" != "" ] && KVDISABLE_OPTS="--disable $KVDISABLE"
echo "Starting KV:"
echo "$PWD/KitValidation/*/share/KitValidation -r $RELEASE -p $LOCATION -kngv --bw -t $PWD $KVDISABLE_OPTS"
$PWD/KitValidation/*/share/KitValidation -r $RELEASE -p $LOCATION \
                                         -kngv --bw -t $PWD $KVDISABLE_OPTS

exit
