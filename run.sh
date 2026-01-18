#!/usr/bin/env bash
# This file is for mac/linux

echo "================================="
echo " Valant PDF Bill Splitter"
echo "================================="

source venv/bin/activate
python split_bills.py "$@"
deactivate
