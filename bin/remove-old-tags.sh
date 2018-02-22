#!/bin/sh

CS="${1}"
TEMPSITEINFO="/tmp/siteinfo.$$"
get-site-info $CS | egrep '^GlueSiteName|^gridName' > $TEMPSITEINFO
SITENAME="`cat $TEMPSITEINFO | grep ^GlueSiteName | tail -n 1 | awk '{print $2}'`"
GNAME="`cat $TEMPSITEINFO | grep ^gridName | tail -n 1 | awk '{print $2}'`"
rm -f $TEMPSITEINFO ${SITENAME}.oldtags
show-tags -c $CS | while read tag; do
    CVMFSTAG="`grep ^$tag$ /cvmfs/atlas.cern.ch/repo/sw/tags`"
    if [ -z "$CVMFSTAG" ] ; then
        RELNAME="`ljsfinfo.py --reltag=$tag --select='DISTINCT(release_data.name)' --quiet | sed 's/\"//g'`"
        if [ -n "$RELNAME" -a "$RELNAME" != "PoolCondPFC" ] ; then
            echo "Sending tag removal of release $RELNAME"
            ljsfreq.py --cs=$CS --rel=$RELNAME --reqtype=remove-tag --sitename=$SITENAME --status=autorun --grid-name=$GNAME --comments="Removing tag"
            echo $tag >> ${SITENAME}.oldtags
        fi
    fi
done

exit
