#!/bin/bash

if [ -z "${PTH}" ]; then
   export PTH="$(dirname $0)/"
fi


echo "starting GWASbot"
python3 ./app/enrichrbot.py
