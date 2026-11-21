"""DC current-flow (IR drop) solve on the real copper of one net, all 4 layers + vias, 0.2 mm cells."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
import pcbmodel as pm
F = 2; DX = pm.RES0 * F                     # mm
RHO = 1.72e-8 * 1.15                         # copper at ~60 C
T_CU = 35e-6
VIA_R = RHO * 1.6e-3 / (np.pi * 0.3e-3 * 25e-6)

def solve(net, sources, sinks):
    """sources: list of (ref, [padnums] or None, current A); sinks: list of (ref, padnums) held at 0 V."""
    msk = pm.netmask(net, F); NY, NX = msk['F'].shape; N1 = NX * NY
    sig = {k: (msk[k] > 0.5) * (1.0 / RHO * T_CU) for k in pm.LAYERS}          # S per square
    rows, cols, vals = [], [], []
    for l, k in enumerate(pm.LAYERS):
        s = sig[k]
        for (a, b, ga, gb) in [(np.s_[:, :-1], np.s_[:, 1:], s[:, :-1], s[:, 1:]), (np.s_[:-1, :], np.s_[1:, :], s[:-1, :], s[1:, :])]:
            g = np.where((ga > 0) & (gb > 0), 2 * ga * gb / np.maximum(ga + gb, 1e-30), 0)
            I, J = np.nonzero(g)
            ia = l * N1 + np.arange(N1).reshape(NY, NX)[a][I, J]; ib = l * N1 + np.arange(N1).reshape(NY, NX)[b][I, J]; gg = g[I, J]
            rows += list(np.r_[ia, ib, ia, ib]); cols += list(np.r_[ia, ib, ib, ia]); vals += list(np.r_[gg, gg, -gg, -gg])
    v = pm.NETS[net]
    for x, y, vn, d in pm.M['vias']:
        if vn != v: continue
        i, j = min(int(y / DX), NY - 1), min(int(x / DX), NX - 1)
        ls = [l for l, k in enumerate(pm.LAYERS) if sig[k][i, j] > 0]
        for a, b in zip(ls[:-1], ls[1:]):
            g = 1.0 / (VIA_R * (b - a) / 3); ia, ib = a * N1 + i * NX + j, b * N1 + i * NX + j
            rows += [ia, ib, ia, ib]; cols += [ia, ib, ib, ia]; vals += [g, g, -g, -g]
    G = sp.coo_matrix((vals, (rows, cols)), shape=(4 * N1, 4 * N1)).tocsr()
    def padcells(ref, nums):
        fp = pm.FPS[ref]; out = []
        for p in fp['pads']:
            if p['net'] != net or (nums and p['num'] not in nums): continue
            si, sj = pm.cells(p['bb'], DX, (NY, NX))
            for l, k in enumerate(pm.LAYERS):
                for i in range(si.start, si.stop):
                    for j in range(sj.start, sj.stop):
                        if sig[k][i, j] > 0: out.append(l * N1 + i * NX + j)
        return sorted(set(out))
    q = np.zeros(4 * N1)
    for ref, nums, I in sources:
        c = padcells(ref, nums); q[c] += I / len(c)
    fixed = sorted(set(sum([padcells(r, n) for r, n in sinks], [])))
    active = np.flatnonzero(np.asarray(abs(G).sum(axis=1)).ravel() > 0)
    free = np.setdiff1d(active, fixed)
    Vv = np.zeros(4 * N1)
    Vv[free] = sla.spsolve(G[free][:, free].tocsc(), q[free])
    # current density per layer (A per mm width) from cell-centred gradients
    Jm = {}
    for l, k in enumerate(pm.LAYERS):
        V = Vv[l * N1:(l + 1) * N1].reshape(NY, NX); s = sig[k]
        gx = np.zeros_like(V); gy = np.zeros_like(V)
        ok = (s[:, :-1] > 0) & (s[:, 1:] > 0); d = np.where(ok, (V[:, 1:] - V[:, :-1]), 0)
        gx[:, :-1] += d / 2; gx[:, 1:] += d / 2
        ok = (s[:-1, :] > 0) & (s[1:, :] > 0); d = np.where(ok, (V[1:, :] - V[:-1, :]), 0)
        gy[:-1, :] += d / 2; gy[1:, :] += d / 2
        Jm[k] = np.where(s > 0, s * np.hypot(gx, gy) / DX, np.nan)        # A/mm (sheet current density)
    Itot = sum(I for _, _, I in sources)
    srcV = np.mean([Vv[padcells(r, n)].mean() for r, n, _ in sources])
    P = float(Vv @ (G @ Vv))
    return dict(V=Vv, J=Jm, R=srcV / Itot, P=P, I=Itot, shape=(NY, NX), sig=sig)
