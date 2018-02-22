#!/bin/sh
showhelp()
{
  echo "Usage: `basename $0` [OPTIONS]"
  echo "       OPTIONS:"
  echo "          -h|--help             Show this help."
  echo "          -r|--resource <name>  Specify Panda resource to check."
  echo "          -s|--sitename         Specify the site name to check."
  echo "          -v|--verbose          Increase verbosity."
  exit 0
}

OPTS=`getopt -o hr:s:v -l help,resource:,sitename:,verbose -- "$@"`
if [ $? != 0 ] ; then echo "Terminating..."; exit -1 ; fi
eval set -- "$OPTS"
while true ; do
        case "$1" in
                -h|--help)         showhelp; shift;;
                -r|--resource)     RESNAME="$2"; shift 2;;
                -s|--sitename)     SITEOPT="--sitename=$2"; shift 2;;
                -v|--verbose)      VERBOSE="yes"; shift;;
                --)                shift ; break ;;
                \?)                break ;
                exit ;;
        esac
done

AGISQUEUES=agis-queues.txt
QUEUETAGS="/tmp/agis-queuetags.$$"

rm -f $AGISQUEUES
ljsfinfo.py --select="DISTINCT(site.cename),site.name" --after '2011-06-01' $SITEOPT --quiet | sed 's/"//g' | sed '/,$/d' | \
while read line; do
    CE="`echo $line | cut -d, -f 1`"
    if [ -n "$RESNAME" ] ; then
        QUEUES="`agis-tags -S --ce $CE | grep "^$RESNAME" | tr '\n' ',' | sed 's/,$//'`"
    else
        QUEUES="`agis-tags -S --ce $CE | tr '\n' ',' | sed 's/,$//'`"
    fi
    if [ ! -s ${QUEUETAGS}.${CE}.data ] ; then
        echo "Caching AGIS tags for ${CE} in ${QUEUETAGS}.${CE}.data"
        if [ -n "$RESNAME" ] ; then
            agis-tags --list --panda-resource ${RESNAME} > ${QUEUETAGS}.${CE}.data
        else
            agis-tags --list --ce ${CE} > ${QUEUETAGS}.${CE}.data
        fi
    fi
    # Remove the wrong tags
    CMTCONFIG="x86-64-slc5-gcc43-opt"
    agis-tags --quiet --list --ce ${CE} --cmtconfig $CMTCONFIG | while read wrongtag; do
        echo "Removing bad CMTCONFIG $CMTCONFIG tag $wrongtag from panda resources associated to ${CE}"
        [ -n "$DEBUG" ] && echo "agis-tags --remove --tags=$wrongtag --ce=$CE --cmtconfig=$CMTCONFIG"
        agis-tags --remove --tags="$wrongtag" --ce="$CE" --cmtconfig="$CMTCONFIG"
    done
    #cat ${QUEUETAGS}.${CE}.data | grep "x86-64" | while read wrongtag; do
    #    CMTCONFIG="`echo $wrongtag | sed 's/.*\(x86-64.*\)/\1/'`"
    #    echo "Removing AGIS tag $wrongtag from ${CE}"
    #    TAG="`echo $wrongtag | sed 's/x86-64/x86_64/g'`"
    #    [ -n "$DEBUG" ] && echo "agis-tags --remove --tags=$TAG --ce=$CE --cmtconfig=$CMTCONFIG"
    #    agis-tags --remove --tags="$TAG" --ce="$CE" --cmtconfig="$CMTCONFIG"
    #done
    [ -n "$QUEUES" ] && echo "$line:$QUEUES" >> $AGISQUEUES
done

TMPAGISTAGS=agistags.$$
TMPRESTAGS=restags.$$
if [ -s $AGISQUEUES ] ; then
    NUMAGISQUEUES="`cat $AGISQUEUES | wc -l`"
    QUEUINDX=0
    cat $AGISQUEUES | sort | uniq | while read line; do
        QUEUEINDX=$((QUEUEINDX+1))
        PROGRESS=$((100*$QUEUEINDX/$NUMAGISQUEUES))
        CE="`echo $line | cut -d: -f 1 | cut -d, -f 1`"
        SITE="`echo $line | cut -d: -f 1 | cut -d, -f 2`"
        echo "Checking Tags on $CE [$SITE] - ${PROGRESS}% done"
        ljsfinfo.py --select="release_stat.name,release_data.tag" --status=installed --ce=$CE --quiet | sort | uniq | sed 's/"//g' | while read RELTAG; do
            REL="`echo $RELTAG | cut -d, -f 1`"
            TAG="`echo $RELTAG | cut -d, -f 2`"
            if [ -s ${QUEUETAGS}.${CE}.data ] ; then
                grep -q $TAG ${QUEUETAGS}.${CE}.data
                tagsearchrc=$?
            else
                tagsearchrc=1
            fi
            if [ $tagsearchrc -eq 0 ] ; then
                [ -n "$VERBOSE" ] && echo "Tag $TAG already present in AGIS for $CE"
            else
                echo -n "Tagging $REL on $CE: "
                [ -n "$DEBUG" ] && echo agis-tags --add --rel="$REL" --ce="$CE"
                agis-tags --add --rel="$REL" --ce="$CE"
                [ $? -eq 0 ] && echo "OK" || echo "FAILED"
            fi
        done
    done
    NUMAGISQUEUES="`cat $AGISQUEUES | wc -l`"
    QUEUINDX=0
    cat $AGISQUEUES | sort | uniq | while read line; do
        QUEUEINDX=$((QUEUEINDX+1))
        PROGRESS=$((100*$QUEUEINDX/$NUMAGISQUEUES))
        CE="`echo $line | cut -d: -f 1 | cut -d, -f 1`"
        SITE="`echo $line | cut -d: -f 1 | cut -d, -f 2`"
        if [ -n "$CE" -a -n "$SITE" ] ; then
            echo "Checking $CE [$SITE] - ${PROGRESS}% done"
            agis-tags --list --ce $CE > $TMPAGISTAGS
            #show-tags --site $SITE $CE > $TMPRESTAGS
            show-tags $CE > $TMPRESTAGS
            cat $TMPRESTAGS | while read restag; do
                grep -q $restag $TMPAGISTAGS
                [ $? -ne 0 ] && echo "AGIS_MISSING> $CE: $restag"
            done
            cat $TMPAGISTAGS | while read agistag; do
                grep -q $agistag $TMPRESTAGS
                [ $? -ne 0 ] && echo "AGIS_WRONG> $CE: $agistag"
            done
            rm -f $TMPAGISTAGS $TMPRESTAGS
        fi
    done
fi

echo "ALL DONE"

rm -f ${QUEUETAGS}* $AGISQUEUES
exit
