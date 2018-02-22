#!/bin/sh

RELEASE=$1
cd $VO_ATLAS_SW_DIR

#
#=============================
#
echo "============================="
date
echo "Running on "`/bin/hostname`
uname -a
echo "+---------------------------+"
echo "Removing $VO_ATLAS_SW_DIR/prod/$RELEASE ..."
rm -fr $VO_ATLAS_SW_DIR/prod/$RELEASE

#
#=============================
#
echo "============================="
echo "Listing $VO_ATLAS_SW_DIR/prod ..."
echo "+---------------------------+"
\ls $VO_ATLAS_SW_DIR/prod
echo "============================="
fs listquota $VO_ATLAS_SW_DIR/prod
echo "============================="
#
#=============================
#

exit
