[![build](https://github.com/SystemRDL/PeakRDL-ipxact/workflows/build/badge.svg)](https://github.com/SystemRDL/PeakRDL-ipxact/actions?query=workflow%3Abuild+branch%3Amaster)
[![Coverage Status](https://coveralls.io/repos/github/SystemRDL/PeakRDL-ipxact/badge.svg?branch=master)](https://coveralls.io/github/SystemRDL/PeakRDL-ipxact?branch=master)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peakrdl-ipxact.svg)](https://pypi.org/project/peakrdl-ipxact)

# PeakRDL-ipxact
This package implements IP-XACT import and export for the PeakRDL toolchain

- **Export:** Convert compiled SystemRDL input into IP-XACT XML
- **Import:** Read an IP-XACT file and import it into the `systemrdl-compiler` namespace

## Installing
Install from [PyPi](https://pypi.org/project/peakrdl-ipxact) using pip:

    python3 -m pip install peakrdl-ipxact

--------------------------------------------------------------------------------

## Exporter Usage
Pass the elaborated output of the [SystemRDL Compiler](http://systemrdl-compiler.readthedocs.io)
to the exporter.

```python
import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.ipxact import IPXACTExporter

rdlc = RDLCompiler()

try:
    rdlc.compile_file("path/to/my.rdl")
    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)

exporter = IPXACTExporter()

exporter.export(root, "path/to/output.xml")
```

## Importer Usage
When an IP-XACT file is imported, the register description is loaded into the
SystemRDL register model as if it was an `addrmap` component declaration.
Once imported, the IP-XACT contents can be used as-is, or referenced from
another RDL file.

Import can occur at any point alongside normal RDL file compilation.

```python
import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.ipxact import IPXACTImporter

rdlc = RDLCompiler()
ipxact = IPXACTImporter(rdlc)

try:
    ipxact.import_file("path/to/my_ipxact.xml")
    rdlc.compile_file("path/to/my.rdl")
    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)
```
--------------------------------------------------------------------------------

## Reference

### `IPXACTExporter(**kwargs)`
Constructor for the IP-XACT exporter class

**Optional Parameters**

* `vendor`
    * Vendor url string. Defaults to "example.org"
* `library`
    * library name string. Defaults to "mylibrary"
* `version`
    * Version string. Defaults to "1.0"
* `standard`
    * IP-XACT Standard to use. Currently supports:
        * `peakrdl.ipxact.Standard.IEEE_1685_2009`
        * `peakrdl.ipxact.Standard.IEEE_1685_2014`
    * Defaults to IEEE Std 1685-2014
* `xml_indent`
    * String to use for each indent level. Defaults to 2 spaces.
* `xml_newline`
    * String to use for line breaks. Defaults to newline.

### `IPXACTExporter.export(node, path)`
Perform the export!

**Parameters**

* `node`
    * Top-level node to export. Can be the top-level `RootNode` or any internal `AddrmapNode`.
* `path`
    * Output file.

### `IPXACTImporter(compiler)`
Constructor for the IP-XACT importer class

* `compiler`
    * Reference to `RDLCompiler` instance to bind the importer to

### `IPXACTImporter.import_file(path)`
Perform the import!

* `path`
    * Input IP-XACT file.
* `remap_state`
    * Optional remapState string that is used to select memoryRemap regions
