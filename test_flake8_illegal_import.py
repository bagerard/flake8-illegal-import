from __future__ import print_function

import ast
import os
from collections import namedtuple

import mock
from flake8.options.manager import OptionManager

from flake8_illegal_import import (Flake8Argparse, ImportChecker,
                                   format_code, resolve_path)

curr_dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_FILE_PATH = curr_dir_path + '/tests/files/sample.py'
SAMPLE_FILE_DIR = os.path.dirname(SAMPLE_FILE_PATH)

SysArgs = namedtuple('SysArgs', 'illegal_import_dir illegal_import_packages')


def get_tree(filename):
    with open(filename, 'rb') as f:
        return compile(f.read(), filename, 'exec', ast.PyCF_ONLY_AST, True)


class TestModuleUtils():
    def test_resolve_path_absolute(self):
        assert resolve_path('/tmp') == '/tmp'

    def test_resolve_path_relative(self):
        assert resolve_path('./tmp') == os.path.abspath('./tmp')

    def test_resolve_path_expand(self):
        assert resolve_path('~/tmp') == os.path.expanduser('~/tmp')

    def test_format_code(self):
        assert format_code(302) == "II302"


class TestFlake8Optparse():
    def test_add_options(self):
        flake8_opt_mgr = OptionManager()
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        plugin.add_options(flake8_opt_mgr)
        assert len(flake8_opt_mgr.options) == 2

    def test_parse_options(self):
        flake8_opt_mgr = OptionManager()
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir=SAMPLE_FILE_DIR, illegal_import_packages='os,json')
        plugin.parse_options(flake8_opt_mgr, args, extra_args=None)
        assert plugin.illegal_import_dir == args.illegal_import_dir
        assert plugin.illegal_import_packages == ['os', 'json']


class TestImportChecker():
    def test_get_illegal_imports(self):
        tree = get_tree(SAMPLE_FILE_PATH)

        banned_packages = ['os', 'json']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        expected = {1: 'os',
                    4: 'json',
                    6: 'os',
                    7: 'os'}

        assert errors == expected

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
        assert res == expected

    @mock.patch('flake8_illegal_import.ImportChecker.report')
    def test_run_no_package_name(self, reporter):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='/tmp', illegal_import_packages='')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)
        resp = list(checker.run())
        assert len(resp) == 0
        reporter.assert_called_once_with('No illegal import package set - skip checks')

    @mock.patch('flake8_illegal_import.ImportChecker.report')
    def test_run_dir_not_exist(self, reporter):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='./non-exist', illegal_import_packages='os')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)
        resp = list(checker.run())
        assert len(resp) == 0
        reporter.assert_called_once()
        assert 'WARNING: Directory configured does not exist:' in reporter.call_args_list[0][0][0]
