#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Extension for flake8 to reject specific imports"""
from __future__ import print_function, unicode_literals

import ast
from collections import namedtuple

import sys
import os.path

try:
    import argparse
except ImportError as e:
    argparse = e

__version__ = '0.1.0'


CODE_PREFIX = "II"


def format_code(code):
    return '{}{}'.format(CODE_PREFIX, code)


def resolve_path(dir_path):
    dir_path = os.path.expanduser(dir_path)
    return os.path.abspath(dir_path)


class Flake8Argparse(object):

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = resolve_path(filename)

    @classmethod
    def add_options(cls, option_manager):
        option_manager.add_option(
            "--illegal-import-dir", type="str", default="./",
            parse_from_config=True,
            help="Directory to consider when looking for illegal import",
        )

        option_manager.add_option(
            "--illegal-import-packages", type="str", parse_from_config=True,
            help="Set packages that are not allowed in directory",
        )

    @classmethod
    def parse_options(cls, option_manager, options, extra_args):
        cls.illegal_import_dir = resolve_path(options.illegal_import_dir)
        cls.illegal_import_packages = [pkg for pkg in options.illegal_import_packages.split(',') if pkg]    # Allows for "package," as option

    @classmethod
    def add_arguments(cls, parser):
        pass


def create_parser(plugin_class, codes):
    def handler(value):
        if value:
            ignored = set(value.split(','))
            unrecognized = ignored - codes
            ignored &= codes
            if unrecognized:
                invalid = set()
                for invalid_code in unrecognized:
                    no_valid = True
                    if not invalid:
                        for valid_code in codes:
                            if valid_code.startswith(invalid_code):
                                ignored.add(valid_code)
                                no_valid = False
                    if no_valid:
                        invalid.add(invalid_code)
                if invalid:
                    raise argparse.ArgumentTypeError(
                        'The code(s) is/are invalid: "{0}"'.format(
                            '", "'.join(invalid)))
            return ignored
        else:
            return set()

    if isinstance(argparse, ImportError):
        print('argparse is required for the standalone version.')
        return False

    parser = argparse.ArgumentParser()
    parser.add_argument('--ignore', type=handler, default='',
                        help='Ignore the given comma-separated codes')
    parser.add_argument('files', nargs='+')
    plugin_class.add_arguments(parser)
    return parser


def handle_plugin(plugin_class, parser, args):
    args = parser.parse_args(args)
    if hasattr(plugin_class, 'parse_options'):
        plugin_class.parse_options(args)
    failed = False
    for filename in args.files:
        with open(filename, 'rb') as f:
            tree = compile(f.read(), filename, 'exec', ast.PyCF_ONLY_AST, True)
        for line, char, msg, checker in plugin_class(tree, filename).run():
            if msg[:4] not in args.ignore:
                print('{0}:{1}:{2}: {3}'.format(filename, line, char + 1, msg))
                failed = True
    return not failed


def execute(plugin_class, args, choices):
    parser = create_parser(plugin_class, choices)
    if parser is not False:
        return handle_plugin(plugin_class, parser, args)
    else:
        return False


def root_package_name(name):
    tree = ast.parse(name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            return node.id
    else:
        return None


ImportedPackage = namedtuple('ImportedPackage', 'name node')


class ImportVisitor(ast.NodeVisitor):

    def __init__(self):
        self.imported_packages = []

    def visit_Import(self, node):  # noqa: N802
        if node.col_offset == 0:
            modules = [alias.name for alias in node.names]
            self.imported_packages.append(
                ImportedPackage(root_package_name(modules[0]), node)
            )

    def visit_ImportFrom(self, node):  # noqa: N802
        if node.col_offset == 0:
            module = node.module or ''
            if node.level > 0:
                # ignore application relative
                return

            self.imported_packages.append(
                ImportedPackage(root_package_name(module), node)
            )


class ImportChecker(Flake8Argparse):

    version = __version__
    name = 'illegal-import'

    ERRORS = {
        101: 'importing this package is forbidden in this directory ({package})',
    }

    def _generate_error(self, node, code, **params):
        msg = '{0} {1}'.format(format_code(code), self.ERRORS[code])
        msg = msg.format(**params)
        return node.lineno, node.col_offset, msg, type(self)

    @staticmethod
    def get_illegal_imports(tree, banned_packages):
        visitor = ImportVisitor()
        visitor.visit(tree)

        for package_name, node in visitor.imported_packages:
            if package_name in banned_packages:
                yield (node, package_name)

    def run(self):
        dir_path = self.illegal_import_dir
        banned_packages = set(self.illegal_import_packages)

        if not banned_packages:
            print('No illegal import package set - skip checks')
            return

        if not os.path.isdir(dir_path):
            print('WARNING: Directory configured does not exist: {}'.format(dir_path))
            return

        if not self.filename.startswith(dir_path):
            # File not concerned by the restriction
            return

        for node, pkg in ImportChecker.get_illegal_imports(self.tree, banned_packages):
            yield self._generate_error(node, 101, package=pkg)


def main(args):
    choices = set('{0}'.format(format_code(code)) for code in ImportChecker.ERRORS)
    return execute(ImportChecker, args, choices)


if __name__ == '__main__':
    main(sys.argv[1:])
