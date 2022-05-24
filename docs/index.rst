Introduction
============

This package implements IP-XACT import and export functionality for the PeakRDL
toolchain. This involves the ability to translate between a SystemRDL register
model and `Accelera's IP-XACT <https://www.accellera.org/downloads/standards/ip-xact>`_
data exchange document format.


Installing
----------

Install from `PyPi`_ using pip

.. code-block:: bash

    python3 -m pip install peakrdl-ipxact

.. _PyPi: https://pypi.org/project/peakrdl-ipxact



Quick Start
-----------

Exporting to IP-XACT
^^^^^^^^^^^^^^^^^^^^
Below is a simple example that shows how to convert a SystemRDL register model
into IP-XACT.

.. code-block:: python
    :emphasize-lines: 3, 13-15, 17

    import sys
    from systemrdl import RDLCompiler, RDLCompileError
    from peakrdl.ipxact import IPXACTExporter, Standard

    rdlc = RDLCompiler()

    try:
        rdlc.compile_file("path/to/my.rdl")
        root = rdlc.elaborate()
    except RDLCompileError:
        sys.exit(1)

    exporter = IPXACTExporter(
        standard=Standard.IEEE_1685_2014
    )

    exporter.export(root, "path/to/output.xml")



Importing IP-XACT
^^^^^^^^^^^^^^^^^
Below is a simple example of how to import an IP-XACT definition into the
register model.

.. code-block:: python
    :emphasize-lines: 3, 6, 9

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



Links
-----

- `Source repository <https://github.com/SystemRDL/PeakRDL-ipxact>`_
- `Release Notes <https://github.com/SystemRDL/PeakRDL-ipxact/releases>`_
- `Issue tracker <https://github.com/SystemRDL/PeakRDL-ipxact/issues>`_
- `PyPi <https://pypi.org/project/peakrdl-ipxact>`_



.. toctree::
    :hidden:

    self
    importer
    exporter
