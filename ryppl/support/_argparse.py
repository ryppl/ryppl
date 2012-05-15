# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from argparse import *

import os

def existing_directory(dirname):
    if not os.path.isdir(dirname):
        raise ArgumentTypeError('%r: not a directory' % dirname)
    return dirname

def valid_0install_feed(uri):
    from zeroinstall.injector.model import canonical_iface_uri
    from zeroinstall import SafeException
    try:
        return canonical_iface_uri(uri)
    except SafeException, e:
        raise ArgumentTypeError(e)
