#!/bin/bash

source ~/pyvenv/bin/activate
export PWBPATH="${PWBPATH:=$HOME/pwb/core}"
cd ~/scripts/broken_refs
 ./scanner.py
./post_to_wiki.py
