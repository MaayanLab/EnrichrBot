#!/bin/bash
if ! pgrep -f QA.py
then
  echo "restarted the talkback bot">>/home/maayanlab/enrichrbot/QA/test1.log
  python3 /home/maayanlab/enrichrbot/QA/QA.py
fi