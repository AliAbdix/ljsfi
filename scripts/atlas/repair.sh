#!/bin/sh

[ "$PACMAN_VER" == "" ] && PACMAN_VER=3.15
PACMAN_DIR=pacman-${PACMAN_VER}
PACMAN_TAR=${PACMAN_DIR}.tar.gz
PACMAN_URL=http://physics.bu.edu/~youssef/pacman/sample_cache/tarballs
PACMAN_OPTS="-allow unsupported-platforms"
if [ "$platform" != "" -a "$platform" != "auto" ] ; then
  export PACMAN_OPTS="$PACMAN_OPTS -pretend-platform $platform"
fi


if [ "$1" = "" ] ; then
  echo "Usage: `basename $0` <release>"
  exit -1
fi

# Get the parameters
RELEASE=$1
shift $#

SANDBOX=$PWD

RELEASE_MAJOR="`echo $RELEASE | cut -d'.' -f 1`"
RELEASE_MINOR="`echo $RELEASE | cut -d'.' -f 2`"
RELEASE_REV="`echo $RELEASE | cut -d'.' -f 3`"

date
echo "================================================="
echo "----- Start repairing the installed release -----"
echo "================================================="
echo "Running on:  `/bin/hostname`"
echo "Experiment Software Installation Area: ${VO_ATLAS_SW_DIR}"
echo "==============================================="

# Setting up pacman
cd ${VO_ATLAS_SW_DIR}
if [ ! -d "${PACMAN_DIR}" ] ; then
    echo "Cannot find Pacman. Trying to fetch it from the RM..."
    # Get pacman
    lcg-cp --vo atlas lfn:${PACMAN_TAR} file://${PWD}/${PACMAN_TAR}
    if [ $? -ne 0 ] ; then
        echo "Cannot get pacman from the RM, trying to download it..."
        rm -f ${PACMAN_TAR}
        wget ${PACMAN_URL}/${PACMAN_TAR}
        if [ $? -ne 0 ] ; then
            echo "Cannot get pacman. Giving up..."
            exit -1
        fi
    fi
    # Unpack pacman
    echo "Unpacking pacman..."
    tar xfz $PACMAN_TAR
fi

# Setup pacman
echo "Setting up pacman..."
cd ${PACMAN}
source setup.sh
cd -

# Start repairing the repository
cd ${VO_ATLAS_SW_DIR}/releases
echo "Start repairing the release repository in $PWD"
pacman -clear-lock $PACMAN_OPTS
pacman -repair $PACMAN_OPTS
if [ $? -eq 0 ] ; then
    echo "Release repository for $RELEASE repaired"
else
    echo "Unable to repair repository for $RELEASE"
    exit -1
fi

# Start repairing the logical installation
cd ${VO_ATLAS_SW_DIR}/software/${RELEASE}
echo "Start repairing the release logical installation in $PWD"
pacman -clear-lock $PACMAN_OPTS
pacman -repair $PACMAN_OPTS
if [ $? -eq 0 ] ; then
    echo "Logical installation for release $RELEASE repaired"
else
    echo "Unable to repair logical installation for $RELEASE"
    exit -1
fi

exit
