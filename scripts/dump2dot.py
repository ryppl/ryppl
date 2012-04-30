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

    from SCC import SCC
    def successors(v):
        return [
            lib for lib in (
                fp.findtext('arg') for fp
                in (all_dumps.get(v, Element('x')).findall('find-package')
                + all_dumps.get(v, Element('x')).findall('find-package-indirect'))
                )]

    sccs = SCC(lambda x:x, successors).getsccs(all_dumps)
    import pprint
    cyclic = set()
    for scc in sccs:
        if len(scc) > 1:
            cyclic |= set(scc)

    print 'digraph boost {'
    print 'layout=neato;'
    print 'overlap=scalexy;'
    print 'splines=true;'
    for s in cyclic:
        dump = all_dumps[s]
        if dump.find('libraries/library') is not None:
            print s, '[shape=box3d]'
        for t in [t.find('arg').text for t in dump.findall('find-package')]:
            if t in cyclic:
                print s,'->', t
        for t in dump.findall('find-package-indirect'):
            if t in cyclic:
                print s,'->', t.find('arg').text,'[style=dotted]'
    print '}'

if __name__ == '__main__':
    argv = sys.argv
    run(dump_dir=Path(argv[1]) if len(argv) > 1 else None)
