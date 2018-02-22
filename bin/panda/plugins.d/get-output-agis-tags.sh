#!/bin/sh

# AGIS tagging
if [ "$3" == "installed" ] ; then
  echo "[`date`] Calling agis-tags --panda-resource=\"$1\" --add --rel=\"$2\""
  agis-tags --panda-resource="$1" --add --rel="$2"
  #agis-tags --panda-resource="$1" --add --rel="$2" --api
else
  echo "[`date`] Calling agis-tags --panda-resource=\"$1\" --remove --rel=\"$2\""
  agis-tags --panda-resource="$1" --remove --rel="$2"
  #agis-tags --panda-resource="$1" --remove --rel="$2" --api
fi

exit $?
