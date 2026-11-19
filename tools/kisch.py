"""Read/write helpers for KiCad .kicad_sch files (s-expressions): symbol instances, library pins, pin positions."""
import math, re, uuid
from kinet import sexp, find, val

Q = lambda s: '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(x, ind=0):
    """s-expression list -> text (strings quoted unless they are plain atoms)."""
    if not isinstance(x, list):
        return x
    head = x[0]
    parts = []
    for c in x[1:]:
        if isinstance(c, list):
            parts.append('\n' + '\t' * (ind + 1) + dump(c, ind + 1))
        else:
            parts.append(' ' + atom(c))
    return '(' + head + ''.join(parts) + ')'


ATOMS = {'yes', 'no', 'hide', 'none', 'default', 'solid', 'dash', 'dot', 'outline', 'background', 'left', 'right', 'top',
         'bottom', 'input', 'output', 'bidirectional', 'tri_state', 'passive', 'free', 'unspecified', 'power_in',
         'power_out', 'open_collector', 'open_emitter', 'no_connect', 'line', 'inverted', 'clock', 'inverted_clock',
         'input_low', 'clock_low', 'output_low', 'edge_clock_high', 'non_logic', 'mirror', 'x', 'y', 'true', 'false',
         'power', 'italic', 'bold', 'hide', 'local', 'global', 'stroke'}


def atom(c):
    if re.fullmatch(r'-?\d+(\.\d+)?', c) or c in ATOMS:
        return c
    return Q(c)


class Sch:
    def __init__(self, path):
        self.text = open(path, encoding='utf-8').read()
        self.root = sexp(self.text)
        self.lib = {val(s, 'symbol') if False else s[1]: s for s in find(find(self.root, 'lib_symbols')[0], 'symbol')}
        self.syms = find(self.root, 'symbol')

    @staticmethod
    def prop(sym, name):
        for p in find(sym, 'property'):
            if p[1] == name:
                return p[2]

    def pins(self, lib_id, unit=1):
        """{pin number: (x, y, angle, length)} in library coordinates (y up)."""
        out = {}

        def walk(node):
            for c in node:
                if isinstance(c, list) and c and c[0] == 'symbol':
                    m = re.search(r'_(\d+)_(\d+)$', c[1])
                    if m and int(m.group(1)) not in (0, unit):
                        continue
                    walk(c)
                elif isinstance(c, list) and c and c[0] == 'pin':
                    at = find(c, 'at')[0]; ln = find(c, 'length')[0]
                    num = find(c, 'number')[0][1]; nm = find(c, 'name')[0][1]
                    out[num] = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, float(ln[1]), nm, c[1])
        walk(self.lib[lib_id])
        return out


def place(px, py, x, y, rot, mirror=None):
    """library pin point (y up) -> schematic point for a symbol at (x, y) rotated rot (deg, CCW on screen)."""
    lx, ly = px, -py                       # to screen coordinates (y down)
    if mirror == 'x':
        ly = -ly
    elif mirror == 'y':
        lx = -lx
    a = math.radians(rot)
    # KiCad rotates symbols counter-clockwise on screen; in y-down coordinates that is (x, y) -> (x cos + y sin, -x sin + y cos)
    rx = lx * math.cos(a) + ly * math.sin(a)
    ry = -lx * math.sin(a) + ly * math.cos(a)
    return round(x + rx, 4), round(y + ry, 4)


def uid():
    return str(uuid.uuid4())
