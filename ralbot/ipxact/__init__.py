from .__about__ import __version__

from .exporter import IPXACTExporter
from .importer import IPXACTImporter

import warnings
warnings.warn(
"""
================================================================================
The RALBot-ipxact project has been deprecated and renamed to PeakRDL-ipxact.
Please update your dependencies to continue receiving the latest updates.
For details, see: https://github.com/SystemRDL/PeakRDL/issues/2
================================================================================
"""
) 
