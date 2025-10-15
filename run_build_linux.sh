#!/bin/bash
if [ ! -f ".venv/bin/activate" ]; then
    rm -rf .venv/
fi
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install pyinstaller
python3 build.py
