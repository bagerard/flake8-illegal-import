# -*- coding: utf-8 -*-
import codecs

from setuptools import setup


def get_version():
    with open('flake8_illegal_import.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_prefix():
    with open('flake8_illegal_import.py') as f:
        for line in f:
            if line.startswith('CODE_PREFIX'):
                return eval(line.split('=')[-1])


def get_long_description():
    with codecs.open('README.rst', 'r', 'utf-8') as f:
        return f.read()


INSTALL_REQUIRES = ['flake8']
TESTS_REQUIRES = ['pytest', 'mock', 'pytest-cov']

setup(
    name='flake8-illegal-import',
    version=get_version(),
    description='illegal import detector, plugin for flake8',
    long_description=get_long_description(),
    keywords='flake8 import reject',
    maintainer='Bastien Gérard',
    maintainer_email='bastien.gerard@gmail.com',
    url='https://github.com/bagerard/flake8-illegal-import',
    license='MIT License',
    py_modules=['flake8_illegal_import'],
    zip_safe=False,
    entry_points={
        'flake8.extension': [
            '{prefix} = flake8_illegal_import:ImportChecker'.format(prefix=get_prefix()),
        ],
    },
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    setup_requires=['pytest-runner'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
