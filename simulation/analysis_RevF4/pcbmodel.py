"""Shared PCB grid helpers: copper coverage at coarse resolution, footprint lookup."""
import numpy as np, json
D = np.load('cu.npz'); M = json.load(open('cu.json'))
LAYERS = ['F', 'In1', 'In2', 'B']
RES0 = M['RES']; NETS = M['nets']; FPS = {f['ref']: f for f in M['fps']}

def coverage(f):
    """per-layer copper fraction on a grid f times coarser than 0.1 mm"""
    out = {}
    for k in LAYERS:
        a = (D[k] > 0).astype(float); ny, nx = a.shape; ny2, nx2 = ny // f, nx // f
        out[k] = a[:ny2 * f, :nx2 * f].reshape(ny2, f, nx2, f).mean(axis=(1, 3))
    return out

def netmask(net, f):
    v = NETS[net]; out = {}
    for k in LAYERS:
        a = (D[k] == v).astype(float); ny, nx = a.shape; ny2, nx2 = ny // f, nx // f
        out[k] = a[:ny2 * f, :nx2 * f].reshape(ny2, f, nx2, f).mean(axis=(1, 3))
    return out

def cells(bb, res, shape):
    x0, y0, x1, y1 = bb
    i0, i1 = max(int(y0 / res), 0), min(int(np.ceil(y1 / res)), shape[0])
    j0, j1 = max(int(x0 / res), 0), min(int(np.ceil(x1 / res)), shape[1])
    return slice(i0, i1), slice(j0, j1)
