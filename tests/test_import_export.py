import os

from peakrdl_ipxact.exporter import Standard

from .unittest_utils import IPXACTTestCase

from systemrdl.node import RegNode, FieldNode, MemNode

class TestImportExport(IPXACTTestCase):

    def symmetry_check(self, sources, std):
        a = self.compile(sources)

        xml_path = "%s.xml" % self.request.node.name

        with self.subTest("export"):
            self.export(a, xml_path, std)

        with self.subTest("validate xsd"):
            self.validate_xsd(xml_path, self.get_schema_path(std))

        with self.subTest("import"):
            b = self.compile([xml_path])

        # Compare equivalent
        a_nodes = [node for node in a.descendants(unroll=True, skip_not_present=False) if isinstance(node, (RegNode, FieldNode, MemNode))]
        b_nodes = [node for node in b.descendants(unroll=True, skip_not_present=False) if isinstance(node, (RegNode, FieldNode, MemNode))]
        self.assertEqual(len(a_nodes), len(b_nodes))
        for node_a, node_b in zip(a_nodes, b_nodes):
            self.compare_nodes(node_a, node_b)


    def test_generic_example_2014(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accelera-generic_example.rdl")
            ],
            Standard.IEEE_1685_2014
        )


    def test_generic_example_2009(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accelera-generic_example.rdl")
            ],
            Standard.IEEE_1685_2009
        )


    def test_nested_2014(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accelera-generic_example.rdl"),
                os.path.join(this_dir, "test_sources/nested.rdl")
            ],
            Standard.IEEE_1685_2014
        )


    def test_nested_2009(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accelera-generic_example.rdl"),
                os.path.join(this_dir, "test_sources/nested.rdl")
            ],
            Standard.IEEE_1685_2009
        )
