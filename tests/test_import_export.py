import os

from peakrdl_ipxact.exporter import Standard

from .unittest_utils import IPXACTTestCase

from systemrdl.node import RegNode, FieldNode, MemNode
from systemrdl.rdltypes.builtin_enums import AccessType

class TestImportExport(IPXACTTestCase):

    def symmetry_check(self, sources, std):
        a = self.compile(sources)

        xml_path = "%s.xml" % os.path.join(self.tempdir.name, self.id())

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
                os.path.join(this_dir, "test_sources/accellera-generic_example.rdl")
            ],
            Standard.IEEE_1685_2014
        )


    def test_generic_example_2009(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accellera-generic_example.rdl")
            ],
            Standard.IEEE_1685_2009
        )


    def test_nested_2014(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accellera-generic_example.rdl"),
                os.path.join(this_dir, "test_sources/nested.rdl")
            ],
            Standard.IEEE_1685_2014
        )


    def test_nested_2009(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accellera-generic_example.rdl"),
                os.path.join(this_dir, "test_sources/nested_allpresent.rdl")
            ],
            Standard.IEEE_1685_2009
        )

    def test_import_xml(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(this_dir, "test_sources/example.xml")

        root = self.compile([xml_path])

        field = root.find_by_path('top.some_regfile.some_reg.f1')
        self.assertIsNotNone(field)
        self.assertEqual(field.get_property("sw"), AccessType.rw)

        field = root.find_by_path('top.some_other_regfile.some_other_reg.f2')
        self.assertIsNotNone(field)
        self.assertEqual(field.get_property("sw"), AccessType.r)

    def test_import_xml_with_name_filter(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(this_dir, "test_sources/example.xml")

        root = self.compile([xml_path], name_filter_regex=r'.*_other_.*')

        self.assertIsNone(root.find_by_path('top.some_regfile'))

        field = root.find_by_path('top.some_other_reg.f2')
        self.assertIsNotNone(field)
        self.assertEqual(field.get_property("sw"), AccessType.r)
