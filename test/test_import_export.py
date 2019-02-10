
from .unittest_utils import IPXACTTestCase
import filecmp

class TestImportExport(IPXACTTestCase):
    
    def test_symmetry(self):
        root = self.compile(
            ["test_sources/accelera-generic_example.rdl"]
        )

        with self.subTest("export 1"):
            self.export(root, "tmp.xml")

        with self.subTest("validate xsd 1"):
            self.validate_xsd("tmp.xml", "schema/index.xsd")

        with self.subTest("import"):
            root2 = self.compile(
                ["tmp.xml"]
            )

        with self.subTest("export 2"):
            self.export(root2, "tmp2.xml")

        with self.subTest("validate xsd 2"):
            self.validate_xsd("tmp.xml", "schema/index.xsd")

        with self.subTest("symmetry check"):
            self.compare("tmp.xml", "tmp2.xml")
