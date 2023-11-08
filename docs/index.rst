Introduction
============

This package implements IP-XACT import and export functionality for the PeakRDL
toolchain. This involves the ability to translate between a SystemRDL register
model and `Accellera's IP-XACT <https://www.accellera.org/downloads/standards/ip-xact>`_
data exchange document format.


Installing
----------

Install from `PyPi`_ using pip

.. code-block:: bash

    python3 -m pip install peakrdl-ipxact

.. _PyPi: https://pypi.org/project/peakrdl-ipxact


Example
-------
The easiest way to use PeakRDL-ipxact is via the `PeakRDL command line tool <https://peakrdl.readthedocs.io/>`_:

.. code-block:: bash

    # Install the command line tool
    python3 -m pip install peakrdl

    # Convert SystemRDL to IP-XACT
    peakrdl ip-xact your_design.rdl -o your_design.xml

    # Convert IP-XACT to SystemRDL
    peakrdl systemrdl your_design.xml -o your_design.rdl



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
