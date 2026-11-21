"""Minimal LTspice binary .raw reader (transient, uncompressed). Returns dict name->np.array."""
import numpy as np
def read(fn, want=None):
    d = open(fn, 'rb').read()
    k = d.find('Binary:\n'.encode('utf-16-le'))
    hdr = d[:k].decode('utf-16-le'); body = d[k + len('Binary:\n') * 2:]
    lines = hdr.splitlines(); nv = npnt = 0; names = []; dbl = False; off = 0.0
    for i, l in enumerate(lines):
        if l.startswith('No. Variables:'): nv = int(l.split(':')[1])
        if l.startswith('No. Points:'): npnt = int(l.split(':')[1])
        if l.startswith('Offset:'): off = float(l.split(':')[1])
        if l.startswith('Flags:') and 'double' in l: dbl = True
        if l.startswith('Variables:'):
            names = [lines[i + 1 + j].split('\t')[2] for j in range(nv)]
    if dbl:
        a = np.frombuffer(body, dtype=np.float64, count=nv * npnt).reshape(npnt, nv); t = a[:, 0]
        cols = {n: a[:, j] for j, n in enumerate(names)}
    else:
        rec = np.dtype([('t', '<f8')] + [(f'v{j}', '<f4') for j in range(1, nv)])
        a = np.frombuffer(body, dtype=rec, count=npnt)
        cols = {names[0]: np.abs(a['t']) + off}
        for j in range(1, nv): cols[names[j]] = a[f'v{j}'].astype(np.float64)
    out = {}
    for n, v in cols.items():
        key = n.replace('time', 't')
        if want is None or key in want or n in want: out[n if n != 'time' else 't'] = v
    return out

def avg(t, y, t0=None, t1=None):
    m = np.ones_like(t, bool)
    if t0 is not None: m &= t >= t0
    if t1 is not None: m &= t <= t1
    tt, yy = t[m], y[m]
    return np.trapezoid(yy, tt) / (tt[-1] - tt[0])
def rms(t, y, t0=None, t1=None): return np.sqrt(avg(t, y * y, t0, t1))
