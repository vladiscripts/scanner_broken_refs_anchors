#!/bin/bash
#
# To run: `crontab -e` and set the scheduler to one of the following:
# 20 1 * * * jsub -once -quiet -N bra ~/scripts/broken_refs/run.sh  # with saving logging in home folder; or specify log path: `-e path_to -o path_to`
# 20 1 * * * jsub -once -quiet -N bra -o /dev/null -e /dev/null ~/scripts/broken_refs/run.sh  # without logging
#
# `pyenv activate venv3.6.4`  # work on Python > v3.6
source $PYTHONENV/bin/activate
cd ~/scripts/broken_refs
./scanner.py
./post_to_wiki.py
