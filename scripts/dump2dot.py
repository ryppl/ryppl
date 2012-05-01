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

colors=('red','green','orange', 'blue', 'indigo', 'violet')

def first(seq):
    return iter(seq).next()

def run(dump_dir=None):
    all_dumps = read_dumps(dump_dir)
    g = all_dumps

    # find all strongly-connected components
    from SCC import SCC
    sccs = SCC(str, lambda i: successors(g, i)).getsccs(g)

    # map each vertex to a scc set
    scc = {}
    for component in sccs:
        s = set(component)
        for u in s:
            scc[u] = s

    long_sccs = [s for s in sccs if len(s) > 1]

    # color each vertex in an SCC of size > 1 according to its SCC
    color = {}
    for i,s in enumerate(long_sccs):
        for u in s:
            color[u] = colors[i]

    V = set(u for u in g if successors(g,u))
    t_redux = dict((s, set(t for t in successors(g, s) if t in V)) for s in V)

    for component in sccs:
        representative = first(component)
        if representative not in V:
            continue
        
        # Keep only one representative link to each other component
        visited = set()
        scc_s = scc[representative]

        for s in component:
            succs = t_redux[s]
            for t in list(succs):
                scc_t = scc[t]
                if id(scc_t) in visited:
                    succs.remove(t)
                elif id(scc_t) != id(scc_s):
                    visited.add(id(scc_t))
                
        N = len(scc_s)
        if N > 1:
            # replace SCCs with simple cycles
            next = dict((component[i], component[(i+1)%N]) for i in range(N))
            for u in component:
                t_redux[u] -= set(v for v in component if v != next[u])
                t_redux[u].add(next[u])
    
    direct = dict((s, set(t for t in direct_successors(g, s) if t in V)) for s in V)

    print 'digraph boost {'
    print 'splines=true;'
    print 'layout=dot;'
    #print 'nodesep=3;'
    print 'overlap=scalexy;'
    for s in V:
        c = color.get(s,'black')

        if all_dumps[s].find('libraries/library') is not None:
            print s, '[shape=box3d,color=%s]'%c
        else:
            print s, '[color=%s]'%c

        direct_edges = direct.get(s,set())
        for t in direct_edges:
            print s,'->', t,'[style=bold]'

        for t in t_redux.get(s,set()):
            if t not in direct_edges:
                print s,'->', t,'[style=dashed,arrowhead=open,color=blue]'
    print '}'

if __name__ == '__main__':
    argv = sys.argv
    run(dump_dir=Path(argv[1]) if len(argv) > 1 else None)
