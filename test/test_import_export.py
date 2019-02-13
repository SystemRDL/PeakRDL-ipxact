
from .unittest_utils import IPXACTTestCase
import filecmp
import tempfile
import os

class TestImportExport(IPXACTTestCase):
    
    def symmetry_check(self, sources):
        this_dir = os.path.dirname(os.path.realpath(__file__))

        root = self.compile(sources)
        
        t1 = tempfile.NamedTemporaryFile(delete=False, dir=this_dir, suffix=".xml")
        t1.close()
        t2 = tempfile.NamedTemporaryFile(delete=False, dir=this_dir, suffix=".xml")
        t2.close()

        with self.subTest("export 1"):
            self.export(root, t1.name)

        with self.subTest("validate xsd 1"):
            self.validate_xsd(t1.name, os.path.join(this_dir, "schema/index.xsd"))

        with self.subTest("import"):
            root2 = self.compile(
                [t1.name]
            )

        with self.subTest("export 2"):
            self.export(root2, t2.name)

        with self.subTest("validate xsd 2"):
            self.validate_xsd(t2.name, os.path.join(this_dir, "schema/index.xsd"))

        with self.subTest("symmetry check"):
            self.compare(t1.name, t2.name)

    def test_generic_example(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check([
            os.path.join(this_dir, "test_sources/accelera-generic_example.rdl")
        ])

    def test_nested(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check([
            os.path.join(this_dir, "test_sources/accelera-generic_example.rdl"),
            os.path.join(this_dir, "test_sources/nested.rdl")
        ])
