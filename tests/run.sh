#!/bin/bash

set -e

cd "$(dirname "$0")"

# Initialize venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Install dut
pip install -e "../[cli]"

# Make sure IP-XACT schema have been downloaded
./schema/1685-2014/download_schema.sh
./schema/1685-2009/download_schema.sh

# Run unit tests while collecting coverage
pytest --cov=peakrdl_ipxact

# Generate coverage report
coverage html -d htmlcov

# Run lint
pylint --rcfile pylint.rc ../src/peakrdl_ipxact | tee lint.rpt

# Run static type checking
mypy ../src/peakrdl_ipxact

rm -f tmp*.xml
