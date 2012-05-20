# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from ryppl.support import _zeroinstall
from logging import info

def cmake(args, **kw):
    info('cmake-2.8.8+ %s', args)
    _zeroinstall.launch(
        ['--not-before=2.8.8', 'https://raw.github.com/ryppl/feeds/gh-pages/cmake.xml'] + args
        , **kw)

