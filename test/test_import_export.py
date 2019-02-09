
from .unittest_utils import IPXACTTestCase
import filecmp

class TestImportExport(IPXACTTestCase):
    
    def test_symmetry(self):
        root, env = self.compile(
            ["test_sources/accelera-generic_example.rdl"]
        )

        self.export(env, root, "tmp.xml")

        root2, env2 = self.compile(
            ["tmp.xml"]
        )

        self.export(env2, root2, "tmp2.xml")

        self.compare("tmp.xml", "tmp2.xml")