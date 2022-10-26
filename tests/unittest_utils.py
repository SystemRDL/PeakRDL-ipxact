import os
import unittest
import subprocess
import logging
import pytest

from systemrdl import RDLCompiler
from systemrdl.messages import MessagePrinter
from systemrdl.node import Node, RegNode, FieldNode, MemNode
from peakrdl_ipxact import IPXACTImporter, IPXACTExporter
from peakrdl_ipxact.exporter import Standard

#===============================================================================
class TestPrinter(MessagePrinter):
    def emit_message(self, lines):
        text = "\n".join(lines)
        logging.info(text)


#===============================================================================

class IPXACTTestCase(unittest.TestCase):

    #: this gets auto-loaded via the _load_request autouse fixture
    request = None # type: pytest.FixtureRequest

    @pytest.fixture(autouse=True)
    def _load_request(self, request):
        self.request = request

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
        return rdlc.elaborate(top_name, "top")

    def compare_nodes(self, a: Node, b: Node):
        self.assertEqual(a.inst_name, b.inst_name)
        self.assertEqual(type(a), type(b))

        if isinstance(a, RegNode):
            self.assertEqual(a.absolute_address, b.absolute_address)
        if isinstance(a, FieldNode):
            self.assertEqual(a.lsb, b.lsb)
            self.assertEqual(a.msb, b.msb)

        props = set(a.list_properties() + b.list_properties())
        # Only check a subset of properties
        check_props = {
            'name', 'desc', 'regwidth', 'sw', 'reset', 'onread', 'memwidth', 'mementries'
        }
        for prop in props:
            if prop not in check_props:
                continue
            print(prop, a, b)
            self.assertEqual(a.get_property(prop), b.get_property(prop))

    def export(self, node, file, std):
        ipxact = IPXACTExporter(standard=std)
        ipxact.export(node, file, component_name="my_thing")

    def validate_xsd(self, file, xsd):
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


    def get_schema_path(self, std):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        if std == Standard.IEEE_1685_2014:
            return os.path.join(this_dir, "schema/1685-2014/index.xsd")
        elif std == Standard.IEEE_1685_2009:
            return os.path.join(this_dir, "schema/1685-2009/index.xsd")
        else:
            raise NotImplementedError
