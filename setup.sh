#########################################################
#                   LJSFi main setup                    #
#                LJSFi 1.9.6 - 20110720                 #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it #
#########################################################

LJSFPATH=$PWD
export CONFPATH=$LJSFPATH/etc
export BINPATH=$LJSFPATH/bin
export LJSF_SECURITY=$LJSFPATH/security

# Check the local configuration
[ ! -s $CONFPATH/ljsflocal.conf ] && $BINPATH/ljsf-gen-local-conf
if [ -s $CONFPATH/ljsflocal.conf ] ; then
    . $CONFPATH/ljsflocal.conf
else
    echo "Cannot find any local setup file"
    echo "Configuration failed"
    return -1
fi

# Default paths
export JDLPATH=$LJSFPATH/jdl
export JOBSPATH=$LJSFPATH/jobs
export OUTPUTPATH=$LJSFPATH/output
export SITESPATH=$LJSFPATH/sites
export SITESJDLPATH=$SITESPATH/jdl
export SITESJOBSPATH=$SITESPATH/jobs
export SITESOUTPUTPATH=$SITESPATH/output
export TOOLSPATH=$LJSFPATH/tools
export LJSFVARPATH=$LJSFPATH/var
export LJSFLIBPATH=$LJSFPATH/lib
export LJSFCACHEPATH=$LJSFPATH/cache
export LJSFWWWPATH=$LJSFPATH/www

# WMS type configuration
# EDG/LCG
# source $CONFPATH/ljsf-edg.conf
# gLite
#. $CONFPATH/ljsf-glite.conf
# Panda
. $CONFPATH/ljsf-panda.conf

# Path to the templates
export TEMPLATEPATH=$LJSFPATH/templates/$VO
[ ! -d $TEMPLATEPATH ] && ln -sf generic $TEMPLATEPATH

# Path to the scripts
export SCRIPTPATH=$LJSFPATH/scripts/$VO
[ ! -d $SCRIPTPATH ] && ln -sf generic $SCRIPTPATH

# Default BDII for auto requests
#export LJSF_DEFBDII=exp-bdii.cern.ch

[ ! -d $JDLPATH ] && mkdir -p $JDLPATH
[ ! -d $JOBSPATH ] && mkdir -p $JOBSPATH
[ ! -d $OUTPUTPATH ] && mkdir -p $OUTPUTPATH
[ ! -d $SITESJDLPATH ] && mkdir -p $SITESJDLPATH
[ ! -d $SITESJOBSPATH ] && mkdir -p $SITESJOBSPATH
[ ! -d $SITESOUTPUTPATH ] && mkdir -p $SITESOUTPUTPATH
[ ! -d $LJSFVARPATH ] && mkdir -p $LJSFVARPATH
[ ! -d $LJSF_SECURITY ] && mkdir $LJSF_SECURITY
chmod 700 $LJSF_SECURITY

SRC_URL=http://classis01.roma1.infn.it/externals
LJSF_MYSQL_VERSION="5.6.15"
LJSF_ST_VERSION="2.1"
LJSF_EXTPATH=$LJSFPATH/ext
LJSF_MYSQL_PYTHON_VERSION="1.2.4b4"
LJSF_PYOPENSSL_VERSION="0.13.1"
LJSF_FPCONST_VERSION="0.7.2"
LJSF_SOAPPY_VERSION="0.12.5"
LJSF_PYTHON_MODVER="$LJSF_EXTPATH/lib/python`python -V 2>&1 | awk '{print $2}' | sed 's/\([0-9]*\)\.\([0-9]*\)\..*/\1.\2/g'`/site-packages"
LJSF_PYTHON_MODVER64="$LJSF_EXTPATH/lib64/python`python -V 2>&1 | awk '{print $2}' | sed 's/\([0-9]*\)\.\([0-9]*\)\..*/\1.\2/g'`/site-packages"
LJSF_MYSQL_DIR=$LJSF_EXTPATH/mysql/$LJSF_MYSQL_VERSION
LJSF_MYSQL_BIN=$LJSF_MYSQL_DIR/bin
LJSF_MYSQL_LIB=$LJSF_MYSQL_DIR/lib/mysql
LJSF_LDAP=$LJSF_EXTPATH/ldap
export PATH=$LJSF_MYSQL_BIN:$BINPATH:$PATH
export PYTHONPATH=$BINPATH:$LJSF_PYTHON_MODVER:$LJSF_PYTHON_MODVER64:$LJSF_LDAP:$PYTHONPATH
export LD_LIBRARY_PATH=$LJSFLIBPATH:$LJSF_MYSQL_LIB:$LJSF_LDAP:$LD_LIBRARY_PATH

