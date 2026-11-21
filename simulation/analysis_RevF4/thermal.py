"""4-layer PCB transient thermal model (finite volume, 0.5 mm cells, implicit Euler).
Layers F/In1/In2/B with real copper coverage from KiCad, FR4 between them, via barrels, convection+radiation on
both faces, lumped body nodes for tall parts. Linear in losses -> temperature rise above ambient."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
import pcbmodel as pm
F = 5; DX = pm.RES0 * F * 1e-3                       # 0.5 mm cells
COV = pm.coverage(F); NY, NX = COV['F'].shape; N1 = NX * NY
K_CU, K_FR4_XY, K_FR4_Z = 390.0, 0.8, 0.3
T_CU = 35e-6
DIE = [0.2e-3, 1.06e-3, 0.2e-3]                      # F-In1, In1-In2, In2-B
FR4_SHARE = [DIE[0] / 2, DIE[0] / 2 + DIE[1] / 2, DIE[1] / 2 + DIE[2] / 2, DIE[2] / 2]
RHOC_CU, RHOC_FR4 = 3.45e6, 1.85e6
H_TOP, H_BOT = 14.0, 10.0                             # W/m2K natural convection + radiation (linearised, ~50 C)
VIA_A = np.pi * 0.3e-3 * 25e-6                        # 0.3 mm drill, 25 um plating
# lumped bodies: ref -> (heat capacity J/K, exposed area m2, body-to-pads K/W)
BODY = {'L1': (4.6, 885e-6, 8.0), 'CINB1': (2.0, 409e-6, 40.0), 'CINB2': (2.0, 409e-6, 40.0), 'CINB3': (2.0, 409e-6, 40.0),
        'COUT1': (2.5, 500e-6, 30.0), 'COUT2': (2.5, 500e-6, 30.0), 'J1': (3.0, 600e-6, 20.0), 'J2': (3.0, 600e-6, 20.0)}
H_BODY = 14.0
RTH_JC = {'Q1': 1.2, 'Q2': 0.9, 'Q3': 0.9, 'U1': 3.0, 'U5': 20.0, 'RS1': 5.0}

def idx(l, i, j): return l * N1 + i * NX + j

def build():
    rows, cols, vals = [], [], []
    def add(a, b, g):
        rows.extend([a, b, a, b]); cols.extend([a, b, b, a]); vals.extend([g, g, -g, -g])
    C = np.zeros(4 * N1)
    I, J = np.mgrid[0:NY, 0:NX]
    for l, k in enumerate(pm.LAYERS):
        c = COV[k]; gs = K_CU * T_CU * c + K_FR4_XY * FR4_SHARE[l]          # sheet conductance W/K (square cells)
        # x-neighbours
        g = 2 * gs[:, :-1] * gs[:, 1:] / (gs[:, :-1] + gs[:, 1:])
        a = (l * N1 + I[:, :-1] * NX + J[:, :-1]).ravel(); b = a + 1
        rows += list(np.r_[a, b, a, b]); cols += list(np.r_[a, b, b, a]); gg = g.ravel(); vals += list(np.r_[gg, gg, -gg, -gg])
        g = 2 * gs[:-1, :] * gs[1:, :] / (gs[:-1, :] + gs[1:, :])
        a = (l * N1 + I[:-1, :] * NX + J[:-1, :]).ravel(); b = a + NX
        rows += list(np.r_[a, b, a, b]); cols += list(np.r_[a, b, b, a]); gg = g.ravel(); vals += list(np.r_[gg, gg, -gg, -gg])
        C[l * N1:(l + 1) * N1] = (RHOC_CU * T_CU * c + RHOC_FR4 * FR4_SHARE[l]).ravel() * DX * DX
    # vertical
    nvia = np.zeros((NY, NX))
    for x, y, net, drill in pm.M['vias']:
        i, j = min(int(y / (DX * 1e3)), NY - 1), min(int(x / (DX * 1e3)), NX - 1); nvia[i, j] += 1
    for l in range(3):
        g = (K_FR4_Z * DX * DX / DIE[l] + nvia * K_CU * VIA_A / DIE[l]).ravel()
        a = l * N1 + np.arange(N1); b = a + N1
        rows += list(np.r_[a, b, a, b]); cols += list(np.r_[a, b, b, a]); vals += list(np.r_[g, g, -g, -g])
    # convection to ambient (node 'ground' = reference 0)
    gconv = np.zeros(4 * N1); gconv[:N1] = H_TOP * DX * DX; gconv[3 * N1:] = H_BOT * DX * DX
    nb = len(BODY); n = 4 * N1 + nb
    Cb = np.zeros(n); Cb[:4 * N1] = C; gb = np.zeros(n); gb[:4 * N1] = gconv
    bodyidx = {}
    for m, (ref, (cap, area, rbp)) in enumerate(BODY.items()):
        bi = 4 * N1 + m; bodyidx[ref] = bi; Cb[bi] = cap; gb[bi] = H_BODY * area
        fp = pm.FPS[ref]; cl = []
        for p in fp['pads']:
            si, sj = pm.cells(p['bb'], DX * 1e3, (NY, NX)); cl += [i * NX + j for i in range(si.start, si.stop) for j in range(sj.start, sj.stop)]
        cl = sorted(set(cl)); g = 1.0 / rbp / len(cl)
        for c0 in cl: add(bi, c0, g)
        # body covers the board under it: remove top convection there
        si, sj = pm.cells(fp['bb'], DX * 1e3, (NY, NX))
        for i in range(si.start, si.stop):
            for j in range(sj.start, sj.stop): gb[i * NX + j] = 0.3 * H_TOP * DX * DX
    G = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr() + sp.diags(gb)
    return G, Cb, gb, bodyidx

G, CAP, GAMB, BIDX = build()
NN = G.shape[0]

def srcvec(loss):
    """loss: ref -> W. MOSFET/IC/resistor heat into F-layer cells under its pads; bodies into body node."""
    q = np.zeros(NN)
    for ref, P in loss.items():
        if P <= 0: continue
        if ref in BIDX: q[BIDX[ref]] += P; continue
        fp = pm.FPS[ref]; cl = []
        pads = fp['pads']
        if ref.startswith('Q'):   # exposed drain tab = largest pad
            pads = [max(pads, key=lambda p: (p['bb'][2] - p['bb'][0]) * (p['bb'][3] - p['bb'][1]))]
        for p in pads:
            si, sj = pm.cells(p['bb'], DX * 1e3, (NY, NX)); cl += [i * NX + j for i in range(si.start, si.stop) for j in range(sj.start, sj.stop)]
        cl = sorted(set(cl)); q[cl] += P / len(cl)
    return q

def comp_temp(T, ref):
    if ref in BIDX: return T[BIDX[ref]]
    fp = pm.FPS[ref]; si, sj = pm.cells(fp['bb'], DX * 1e3, (NY, NX))
    return T[:N1].reshape(NY, NX)[si, sj].max()

def steady(loss):
    return sla.spsolve(G.tocsc(), srcvec(loss))

def transient(loss, t_end=300.0, rec=None):
    q = srcvec(loss); T = np.zeros(NN); t = 0.0; out_t = [0.0]; out_T = [T.copy()]
    dts = [(10, 0.05), (60, 0.5), (1e9, 2.0)]
    solvers = {}
    while t < t_end - 1e-9:
        dt = next(d for lim, d in dts if t < lim); dt = min(dt, t_end - t)
        if dt not in solvers: solvers[dt] = sla.factorized((sp.diags(CAP / dt) + G).tocsc())
        T = solvers[dt](CAP / dt * T + q); t += dt
        out_t.append(t); out_T.append(T if rec is None else None)
        if rec is not None: rec(t, T)
    return np.array(out_t), T

def tau_estimate():
    return CAP.sum() / GAMB.sum(), GAMB.sum()
