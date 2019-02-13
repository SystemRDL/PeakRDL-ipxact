
import unittest
import subprocess
import logging
import filecmp

from systemrdl import RDLCompiler
from systemrdl.messages import MessagePrinter
from ralbot.ipxact import IPXACTImporter, IPXACTExporter

#===============================================================================
class TestPrinter(MessagePrinter):
    def emit_message(self, lines):
        text = "\n".join(lines)
        logging.info(text)


#===============================================================================

class IPXACTTestCase(unittest.TestCase):

    def compile(self, files, top_name=None):
        rdlc = RDLCompiler(
            message_printer=TestPrinter()
        )
        ipxact = IPXACTImporter(rdlc)

        for file in files:
            if file.endswith(".rdl"):
                rdlc.compile_file(file)
            elif file.endswith(".xml"):
                ipxact.import_file(file)
        return rdlc.elaborate(top_name)
    
    def export(self, node, file):
        ipxact = IPXACTExporter()
        ipxact.export(node, file)

    def compare(self, file1, file2):

        self.assertTrue(filecmp.cmp(
            file1,
            file2
        ), 'file compare failed')
    
    def validate_xsd(self, file, xsd):

        file = file
        xsd = xsd
        cmd = ["xmllint", "--noout", "--schema", xsd, file]

        passed = True
        stderr = ""
        try:
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            passed = False
            stderr = e.output.decode("utf-8")
        
        if not passed:
            raise AssertionError("XML Validate failed: %s" % stderr)
