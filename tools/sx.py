"""Quote-preserving s-expression reader/writer for KiCad files."""
import re

TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


class Q(str):
    """A string that was (or must be) written in double quotes."""


def parse(s):
    st = [[]]
    for t in TOK.findall(s):
        if t == '(':
            st.append([])
        elif t == ')':
            x = st.pop(); st[-1].append(x)
        elif t.startswith('"'):
            st[-1].append(Q(t[1:-1].replace('\\"', '"').replace('\\\\', '\\')))
        else:
            st[-1].append(t)
    return st[0][0]


def q(v):
    return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(x, ind=0):
    if not isinstance(x, list):
        return q(x) if isinstance(x, Q) else str(x)
    inner = [dump(c, ind + 1) for c in x[1:]]
    if sum(len(i) for i in inner) < 90 and not any('\n' in i for i in inner):
        return '(' + ' '.join([str(x[0])] + inner) + ')'
    pad = '\n' + '\t' * (ind + 1)
    return '(' + str(x[0]) + ''.join(pad + i for i in inner) + '\n' + '\t' * ind + ')'


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def first(node, key):
    f = find(node, key)
    return f[0] if f else None


def num(v):
    s = '%.4f' % v
    return s.rstrip('0').rstrip('.') if '.' in s else s
