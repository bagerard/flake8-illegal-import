from __future__ import print_function

import ast
import os
import unittest
from flake8_illegal_import import ImportChecker

curr_dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_FILE_PATH = curr_dir_path + '/tests/files/sample.py'


def get_tree(filename):
    with open(filename, 'rb') as f:
        return compile(f.read(), filename, 'exec', ast.PyCF_ONLY_AST, True)


class TestImportDetector(unittest.TestCase):
    def test_get_illegal_imports(self):
        tree = get_tree(SAMPLE_FILE_PATH)

        banned_packages = ['os', 'json']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        expected = {1: 'os',
                    4: 'json',
                    6: 'os',
                    7: 'os'}

        self.assertEqual(errors, expected)

if __name__ == '__main__':
    unittest.main()
