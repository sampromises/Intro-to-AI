#!/bin/bash

echo "DIRECT SAMPLING (0)"
counter=1
while [ $counter -le 100 ]
do
  python2 sampling.py ./tests/sample.txt $counter 0
  ((counter++))
done

echo "REJECTION SAMPLING (1)"
counter=1
while [ $counter -le 100 ]
do
  python2 sampling.py ./tests/sample.txt $counter 1
  ((counter++))
done

echo "LIKELIHOOD SAMPLING (2)"
counter=1
while [ $counter -le 100 ]
do
  python2 sampling.py ./tests/sample.txt $counter 2
  ((counter++))
done

echo "GIBBS SAMPLING (3)"
counter=1
while [ $counter -le 100 ]
do
  python2 sampling.py ./tests/sample.txt $counter 3
  ((counter++))
done