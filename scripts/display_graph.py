import tempfile
import subprocess

class Formatter:
    def vertex_attributes(self, s):
        return None
    def edge_attributes(self, s, t):
        return None

def digraph(g, formatter=Formatter()):
    result = ['digraph G {','    splines=true;','    overlap=scalexy;']

    for s in g:
        line = '    %s' % s
        a = formatter.vertex_attributes(s)
        if a and len(a):
            line += ' [%s]' % ','.join(a)
        result.append(line)

        for t in g[s]:
            line = '        %s -> %s' % (s,t)
            a = formatter.edge_attributes(s,t)
            if a and len(a):
                line += ' [%s]' % ','.join(a)
            result.append(line)

    result.append('}')
    return '\n'.join(result)

def show_digraph(g, layout='neato', formatter=Formatter()):
    graph = tempfile.NamedTemporaryFile(suffix='.gv')
    graph.write(digraph(g))
    graph.flush()

    svg = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
    print (svg.name,graph.name)
    svg.write(
        subprocess.check_output(['dot','-Tsvg','-K'+layout,graph.name]))
    svg.flush()
    subprocess.check_call(['open',svg.name])
    
if __name__ == '__main__':
    g = {}
    max = 15
    for x in range(1,max):
        g[x] = set()
        for y in range(1,max):
            if (x*x+y) % 11 == 5:
                g[x].add(y)

    import pprint
    pprint.pprint(g)
    show_digraph(g,layout='dot')
