#!/bin/bash

set -e

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"

# Initialize venv
venv_bin=$this_dir/.venv/bin
python3 -m venv $this_dir/.venv

#tools
python=$venv_bin/python
pytest=$venv_bin/pytest
coverage=$venv_bin/coverage
pylint=$venv_bin/pylint
mypy=$venv_bin/mypy

# Install test dependencies
$python -m pip install -U pip setuptools wheel
$python -m pip install -U pytest pytest-cov coverage pylint mypy

# Install dut
cd $this_dir/../
$python -m pip install .
#$python $this_dir/../setup.py install
cd $this_dir

# Make sure IP-XACT schema have been downloaded
$this_dir/schema/1685-2014/download_schema.sh
$this_dir/schema/1685-2009/download_schema.sh

# Run unit tests while collecting coverage
$pytest --cov=peakrdl_ipxact

# Generate coverage report
$coverage html -d $this_dir/htmlcov

# Run lint
$pylint --rcfile $this_dir/pylint.rc ../src/peakrdl_ipxact | tee $this_dir/lint.rpt

# Run static type checking
$mypy $this_dir/../src/peakrdl_ipxact

rm -f tmp*.xml
