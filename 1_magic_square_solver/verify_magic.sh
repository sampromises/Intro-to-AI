for i in `seq 1 100`;
do
    python generate_filled.py 7 40 > verify_test.txt
    # python generate_filled.py 6 30 > verify_test.txt
    # python generate_filled.py 5 12 > verify_test.txt
    # python generate_filled.py 4 8 > verify_test.txt
    # python generate_filled.py 3 5 > verify_test.txt
    python magic.py verify_test.txt > verify.txt
    python check.py verify_test.txt verify.txt True > verify_final.txt
    line=$(head -n 1 verify_final.txt)
    if [ "$line" != "True" ]; then
        echo "Fail"
        cat verify_test.txt
    else
        echo "Pass!"
    fi
done
