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
echo "Would have removed $VO_ATLAS_SW_DIR/software/$RELEASE ..."
RELMAJ="`echo $RELEASE | cut -d '.' -f 1`"

for RELDIR in `ls -d $VO_ATLAS_SW_DIR/releases/rel_${RELMAJ}*`; do
  if [ -d $RELDIR/dist/$RELEASE ] ; then
    echo "Would have removed $RELDIR ..."
  fi
done

for RELDIR in `ls -d $VO_ATLAS_SW_DIR/*/releases/rel_${RELMAJ}*`; do
  if [ -d $RELDIR/dist/$RELEASE -o -d $RELDIR/AtlasOffline/$RELEASE ] ; then
    echo "Would have removed $RELDIR ..."
  fi
done

\find $VO_ATLAS_SW_DIR -type d -depth -path "*/$USERDIR" | while read dname; do
  echo "Would have removed directory $dname"
done

if [ "$VERAREA" != "" ] ; then
  USERAREA="rel_${RELMAJ}-${VERAREA}"
  \find $VO_ATLAS_SW_DIR -type d -depth -name $USERAREA | while read dname; do
    echo "Would have removed directory $dname"
  done
fi

if [ -d $VO_ATLAS_SW_DIR/atlas-release-${RELEASE}-${REV}${arch}_install ] ; then
  echo "We would have removed $VO_ATLAS_SW_DIR/atlas-release-${RELEASE}-${REV}${arch}_install ..."
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
echo "============================="
#
#=============================
#

exit
