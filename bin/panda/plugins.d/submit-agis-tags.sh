#!/bin/sh

# AGIS pre-tagging
echo "[`date`] PRE-TAGGING - Calling agis-tags --panda-resource=\"$1\" --add --rel=\"$2\""
agis-tags --panda-resource="$1" --add --rel="$2"
#agis-tags --panda-resource="$1" --add --rel="$2" --api

exit $?
