#!/bin/sh

if [ "$1" = "" -o "$2" = "" ] ; then
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
echo "=============================================="
echo "----- Start fixing the installed release -----"
echo "=============================================="
echo "Running on:  `/bin/hostname`"
echo "Experiment Software Installation Area: ${VO_ATLAS_SW_DIR}"
echo "Experiment Software Installation Area listing:"
du -sk ${VO_ATLAS_SW_DIR}/*
du -sk ${VO_ATLAS_SW_DIR}/software/*
[ -d "${VO_ATLAS_SW_DIR}/prod/releases" ] && du -sk ${VO_ATLAS_SW_DIR}/prod/releases/*
[ -d "${VO_ATLAS_SW_DIR}/dev/releases" ] && du -sk ${VO_ATLAS_SW_DIR}/dev/releases/*
ls -la ${VO_ATLAS_SW_DIR}
echo "==============================================="

# Start fixing
source ${VO_ATLAS_SW_DIR}/software/${RELEASE}/setup.sh

#echo "================================="
#echo "---- Fixing file permissions ----"
#echo "================================="
#find $LOCATION -type d -exec chmod a+rx {} \;
#echo "Fixed"

echo "==================================="
echo "---- Fixing geometry db access ----"
echo "==================================="
if [ $RELEASE_MAJOR -eq 10 -o $RELEASE_MAJOR -eq 11 -o $RELEASE_MAJOR -eq 12 ] ; then
    if [ -s $SANDBOX/tnsnames.ora ] ; then
        FILES="`\find ${SITEROOT} -name tnsnames.ora`"
        for DEST in $FILES ; do
            echo
            echo "***************************************"
            echo "FIX BEFORE> diff tnsnames.ora <-> $DEST"
            echo "***************************************"
            echo
            diff ${SANDBOX}/tnsnames.ora ${DEST}
            if [ $? -ne 0 ] ; then
                echo
                echo "*******************************"
                echo "FIX BEGIN> Fixing tnsnames.ora"
                echo "*******************************"
                echo
                \mv ${DEST} ${DEST}.save
                \cp ${SANDBOX}/tnsnames.ora ${DEST}
                echo
                echo "**************************************"
                echo "FIX AFTER> diff tnsnames.ora <-> $DEST"
                echo "**************************************"
                echo
                diff ${SANDBOX}/tnsnames.ora ${DEST}
                echo
                echo "*******************************"
                echo "FIX END> End of tnsnames.ora fix"
                echo "*******************************"
                echo
            else
                echo
                echo "**********************************"
                echo "NO FIX> tnsnames.ora is already OK"
                echo "**********************************"
                echo
            fi
        done
    fi
fi

exit
