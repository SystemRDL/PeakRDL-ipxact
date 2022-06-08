# Load modules
import warnings

from peakrdl_ipxact import __about__
from peakrdl_ipxact import exporter
from peakrdl_ipxact import importer
from peakrdl_ipxact import typemaps

# hoist internal objects
from peakrdl_ipxact.__about__ import __version__
from peakrdl_ipxact.exporter import IPXACTExporter, Standard
from peakrdl_ipxact.importer import IPXACTImporter


warnings.warn(
"""
================================================================================
Importing via namespace package 'peakrdl.ipxact' is deprecated and will be
removed in the next release.
Change your imports to load the package using 'peakrdl_ipxact' instead.
For more details, see: https://github.com/SystemRDL/PeakRDL/issues/4
================================================================================
""", DeprecationWarning, stacklevel=2)
