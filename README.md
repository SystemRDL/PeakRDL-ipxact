[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ralbot-html.svg)](https://pypi.org/project/ralbot-html)

# RALBot-ipxact
Convert compiled SystemRDL input into IP-XACT XML

## Installing
Install from [PyPi](https://pypi.org/project/ralbot-ipxact) using pip:

    python3 -m pip install ralbot-ipxact


## Usage
Pass the elaborated output of the [SystemRDL Compiler](http://systemrdl-compiler.readthedocs.io)
into the exporter.

Assuming `root` is the elaborated top-level node, or an internal `AddrmapNode`:

```python
from ralbot.ipxact import IPXACTExporter

exporter = IPXACTExporter()

exporter.export(root, "path/to/output.xml")
```


## Reference

### `IPXACTExporter(**kwargs)`
Constructor for the HTML exporter class

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
