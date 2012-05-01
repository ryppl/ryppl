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

def direct_successors(all_dumps, v):
    return set( fp.findtext('arg') for fp in all_dumps.get(v, Element('x')).findall('find-package') )

def indirect_successors(all_dumps, v):
    return set( fp.findtext('arg') for fp in all_dumps.get(v, Element('x')).findall('find-package-indirect') )

def usage_dependencies(all_dumps, v):
    return set( d.text for d in all_dumps.get(v, Element('x')).findall('depends/dependency') )

def usage_successors(all_dumps, v):
    succ = set()
    for s in direct_successors(all_dumps, v):
        succ |= set(x.text for x in all_dumps.get(v, Element('x')).findall('depends/dependency'))
    return succ

def successors(all_dumps, v):
    return direct_successors(all_dumps,v) | indirect_successors(all_dumps,v)

def run(dump_dir=None):
    all_dumps = read_dumps(dump_dir)
    print 'digraph boost {'
    print 'splines=true;'
    print 'layout=dot;'
    #print 'nodesep=3;'
    print 'overlap=scalexy;'
    for s, dump in all_dumps.items():
        if dump.find('libraries/library') is not None:
            print s, '[shape=box3d]'

        for t in direct_successors(all_dumps,s):
            if successors(all_dumps, t):
                print s,'->', t,'[style=bold]'

        for t in indirect_successors(all_dumps, s):
            if successors(all_dumps, t):
                print s,'->', t,'[style=dotted,arrowhead=open,color=gray]'

        for t in usage_successors(all_dumps, s):
            if usage_successors(all_dumps, t):
                print s,'->', t,'[style=dashed,arrowhead=open,color=blue]'
    print '}'

if __name__ == '__main__':
    argv = sys.argv
    run(dump_dir=Path(argv[1]) if len(argv) > 1 else None)
