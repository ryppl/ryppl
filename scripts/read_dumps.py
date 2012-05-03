# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt
import glob
from xml.etree.cElementTree import ElementTree, Element
from path import Path

class lazydict(dict):
    def __init__(self, factory, *args, **kw):
        self.__factory = factory
        dict.__init__(self, *args,**kw)

    __missing = object()
    def __getitem__(self, x):
        x = self.get(x,self.__missing)
        return self.__factory() if x is self.__missing else x

def read_dumps(dump_dir = None):
    if dump_dir is None:
        ryppl = Path('/Users/dave/src/ryppl')
        dump_dir = ryppl / 'feeds' / 'dumps'

    all_dumps = lazydict(lambda:Element('__NOT_WHAT_YOURE_LOOKING_FOR__'))
    for cmake_dump_file in glob.glob(dump_dir/'*.xml'):
        cmake_dump = ElementTree()
        cmake_dump.parse(cmake_dump_file)
        camel_name = Path(cmake_dump_file).namebase
        all_dumps[camel_name] = cmake_dump

    return all_dumps
