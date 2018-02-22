#!/bin/sh

PRJNAME="$1"
validrc=0

if [ "$PRJNAME" == "cctools" ] ; then
    chirp -h
    validrc=$?
elif [ "$PRJNAME" == "JEM-WN" ] ; then
    TEST="test.$$.sh"
cat > $TEST <<EOD
#!/bin/sh
echo "JEM test"
exit
EOD
    JEM.py --mode WN --valves None --debug --script $TEST
    validrc=$?
    ls
fi

exit $validrc
