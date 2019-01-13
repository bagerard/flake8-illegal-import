from __future__ import print_function

import ast
import os
from collections import namedtuple
import unittest
from flake8_illegal_import import ImportChecker

curr_dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_FILE_PATH = curr_dir_path + '/tests/files/sample.py'

SysArgs = namedtuple('SysArgs', 'illegal_import_dir illegal_import_packages')


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

    def test_run(self):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='./', illegal_import_packages='os,json')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)

        expected = [
            (1, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (4, 0, 'II101 importing this package is forbidden in this directory (json)', ImportChecker),
            (6, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (7, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
        ]
        res = list(checker.run())
        self.assertEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
