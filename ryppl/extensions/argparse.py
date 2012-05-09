# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from __future__ import absolute_import
from argparse import *

import os

def existing_directory(dirname):
    if not os.path.isdir(dirname):
        raise ArgumentTypeError('%r: not a directory' % dirname)
    return dirname
