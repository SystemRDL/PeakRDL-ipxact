#!/usr/bin/env python3

import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl_ipxact import IPXACTExporter

# Collect input files from the command line arguments
input_files = sys.argv[1:]

# Create an instance of the compiler
rdlc = RDLCompiler()

try:
    # Compile all the files provided
    for input_file in input_files:
        rdlc.compile_file(input_file)

    # Elaborate the design
    root = rdlc.elaborate()
except RDLCompileError:
    # A compilation error occurred. Exit with error code
    sys.exit(1)


exporter = IPXACTExporter()
exporter.export(root.top, "%s.xml" % root.top.inst_name)
