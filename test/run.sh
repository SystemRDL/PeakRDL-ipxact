#!/bin/bash

set -e

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"
cd $this_dir/../

# Make sure IP-XACT schema have been downloaded
$this_dir/schema/1685-2014/download_schema.sh
$this_dir/schema/1685-2009/download_schema.sh

# Run unit tests while collecting coverage
coverage3 run $this_dir/../setup.py test
coverage3 html -d $this_dir/htmlcov

# Run lint
pylint --rcfile $this_dir/pylint.rc ralbot | tee $this_dir/lint.rpt
