"""KiCad helpers: s-expression parser and netlist reader.
python tools/kinet.py <netlist.net>            -> prints every net with its pins
python tools/kinet.py <a.net> <b.net> [--ignore REF,..] -> compares the connectivity of two netlists (net names ignored)"""
import re, sys

TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def sexp(s):
    st = [[]]
    for t in TOK.findall(s):
        if t == '(':
            st.append([])
        elif t == ')':
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t[1:-1].replace('\\"', '"').replace('\\\\', '\\') if t.startswith('"') else t)
    return st[0][0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def val(node, key):
    f = find(node, key)
    return f[0][1] if f and len(f[0]) > 1 else None


def nets(path):
    root = sexp(open(path, encoding='utf-8').read())
    out = {}
    for n in find(find(root, 'nets')[0], 'net'):
        out[val(n, 'name')] = [(val(x, 'ref'), val(x, 'pin'), val(x, 'pinfunction')) for x in find(n, 'node')]
    return out


def groups(path, ignore=()):
    """Connectivity as a set of frozensets of 'REF.PIN' (net names ignored, single-pin nets dropped).
    `ignore`: references left out (parts added on purpose in a later revision)."""
    out = set()
    for v in nets(path).values():
        g = frozenset(f'{r}.{p}' for r, p, _ in v if r not in ignore)
        if len(g) > 1:
            out.add(g)
    return out


if __name__ == '__main__':
    if len(sys.argv) == 2:
        for k, v in sorted(nets(sys.argv[1]).items()):
            print(f'{k:24s}', ' '.join(f'{r}.{p}' + (f'({f})' if f else '') for r, p, f in v))
    else:
        ign = sys.argv[4].split(',') if len(sys.argv) > 4 and sys.argv[3] == '--ignore' else ()
        a, b = groups(sys.argv[1], ign), groups(sys.argv[2], ign)
        if ign:
            print('ignored (added in RevF2):', ', '.join(ign))
        print('only in A:'); [print('  ', sorted(x)) for x in a - b]
        print('only in B:'); [print('  ', sorted(x)) for x in b - a]
        print('IDENTICAL' if a == b else 'DIFFERENT')