# Check if the externals are available and compile them if needed
LJSF_BUILD_DIR=/tmp/ljsf.build.tmp.$$
LJSF_BUILD_CACHE=$LJSFPATH/.buildcache
SMPSIZE="`cat /proc/cpuinfo | grep ^processor | wc -l`"
let buildrc=0
if [ ! -d $LJSF_MYSQL_DIR ] ; then
    echo "mysql ${LJSF_MYSQL_VERSION} is not available, trying to get and compile it"
    [ ! -d $LJSF_BUILD_DIR ] && mkdir -p $LJSF_BUILD_DIR
    [ ! -d $LJSF_BUILD_CACHE ] && mkdir -p $LJSF_BUILD_CACHE
    cd $LJSF_BUILD_CACHE
    wget --quiet -c -N $SRC_URL/mysql-${LJSF_MYSQL_VERSION}.tar.gz
    if [ -s mysql-${LJSF_MYSQL_VERSION}.tar.gz ] ; then
        cd $LJSF_BUILD_DIR
        echo "Untarring mysql-${LJSF_MYSQL_VERSION}.tar.gz"
        tar xfz $LJSF_BUILD_CACHE/mysql-${LJSF_MYSQL_VERSION}.tar.gz
        let buildrc=$buildrc+$?
        rm -f mysql-${LJSF_MYSQL_VERSION}.tar.gz
        if [ $buildrc -eq 0 ] ; then
            cd mysql*
            ./configure --prefix=$LJSF_MYSQL_DIR
            let buildrc=$buildrc+$?
            [ $buildrc -eq 0 ] && make -j $SMPSIZE
            let buildrc=$buildrc+$?
            [ $buildrc -eq 0 ] && make install
            let buildrc=$buildrc+$?
        else
            echo "Cannot untar mysql-${LJSF_MYSQL_VERSION}.tar.gz"
        fi
    else
        echo "Cannot get $SRC_URL/mysql-${LJSF_MYSQL_VERSION}.tar.gz"
        let buildrc=1
    fi
fi

