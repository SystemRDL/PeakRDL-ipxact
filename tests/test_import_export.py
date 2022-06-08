import os

from peakrdl_ipxact.exporter import Standard

from .unittest_utils import IPXACTTestCase

class TestImportExport(IPXACTTestCase):

    def symmetry_check(self, sources, std):
        root = self.compile(sources)

        export1_path = "%s-x1.xml" % self.request.node.name
        export2_path = "%s-x2.xml" % self.request.node.name

        with self.subTest("export 1"):
            self.export(root, export1_path, std)

        with self.subTest("validate xsd 1"):
            self.validate_xsd(export1_path, self.get_schema_path(std))

        with self.subTest("import"):
            root2 = self.compile([export1_path])

        with self.subTest("export 2"):
            self.export(root2, export2_path, std)

        with self.subTest("validate xsd 2"):
            self.validate_xsd(export2_path, self.get_schema_path(std))

        with self.subTest("symmetry check"):
            self.compare(export1_path, export2_path)



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
