# This script tests a the magic.py code against sample test cases.
# Please run this script on a unix.andrew.cmu.edu machine.

declare -t SCORE=0
declare -t TIME=0
echo ""

# args: $1 number, $2 file, $3 solution_exist, $4 time_limit, $5 points
check()
{
	echo "Running test $1 ($2). Time limit: $4 second."
	START=$(date +%s.%N)
	timeout $4s python magic.py $2 > driver_output.txt
	END=$(date +%s.%N)
	RUNTIME=$(python -c "print $END-$START")
	TIMEDOUT=$(python -c "print $RUNTIME>$4")
	if [ "${TIMEDOUT}" == "True" ]
	then
		echo "Test $1 timed out - 0/$5 points."
		TIME=$(python -c "print $TIME+$4")
	else
		echo "Test $1 took ${RUNTIME} seconds."
		CHECK="$(python check.py $2 driver_output.txt $3)"
		if [ "${CHECK}" == "True" ]
		then
			echo "Test $1 correct - $5/$5 points."
			SCORE=$(python -c "print $SCORE+$5")
			TIME=$(python -c "print $TIME+$RUNTIME")
		else
			echo "Test $1 incorrect - 0/$5 points."
			TIME=$(python -c "print $TIME+$4")
		fi
	fi
	echo ""
}

check 1 tests/sample1.txt True 1 1
check 2 tests/sample2.txt True 1 1
check 3 tests/sample2_fail.txt False 1 1
check 4 tests/sample3.txt True 1 1
check 5 tests/sample3_fail.txt False 1 1
rm driver_output.txt

echo "TOTAL SCORE: ${SCORE}/5 POINTS."
echo "TOTAL TIME: ${TIME} SECONDS."