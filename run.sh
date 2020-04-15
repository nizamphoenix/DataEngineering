#!/bin/bash

if [ "$#" -lt 3 ]; then
   echo "usage:   ./run.sh project-name bucket-name classname [options] "
   exit
fi

PROJECT=$1
shift
BUCKET=$1
shift
SRC= # my directory containing pipeline driver
shift

echo "Creating $SRC project=$PROJECT bucket=$BUCKET $*"

python3 pipelne_driver.py -Dexec.mainClass=$SRC \
      -Dexec.args="--project=$PROJECT \
      --stagingLocation=gs://$BUCKET/staging/ $* \
      --tempLocation=gs://$BUCKET/staging/ \
      --runner=DataflowRunner \
      --maxNumWorkers=2 \
      --workerMachineType=n1-standard-2"
