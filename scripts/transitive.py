# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt
def inplace_transitive_closure(g):
    """g is an adjacency list graph implemented as a dict of sets"""
    done = False
    while not done:
        done = True
        for v0, v1s in g.items():
            old_len = len(v1s)
            for v2s in [g[v1] for v1 in v1s]:
                if isinstance(v1s,dict):
                    v1s.update(v2s)
                else:
                    v1s |= v2s
            done = done and len(v1s) == old_len

def inplace_transitive_distance(g):
    """g is an adjacency list graph implemented as a dict of dicts.
    The keys in the outgoing edge list are target vertices, and the
    values are
    """
    done = False
    while not done:
        done = True
        for v0, v1s in g.items():
            for v1 in list(v1s):
                v2s = g[v1]
                for v2 in list(v2s):
                    d = v1s[v1] + v2s[v2]
                    if v2 not in v1s or v1s[v2] > d:
                        v1s[v2] = d
                        done = False

if __name__ == '__main__':
    def random_graph(max, a, b):
        g = {}
        for x in range(1,max):
            g[x] = dict((y,1) for y in range(1,max) if (x*x+y) % a == b)
        return g
    
    g0 = random_graph(7,11,5)
    g1 = random_graph(7,11,5)
    inplace_transitive_distance(g1)
    from display_graph import *
    show_digraph2(g0,g1,colors=['black','gray','black'])
    from pprint import pprint
    pprint(g1)

    max = 14
    g = {}
    for x in range(1,max):
        g[x] = set()
        for y in range(1,max):
            if x % y % 7 == 0:
                g[x].add(y)

    pprint(g)
    print '---------------'
    inplace_transitive_closure(g)
    pprint(g)

