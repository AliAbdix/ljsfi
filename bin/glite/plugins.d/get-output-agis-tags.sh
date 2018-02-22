#!/bin/sh

# AGIS tagging
CE="`echo $1 | cut -d: -f 1`"
if [ "$3" == "installed" ] ; then
  echo "[`date`] Calling agis-tags --cs=\"$1\" --add --rel=\"$2\""
  agis-tags --ce="$CE" --add --rel="$2"
else
  echo "[`date`] Calling agis-tags --cs=\"$1\" --remove --rel=\"$2\""
  agis-tags --ce="$CE" --remove --rel="$2"
fi

exit $?
