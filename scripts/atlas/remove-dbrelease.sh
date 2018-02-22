#!/bin/sh

# DQ2 setup
tar xvfz dq.tar.gz
cd dq
source setup.sh
cd -

# Download the db releases
[ ! -d $VO_ATLAS_SW_DIR/db ] && mkdir $VO_ATLAS_SW_DIR/db
cd $VO_ATLAS_SW_DIR/db
for dataset in `dq2_ls '*DBRelease*'`; do
  for fileinfo in `dq2_ls -flg $dataset`; do
    filename="`echo $fileinfo | awk '{print $2}'`"
    filesize="`echo $fileinfo | awk '{print $3}'`"
    if [ -s $filename ] ; then
      echo "INSTALLER> Removing $filename from $PWD ..."
      echo "rm -f $filename"
      rm -f $filename
      lastretcode=$?
      let retcode=$retcode+$lastretcode
    fi
  done
done

# End of the task
echo
echo "#########################"
[ "$retcode" -ne 0 ] && echo "INSTALLER> Error during the installation process"
echo "INSTALLER> End of the Task"

exit $retcode
