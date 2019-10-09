#!/bin/bash
 
if [ -z "${PTH}" ]; then
   export PTH="$(dirname $0)/"
fi

echo "Starting srteam listening"
python3 ./app/QA.py