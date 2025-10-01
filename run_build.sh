#!/bin/bash
echo "Building Automata Builder for Linux..."
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
python build.py
