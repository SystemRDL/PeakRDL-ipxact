[![Build Status](https://travis-ci.org/SystemRDL/RALBot-ipxact.svg?branch=master)](https://travis-ci.org/SystemRDL/RALBot-ipxact)
[![Coverage Status](https://coveralls.io/repos/github/SystemRDL/RALBot-ipxact/badge.svg?branch=master)](https://coveralls.io/github/SystemRDL/RALBot-ipxact?branch=master)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ralbot-ipxact.svg)](https://pypi.org/project/ralbot-ipxact)

# RALBot-ipxact
This package implements IP-XACT import and export for the RALBot toolchain

- **Export:** Convert compiled SystemRDL input into IP-XACT XML
- **Import:** Read an IP-XACT file and import it into the `systemrdl-compiler` namespace

## Installing
Install from [PyPi](https://pypi.org/project/ralbot-ipxact) using pip:

    python3 -m pip install ralbot-ipxact

--------------------------------------------------------------------------------

## Exporter Usage
Pass the elaborated output of the [SystemRDL Compiler](http://systemrdl-compiler.readthedocs.io)
to the exporter.

```python
from ralbot.ipxact import RDLCompiler, IPXACTExporter

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
from ralbot.ipxact import IPXACTImporter

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
    * IP-XACT Standard to use. Currently only supports `ralbot.ipxact.Standard.IEEE_1685_2014`
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
