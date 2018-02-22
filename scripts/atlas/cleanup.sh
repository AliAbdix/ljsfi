#!/bin/sh

RELEASE=$1
[ "$2" != "" ] && REV=$2 || REV=1
cd $VO_ATLAS_SW_DIR

#
#=============================
#
echo "============================="
date
echo "Running on "`/bin/hostname`
uname -a
echo "+---------------------------+"
#rm -fr pacman-*
chmod -R +rw $VO_ATLAS_SW_DIR/software/$RELEASE
echo "Removing $VO_ATLAS_SW_DIR/software/$RELEASE ..."
rm -fr $VO_ATLAS_SW_DIR/software/$RELEASE
RELMAJ="`echo $RELEASE | cut -d '.' -f 1`"

for RELDIR in `ls -d $VO_ATLAS_SW_DIR/releases/rel_${RELMAJ}*`; do
  if [ -d $RELDIR/dist/$RELEASE ] ; then
    echo "Removing $RELDIR ..."
    rm -fr $RELDIR
  fi
  rmdir $RELDIR &> /dev/null
done

for RELDIR in `ls -d $VO_ATLAS_SW_DIR/*/releases/rel_${RELMAJ}*`; do
  if [ -d $RELDIR/dist/$RELEASE -o -d $RELDIR/AtlasOffline/$RELEASE ] ; then
    echo "Removing $RELDIR ..."
    rm -fr $RELDIR
  fi
  rmdir $RELDIR &> /dev/null
done

\find $VO_ATLAS_SW_DIR -type d -depth -path "*/$USERDIR" | while read dname; do
  echo "Removing directory $dname"
  rm -fr $dname
done

if [ "$VERAREA" != "" ] ; then
  USERAREA="rel_${RELMAJ}-${VERAREA}"
  \find $VO_ATLAS_SW_DIR -type d -depth -name $USERAREA | while read dname; do
    echo "Removing directory $dname"
    rm -fr $dname
  done
fi

if [ -d $VO_ATLAS_SW_DIR/atlas-release-${RELEASE}-${REV}${arch}_install ] ; then
  echo "Removing $VO_ATLAS_SW_DIR/atlas-release-${RELEASE}-${REV}${arch}_install ..."
  rm -fr $VO_ATLAS_SW_DIR/atlas-release-${RELEASE}-*${arch}_install
fi

#
#=============================
#
echo "============================="
echo "Listing $VO_ATLAS_SW_DIR/software ..."
echo "+---------------------------+"
\ls $VO_ATLAS_SW_DIR/software
echo "+---------------------------+"
echo "Listing $VO_ATLAS_SW_DIR/releases ..."
echo "+---------------------------+"
\ls $VO_ATLAS_SW_DIR/releases
echo "+---------------------------+"
echo "Listing $VO_ATLAS_SW_DIR/*/releases ..."
echo "+---------------------------+"
\ls $VO_ATLAS_SW_DIR/*/releases
echo "============================="
#
#=============================
#

exit
