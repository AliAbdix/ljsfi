OSGTags() {
    local TU_OPTS=`getopt -o adlLprtV -l add,ce:,debug,file:,list,location:,project:,remove,tags:,vo:,version -- "$@"`
    if [ $? != 0 ] ; then echo "Terminating..."; return -1 ; fi
    eval set -- "$TU_OPTS"

    # Defaults
    local TU_CE=
    local TU_DEBUG="no"
    local TU_TFILE=
    local TU_LOCATION=
    local TU_MODE="list"
    local TU_PROJECT=
    local TU_TAGS=
    local TU_VER="OSGTags v0.2 - (c) Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20090211"
    local TU_VO="atlas"
    local TU_RC=0

    while true ; do
        case "$1" in
            --add|-a)      TU_MODE="add";shift;;
            --debug|-d)    TU_DEBUG="yes";shift;;
            --ce)          TU_CE="$2";shift 2;;
            --file|-f)     TU_TFILE="$2";shift 2;;
            --list|-l)     TU_MODE="list";shift;;
            --location|-L) TU_LOCATION="$2";shift 2;;
            --project|-p)  TU_PROJECT="$2";shift 2;;
            --remove|-r)   TU_MODE="remove";shift;;
            --tags|-t)     TU_TAGS="$2";shift 2;;
            --vo)          TU_VO="$2";shift 2;;
            --version|-V)  echo $TU_VER;return 0;;
            --)            shift;break;;
            \?)            break;
            exit;;
        esac
    done

    # Check the CLI syntax
    if [ "$TU_TFILE" == "" ] ; then
        if [ "$OSG_APP" != "" ] ; then
            if [ ! -d "$OSG_APP/etc" ] ; then
                echo "Cannot find dir $OSG_APP/etc"
                return 1
            fi
            TU_TFILE="$OSG_APP/etc/grid3-locations.txt"
        else
            echo "No output file specified and OSG_APP not defined! Please use --file <output file>."
            return 1
        fi
    fi
    if [ "$TU_MODE" != "list" -a "$TU_TAGS" == "" ] ; then
        echo "No tags specified! Please use --tags <tag list>."
        return 2
    fi
    if [ "$TU_MODE" != "list" -a "$TU_LOCATION" == "" ] ; then
        echo "No location specified! Please use --location <path>."
        return 3
    fi
    if [ "$TU_MODE" != "list" -a "$TU_PROJECT" == "" ] ; then
        echo "No project specified! Please use --project <path>."
        return 4
    fi

    local TU_TAGLINE=""
    local TU_TAG=""

    # Perform the actions

    # Xin Zhao -- move the lock file to $OSG_APP/atlas_app/atlas_rel, 
    # since not all OSG sites allow write permission to the whole $OSG_APP/etc dir
    TU_LOCKFILE=${RELLOC}/../`basename ${TU_TFILE}.lock`
    echo "Using Lockfile $TU_LOCKFILE"
    
    if [ "$TU_MODE" == "add" ] ; then
        [ "$TU_DEBUG" == "yes" ] && echo "Adding tags ${TU_TAGS} to ${TU_TFILE}"
        if [ -f "${TU_LOCKFILE}" ] ; then
            echo "File lock exists: ${TU_LOCKFILE}"
            echo "Aborting the tag operations"
            return 10
        else
            if [ -f ${TU_TFILE} ] ; then
                \cp "${TU_TFILE}" "${TU_LOCKFILE}"
            else
                touch "${TU_LOCKFILE}"
            fi
            if [ $? -ne 0 ] ; then
                echo "Cannot create lock file ${TU_LOCKFILE}"
                echo "Aborting the tag operations"
                return 11
            else
                for TU_TAG in "`echo ${TU_TAGS} | sed 's/,/ /g'`"; do
                    TU_TAGLINE="${TU_TAG} ${TU_PROJECT} ${TU_LOCATION}"
                    TU_FTAG="`grep "${TU_TAGLINE}" "${TU_TFILE}" 2>/dev/null`"
                    if [ "$TU_FTAG" == "" ] ; then
                        [ "$TU_DEBUG" == "yes" ] && echo "Adding tag ${TU_TAGLINE} to ${TU_TFILE}"
                        echo "${TU_TAGLINE}" >> "${TU_LOCKFILE}"
                        if [ $? -ne 0 ] ; then
                            echo "Cannot add new tags to file ${TU_LOCKFILE}"
                            echo "Aborting the tag operations"
                            rm -f "${TU_LOCKFILE}"
                            return 12
                        fi
                    else
                        echo "The tag ${TU_TAGLINE} is already present in ${TU_TFILE}"
                    fi
                done
                \cp "${TU_LOCKFILE}" "${TU_TFILE}"
                if [ $? -ne 0 ] ; then
                    echo "Cannot finalize the update to file ${TU_TFILE}"
                    echo "Aborting the tag operations"
                    rm -f "${TU_LOCKFILE}"
                    return 13
                fi 
                [ "$TU_DEBUG" == "yes" ] && echo "Tags added succesfully to ${TU_TFILE}"
            fi 
            rm -f "${TU_LOCKFILE}"
        fi
    elif [ "$TU_MODE" == "remove" ] ; then
        [ "$TU_DEBUG" == "yes" ] && echo "Removing tags ${TU_TAGS} from ${TU_TFILE}"
        if [ -f "${TU_LOCKFILE}" ] ; then
            echo "File lock exists: ${TU_LOCKFILE}"
            echo "Aborting the tag operations"
            return 20
        else
            local TU_FTAG=""
            [ ! -f "${TU_TFILE}" ] && touch "${TU_TFILE}"
            touch "${TU_LOCKFILE}"
            for TU_TAG in "`echo ${TU_TAGS} | sed 's/,/ /g'`"; do
                TU_TAGLINE="${TU_TAG} ${TU_PROJECT} ${TU_LOCATION}"
                TU_FTAG="`grep "${TU_TAGLINE}" "${TU_TFILE}"`"
                if [ "$TU_FTAG" != "" ] ; then
                    [ "$TU_DEBUG" == "yes" ] && echo "Removing tag ${TU_TAGLINE} from ${TU_TFILE}"
                    grep -v "${TU_TAGLINE}" "${TU_TFILE}" > "${TU_LOCKFILE}"
                    if [ $? -ne 0 -a `cat ${TU_TFILE} | wc -l` -gt 1 ] ; then
                        echo "Cannot create lock file ${TU_LOCKFILE} while removing tag ${TU_TAGLINE}"
                        echo "Aborting the tag operations"
                        rm -f "${TU_LOCKFILE}"
                        return 21
                    else
                        \cp "${TU_LOCKFILE}" "${TU_TFILE}"
                        if [ $? -ne 0 ] ; then
                            echo "Cannot finalize the update to file ${TU_TFILE} while removing tag ${TU_TAGLINE}"
                            echo "Aborting the tag operations"
                            rm -f "${TU_LOCKFILE}"
                            return 22
                        fi 
                        [ "$TU_DEBUG" == "yes" ] && echo "Tag ${TU_TAGLINE} removed successfully from $TU_TFILE"
                    fi 
                else
                    echo "No tag ${TU_TAGLINE} found in ${TU_TFILE}"
                fi 
            done
            rm -f "${TU_LOCKFILE}"
        fi
    else
        [ "$TU_DEBUG" == "yes" ] && echo "Listing tags from $TU_TFILE"
        if [ -f "${TU_TFILE}" ] ; then
            cat "$TU_TFILE"
            if [ $? -ne 0 ] ; then
                echo "Cannot list the tag file ${TU_TFILE}"
                return 30
            fi 
        else
            echo "File not found: ${TU_TFILE}"
        fi 
    fi
    return 0
}