if [ ! -d $LJSF_PYTHON_MODVER -o "$1" == "build_python" ] ; then
    if [ $buildrc -eq 0 ] ; then
        mkdir -p $LJSF_PYTHON_MODVER $LJSF_PYTHON_MODVER64
        echo "Compiling setuptools-$LJSF_ST_VERSION"
        [ ! -d $LJSF_BUILD_DIR ] && mkdir -p $LJSF_BUILD_DIR
        [ ! -d $LJSF_BUILD_CACHE ] && mkdir -p $LJSF_BUILD_CACHE
        cd $LJSF_BUILD_CACHE
        wget --quiet -c -N $SRC_URL/setuptools-${LJSF_ST_VERSION}.tar.gz
        if [ -s setuptools-${LJSF_ST_VERSION}.tar.gz ] ; then
            cd $LJSF_BUILD_DIR
            echo "Untarring setuptools-${LJSF_ST_VERSION}.tar.gz"
            tar xfz $LJSF_BUILD_CACHE/setuptools-${LJSF_ST_VERSION}.tar.gz
            let buildrc=$buildrc+$?
            if [ $buildrc -eq 0 ] ; then
                cd setuptools*
                python setup.py build
                let buildrc=$buildrc+$?
                [ $buildrc -eq 0 ] && python setup.py install --prefix=$LJSF_EXTPATH
                let buildrc=$buildrc+$?
            else
                echo "Cannot untar setuptools-${LJSF_ST_VERSION}.tar.gz"
            fi
        else
            echo "Cannot get $SRC_URL/setuptools-${LJSF_ST_VERSION}.tar.gz"
            let buildrc=1
        fi
    fi

    # MySQL python
    if [ $buildrc -eq 0 ] ; then
        echo "Compiling MySQL-python-$LJSF_MYSQL_PYTHON_VERSION"
        cd $LJSF_BUILD_CACHE
        wget --quiet -c -N $SRC_URL/MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz
        if [ -s MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz ] ; then
            cd $LJSF_BUILD_DIR
            echo "Untarring MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz"
            tar xfz $LJSF_BUILD_CACHE/MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz
            let buildrc=$buildrc+$?
            rm -f MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz
            if [ $buildrc -eq 0 ] ; then
                cd MySQL-python*
                python setup.py build
                let buildrc=$buildrc+$?
                [ $buildrc -eq 0 ] && python setup.py install --prefix=$LJSF_EXTPATH
                let buildrc=$buildrc+$?
            else
                echo "Cannot untar MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz"
            fi
        else
            echo "Cannot get $SRC_URL/MySQL-python-${LJSF_MYSQL_PYTHON_VERSION}.tar.gz"
            let buildrc=1
        fi
    fi

    # pyOpenSSL
    if [ $buildrc -eq 0 ] ; then
        echo "Compiling pyOpenSSL-$LJSF_PYOPENSSL_VERSION"
        cd $LJSF_BUILD_CACHE
        wget --quiet -c -N $SRC_URL/pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz
        if [ -s pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz ] ; then
            cd $LJSF_BUILD_DIR
            echo "Untarring pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz"
            tar xfz $LJSF_BUILD_CACHE/pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz
            let buildrc=$buildrc+$?
            rm -f pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz
            if [ $buildrc -eq 0 ] ; then
                cd pyOpenSSL*
                python setup.py build
                let buildrc=$buildrc+$?
                [ $buildrc -eq 0 ] && python setup.py install --prefix=$LJSF_EXTPATH
                let buildrc=$buildrc+$?
            else
                echo "Cannot untar pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz"
            fi
        else
            echo "Cannot get $SRC_URL/pyOpenSSL-${LJSF_PYOPENSSL_VERSION}.tar.gz"
            let buildrc=1
        fi
    fi

    # fpconst
    if [ $buildrc -eq 0 ] ; then
        echo "Compiling fpconst-$LJSF_FPCONST_VERSION"
        cd $LJSF_BUILD_CACHE
        wget --quiet -c -N $SRC_URL/fpconst-${LJSF_FPCONST_VERSION}.tar.gz
        if [ -s fpconst-${LJSF_FPCONST_VERSION}.tar.gz ] ; then
            cd $LJSF_BUILD_DIR
            echo "Untarring fpconst-${LJSF_FPCONST_VERSION}.tar.gz"
            tar xfz $LJSF_BUILD_CACHE/fpconst-${LJSF_FPCONST_VERSION}.tar.gz
            let buildrc=$buildrc+$?
            rm -f fpconst-${LJSF_FPCONST_VERSION}.tar.gz
            if [ $buildrc -eq 0 ] ; then
                cd fpconst*
                python setup.py build
                let buildrc=$buildrc+$?
                [ $buildrc -eq 0 ] && python setup.py install --prefix=$LJSF_EXTPATH
                let buildrc=$buildrc+$?
            else
                echo "Cannot untar fpconst-${LJSF_FPCONST_VERSION}.tar.gz"
            fi
        else
            echo "Cannot get $SRC_URL/fpconst-${LJSF_FPCONST_VERSION}.tar.gz"
            let buildrc=1
        fi
    fi

    # SOAPpy
    if [ $buildrc -eq 0 ] ; then
        echo "Compiling SOAPpy-$LJSF_SOAPPY_VERSION"
        cd $LJSF_BUILD_CACHE
        wget --quiet -c -N $SRC_URL/SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz
        if [ -s SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz ] ; then
            cd $LJSF_BUILD_DIR
            echo "Untarring SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz"
            tar xfz $LJSF_BUILD_CACHE/SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz
            let buildrc=$buildrc+$?
            rm -f SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz
            if [ $buildrc -eq 0 ] ; then
                cd SOAPpy*
                python setup.py build
                let buildrc=$buildrc+$?
                [ $buildrc -eq 0 ] && python setup.py install --prefix=$LJSF_EXTPATH
                let buildrc=$buildrc+$?
            else
                echo "Cannot untar SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz"
            fi
        else
            echo "Cannot get $SRC_URL/SOAPpy-${LJSF_SOAPPY_VERSION}.tar.gz"
            let buildrc=1
        fi
    fi
fi

cd $LJSFPATH
[ -d $BUILD_DIR ] && rm -fr $BUILD_DIR

if [ $buildrc -ne 0 ] ; then
    echo "setup failed"
    return $buildrc
fi

if [ "$1" == "md5sum" ] ; then
    echo -n "Creating MD5SUM... "
    find bin etc scripts templates -xtype f -exec md5sum {} \; | egrep -v '.pyc|.save|edglog|sw-mgr\.|gbb-|\.SL4' > MD5SUM
    echo "done"
fi

echo
echo "##########################################################"
echo "#       LJSFi v1.9.6  - 20110720 Engine initialized      #"
echo "# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> #"
echo "##########################################################"
echo
