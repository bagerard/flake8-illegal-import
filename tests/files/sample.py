import os
import ast
import codecs
import json as jayson
import collections, abc

import os.path
from os.path import expanduser

from .test import nothing


def funky_method_that_import():
    from os.path import abspath
    from json import dumps
    return
