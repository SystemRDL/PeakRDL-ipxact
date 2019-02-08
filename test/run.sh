#!/bin/bash

set -e

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"
cd $this_dir/../

# Run unit tests while collecting coverage
coverage3 run $this_dir/../setup.py test
coverage3 html -d $this_dir/htmlcov

# Run lint
#cd ralbot
#pylint --rcfile $this_dir/pylint.rc ipxact | tee $this_dir/lint.rpt
