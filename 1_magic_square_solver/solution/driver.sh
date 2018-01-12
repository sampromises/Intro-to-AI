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

check 1 tests/basic1.txt True 1 4
check 2 tests/basic2.txt True 1 4
check 3 tests/basic1_fail.txt False 1 4
check 4 tests/basic2_fail.txt False 1 4
check 5 tests/med.txt True 1 4
check 6 tests/med_fail.txt False 10 4
check 7 tests/hard1.txt True 1 4
check 8 tests/hard2.txt True 1 4
check 9 tests/hard3.txt True 3 4
check 10 tests/hard4.txt True 3 4
check 11 tests/conflict_precise.txt True 3 5
check 12 tests/crazy1.txt True 5 5
check 13 tests/crazy1_fail.txt False 10 5
check 14 tests/crazy2.txt True 5 5
rm driver_output.txt

echo "TOTAL SCORE: ${SCORE}/60 POINTS."
echo "TOTAL TIME: ${TIME} SECONDS."
echo "{\"scores\": {\"Magic Square\": ${SCORE}}, \"scoreboard\": [${SCORE}, ${TIME}]}"