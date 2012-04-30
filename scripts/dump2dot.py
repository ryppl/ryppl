# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt

import glob, sys
from subprocess import check_output, check_call, Popen, PIPE
from xml.etree.cElementTree import ElementTree, Element
from path import Path
from read_dumps import read_dumps

def run(dump_dir=None):
    all_dumps = read_dumps(dump_dir)
    print 'overlap=false;'
    print 'rotate=90;'
    print 'digraph boost {'
    for s, dump in all_dumps.items():
        if dump.find('libraries/library') is not None:
            print s, '[shape=box3d]'
        for t in dump.findall('find-package'):
            print s,'->', t.find('arg').text
        # for t in dump.findall('find-package-indirect'):
        #     print s,'->', t.find('arg').text,'[style=dotted]'
    print '}'

if __name__ == '__main__':
    argv = sys.argv
    run(dump_dir=Path(argv[1]) if len(argv) > 1 else None)
