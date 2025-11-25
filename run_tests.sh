#!/bin/bash

source .venv/bin/activate
pip install pytest pytest-cov

mkdir tests/tmp
pytest --cov-report=html:htmlcov_report --cov=src tests/
rm -rf tests/tmp
