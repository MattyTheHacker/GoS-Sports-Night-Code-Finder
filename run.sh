#!/bin/bash

# cd to correct directory
cd /home/pi/Documents/GoS-Sports-Night-Code-Finder/

# pull any changes from github
git pull

# run the python script
python get_codes.py

# check for updates
if [[ `git status --porcelain` ]]; then
    # changes found
    git add --all
    git commit -m "update"
    git push
else
    # no changes found
    echo "No changes found..."
fi
