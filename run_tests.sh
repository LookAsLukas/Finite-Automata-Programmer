#!/bin/bash

source .venv/bin/activate
pip install pytest pytest-cov
pytest --cov-report=html:htmlcov_report --cov=src tests/
