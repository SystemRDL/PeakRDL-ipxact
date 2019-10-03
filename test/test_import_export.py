import os
import filecmp
import tempfile

from ralbot.ipxact.exporter import Standard

from .unittest_utils import IPXACTTestCase

class TestImportExport(IPXACTTestCase):
    
    def symmetry_check(self, sources, std):
        this_dir = os.path.dirname(os.path.realpath(__file__))

        root = self.compile(sources)
        
        t1 = tempfile.NamedTemporaryFile(delete=False, dir=this_dir, suffix=".xml")
        t1.close()
        t2 = tempfile.NamedTemporaryFile(delete=False, dir=this_dir, suffix=".xml")
        t2.close()

        with self.subTest("export 1"):
            self.export(root, t1.name, std)

        with self.subTest("validate xsd 1"):
            self.validate_xsd(t1.name, self.get_schema_path(std))

        with self.subTest("import"):
            root2 = self.compile(
                [t1.name]
            )

        with self.subTest("export 2"):
            self.export(root2, t2.name, std)

        with self.subTest("validate xsd 2"):
            self.validate_xsd(t2.name, self.get_schema_path(std))

        with self.subTest("symmetry check"):
            self.compare(t1.name, t2.name)



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
