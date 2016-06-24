#!/usr/bin/env python3
import re
import sys
import functools

graph_re = re.compile(r'(HAVE_DOT\s+=).*')

def doxy_adapt(filein, fileout=sys.stdout):
    doxy_print = functools.partial(print, file=fileout)

    for line in filein:
        line = line.strip()
        if not line.startswith('#'):
            graph_obj = graph_re.match(line)
            if graph_obj:
                doxy_print(graph_obj.group(1),'NO')
                continue

            doxy_print(line)

if __name__ == '__main__':
    import fileinput
    doxy_adapt(fileinput.input())