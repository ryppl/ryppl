from xml.etree.cElementTree import Element
from lazydict import lazydict

def direct_successors(dumps, v):
    ret = set(fp.findtext('arg') for fp in dumps[v].findall('find-package'))
    ret.discard(v)
    return ret

def usage_successors(dumps, v):
    ret = set(d.text for succ in direct_successors(dumps,v) 
              for d in dumps[succ].findall('depends/dependency') )
    ret.discard(v)
    return ret

def successors(dumps, v):
    return direct_successors(dumps,v) | usage_successors(dumps,v)

def to_mutable_graph(dumps, successor_function=successors, vertex_filter=lambda x:True):
    return lazydict(
        set 
      , ((v, set(x for x in successor_function(dumps,v) 
                 if vertex_filter(x)))
         for v in dumps if vertex_filter(v)))

def run(dump_dir=None):
    from read_dumps import read_dumps
    from display_graph import show_digraph, show_digraph2
    from transitive import inplace_transitive_reduction
    dumps = read_dumps(dump_dir)
    
    direct = to_mutable_graph(dumps, direct_successors)
    usage = to_mutable_graph(dumps, usage_successors)

    inplace_transitive_reduction(direct)
    inplace_transitive_reduction(usage)
    
    show_digraph2(direct, usage, layout='neato', overlap='false', splines='True')

    # from pprint import pprint
    # pprint(direct)

    from SCC import SCC
    sccs = SCC(str, lambda i: successors(dumps, i)).getsccs(dumps)
    long_sccs = [s for s in sccs if len(s) > 1]
    assert len(long_sccs) == 0, str(long_sccs)

if __name__ == '__main__':
    import sys
    run(None if len(sys.argv) == 1 else sys.argv[1])
