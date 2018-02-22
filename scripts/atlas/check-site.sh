#!/bin/sh

# Return code
let rc=0

if [ "`which edg-brokerinfo`" != "" ] ; then
    BROKERINFO_CMD="edg-brokerinfo"
else
    BROKERINFO_CMD="glite-brokerinfo"
fi
if [ "$BROKERINFO_CMD" != "" ] ; then
    DEFCE="`$BROKERINFO_CMD getCE | head -n 1 | awk '{ print $1}' | cut -d: -f 1`"
    DEFSE="`$BROKERINFO_CMD getCloseSEs | head -n 1 | awk '{ print $1}'`"
else
    DEFCE="UNKNOWN"
    DEFSE="UNKNOWN"
fi
HOST=`/bin/hostname`
if [ "${VO_ATLAS_SW_DIR}" != "" ] ; then
    DISKSPACE=`df -k ${VO_ATLAS_SW_DIR}`
    [ "${VO_ATLAS_SW_DIR}" == "." ] && SHARED="no" || SHARED="yes"
else
    echo "No \$VO_ATLAS_SW_DIR defined!"
    DISKSPACE=0
fi

date
echo "==============================================="
echo "--------    INSTALLATION PARAMETERS    --------"
echo "==============================================="
echo "Running on:  `/bin/hostname`"
echo "System type: `/bin/uname -a`"
echo "OS type:     `cat /etc/redhat-release 2>/dev/null`"
echo "Username:    $USER"
echo "Default CE:  ${DEFCE}"
echo "Default SE:  ${DEFSE}"
echo "Shared area: ${SHARED}"
echo "Experiment Software Installation Area: ${VO_ATLAS_SW_DIR}"
echo "Disk space available for installation:"
echo "${DISKSPACE}"
echo "==============================================="
if [ "${VO_ATLAS_SW_DIR}" != "" ] ; then
    echo "Printing quotas"
    echo "---------------"
    quota
    echo "==============================================="
    echo "Experiment Software Installation Area listing:"
    echo "==============================================="
    echo ">> Disk usage of ${VO_ATLAS_SW_DIR}"
    du -sk ${VO_ATLAS_SW_DIR}/*
    echo "==============================================="
    echo ">> Disk usage of ${VO_ATLAS_SW_DIR}/software"
    du -sk ${VO_ATLAS_SW_DIR}/software/*
    echo "==============================================="
    echo ">> Full listing of ${VO_ATLAS_SW_DIR}"
    ls -la ${VO_ATLAS_SW_DIR}
    echo "==============================================="
    echo ">> Full listing of ${VO_ATLAS_SW_DIR}/software"
    ls -la ${VO_ATLAS_SW_DIR}/software
    echo "==============================================="
    echo ">> Disk usage of ${VO_ATLAS_SW_DIR}/releases"
    du -sk ${VO_ATLAS_SW_DIR}/releases/*
    echo "==============================================="
    echo ">> Disk usage of ${VO_ATLAS_SW_DIR}/prod"
    du -sk ${VO_ATLAS_SW_DIR}/prod/*
    echo "==============================================="
    echo ">> Full listing of ${VO_ATLAS_SW_DIR}/prod/releases"
    ls -la ${VO_ATLAS_SW_DIR}/prod/releases/*
    echo "==============================================="
    echo ">> Disk usage of ${VO_ATLAS_SW_DIR}/dev"
    du -sk ${VO_ATLAS_SW_DIR}/dev/*
    echo "==============================================="
    echo ">> Full listing of ${VO_ATLAS_SW_DIR}/dev/releases"
    ls -la ${VO_ATLAS_SW_DIR}/dev/releases/*
    echo "==============================================="
    if [ "`echo ${VO_ATLAS_SW_DIR} | cut -d '/' -f 2`" == "afs" ] ; then
      echo ">> Listing afs params for ${VO_ATLAS_SW_DIR}"
      fs lsmount ${VO_ATLAS_SW_DIR}
      fs listquota ${VO_ATLAS_SW_DIR}
      fs listacl ${VO_ATLAS_SW_DIR}
      if [ -d "${VO_ATLAS_SW_DIR}/software" ] ; then
        echo ">> Listing afs params for ${VO_ATLAS_SW_DIR}/software"
        fs lsmount ${VO_ATLAS_SW_DIR}/software
        fs listquota ${VO_ATLAS_SW_DIR}/software
        fs listacl ${VO_ATLAS_SW_DIR}/software
      fi
      if [ -d "${VO_ATLAS_SW_DIR}/releases" ] ; then
        echo ">> Listing afs params for ${VO_ATLAS_SW_DIR}/releases"
        fs lsmount ${VO_ATLAS_SW_DIR}/releases
        fs listquota ${VO_ATLAS_SW_DIR}/releases
        fs listacl ${VO_ATLAS_SW_DIR}/releases
      fi
      if [ -d "${VO_ATLAS_SW_DIR}/dev" ] ; then
        echo ">> Listing afs params for ${VO_ATLAS_SW_DIR}/dev"
        fs lsmount ${VO_ATLAS_SW_DIR}/dev
        fs listquota ${VO_ATLAS_SW_DIR}/dev
        [ -d "${VO_ATLAS_SW_DIR}/dev/releases" ] && fs listacl ${VO_ATLAS_SW_DIR}/dev/releases
      fi
      if [ -d "${VO_ATLAS_SW_DIR}/prod" ] ; then
        echo ">> Listing afs params for ${VO_ATLAS_SW_DIR}/prod"
        fs lsmount ${VO_ATLAS_SW_DIR}/prod
        fs listquota ${VO_ATLAS_SW_DIR}/prod
        [ -d "${VO_ATLAS_SW_DIR}/prod/releases" ] && fs listacl ${VO_ATLAS_SW_DIR}/prod/releases
      fi
      echo "==============================================="
    fi
    for setupfile in `\ls ${VO_ATLAS_SW_DIR}/software/*/setup.sh` ; do
      echo
      echo "===================================="
      echo "|   File: $setupfile"
      echo "===================================="
      cat $setupfile
      echo "===================================="
      echo
    done
    echo "======================================================================"
    echo "Listing lcg-ManageSoftware bin files (LCG_LOCATION=$LCG_LOCATION)"
    rpm -ql lcg-ManageSoftware 2>&1 | grep bin | while read cmd; do
      echo ls -la $cmd
      \ls -la $cmd
    done
    echo "======================================================================"
    echo "Checking for libX11.a"
    locate libX11.a
    /bin/ls -l /usr/X11R6/lib/libX11.a 2>/dev/null
    /bin/ls -l /usr/lib/libX11.a 2>/dev/null
fi

exit ${rc}
