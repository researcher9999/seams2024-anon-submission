#!/bin/bash

SEEDS="123456789 987654321 12121212 34343434 565656 787878 909090 123123 456456 789789"
ADAPTATIONTYPE="coordinated uncoordinated random"
MOTES="3 4 5 6 7 8 9"


PWD=$(pwd)

export JAVA_HOME=/usr/lib/jvm/openjdk17

for motes in $MOTES
do
    for seed in $SEEDS
    do
	sed  "s/!!!SEED!!!/$seed/" src/main/java/util/Constants.java.template > src/main/java/util/Constants.java
	sed  "s/!!!MOTES!!!/$motes/" src/main/java/nogui/MainNoGUI.java.template > src/main/java/nogui/MainNoGUI.java
	mvn package

	for adapttype in $ADAPTATIONTYPE
	do
	    tic=$SECONDS

	    source venv_312/bin/activate

	    python $PWD/src/main/python/main.py --adaptation $adapttype --seed $seed --resultspath results_${motes}motes_good.sqlite3 & (sleep 5 && /usr/lib/jvm/openjdk17/bin/java -jar $PWD/target/DingNet-nogui-jar-with-dependencies.jar)

	    toc=$SECONDS
	    seconds=$(( toc - tic ))
	    echo "$seed,$adapttype,$seconds" >> log.txt
	done
    done
done
