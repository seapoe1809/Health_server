#!/bin/bash

# Navigate to install_module directory
cd install_module

# Reset to latest commit from new_origin/master
git fetch new_origin
git reset --hard new_origin/master

cp ./Analyze/analyze ../analyze.py

