Illegal import checker
===============================

An extension for `Flake8 <https://pypi.python.org/pypi/flake8>`_ to make sure
that certain packages aren't imported in a directory


Standalone script
-----------------

The checker can be used directly::

  $ python -m flake8_illegal_import some_file.py
  some_file.py:1:1: P101 format string does contain unindexed parameters

Even though Flake8 still uses ``optparse`` this script in standalone mode
is using ``argparse``.


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-illegal-import`` are installed, the plugin
is available in ``flake8``::

  $ flake8 --version
  3.0.2 (flake8-illegal-import: 0.1.0, […]


Parameters
----------

This module requires 2 parameters:
--illegal-import-dir={path}
--illegal-import-packages={pkg1},{pkg2}

E.g usage::

  $ flake8 ./sample.py --illegal-import-dir=./ --illegal-import-packages=os --select=II101

>>/home/.../test/sample.py:14:1: II101 importing this package is forbidden in this directory (os)


Error codes
-----------

This plugin is using the following error codes:

+---------------------------------------------------------------------+
| Presence of implicit parameters                                     |
+-------+-------------------------------------------------------------+
| II101 | importing this package is forbidden in this directory {pkg} |
+-------+-------------------------------------------------------------+


Operation
---------

The plugin will go through all ``bytes``, ``str`` and ``unicode`` instances. If
it encounters ``bytes`` instances on Python 3, it'll decode them using ASCII and
if that fails it'll skip that entry.

The strings are basically sorted into three types corresponding to the P1XX
range. Only the format string can cause all errors while any other string can
only cause the corresponding P1XX error.

For this plugin all strings which are the first expression of the module or
after a function or class definition are considered docstrings.

If the ``format`` method is used on a string or ``str.format`` with the string
as the first parameter, it will consider this a format string and will analyze
the parameters of that call. If that call uses variable arguments, it cannot
issue P201 and P202 as missing entries might be hidden in those variable
arguments. P301 and P302 can still be checked for any argument which is defined
statically.


Changes
-------

0.1.0 - 2019-01-XX
``````````````````
* Initial release
