"""Loop gain from LTspice .fra runs (frbXX.fra_loop.raw) -> OUT/fig/bode.(png|pdf), OUT/fra.json"""
import numpy as np, json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OUT = os.environ.get('OUT', 'out'); FIG = os.path.join(OUT, 'fig')
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3, 'savefig.bbox': 'tight'})
def read(fn):
    d = open(fn, 'rb').read(); k = d.find('Binary:\n'.encode('utf-16-le'))
    h = d[:k].decode('utf-16-le').splitlines(); nv = int([l for l in h if l.startswith('No. Variables')][0].split(':')[1])
    n = int([l for l in h if l.startswith('No. Points')][0].split(':')[1])
    a = np.frombuffer(d[k + 16:], dtype=np.complex128, count=n * nv).reshape(n, nv)
    return a[:, 0].real, a[:, 1]
fig, ax = plt.subplots(2, 1, figsize=(7.2, 5), sharex=True); res = {}
for v in (20, 24, 36, 48):
    f, g = read(f'frb{v}.fra_loop.raw'); o = np.argsort(f); f, g = f[o], g[o]
    db = 20 * np.log10(np.abs(g)); ph = np.degrees(np.angle(g))
    ax[0].semilogx(f, db, 'o-', ms=3, label=f'{v} V'); ax[1].semilogx(f, ph, 'o-', ms=3)
    i = np.flatnonzero((db[:-1] > 0) & (db[1:] <= 0))
    if len(i):
        i = i[0]; x = db[i] / (db[i] - db[i + 1]); fc = np.exp(np.log(f[i]) + x * np.log(f[i + 1] / f[i]))
        p = ph[i] + x * (((ph[i + 1] - ph[i] + 180) % 360) - 180); res[v] = dict(fc_Hz=float(fc), PM_deg=float(p))   # LTspice gain_loop phase reads directly as phase margin
ax[0].axhline(0, c='k', lw=.8); ax[0].set_ylabel('|T| [dB]'); ax[0].legend(fontsize=7)
ax[1].set_ylabel('Phase [°]'); ax[1].set_xlabel('f [Hz]'); ax[1].axhline(0, c='k', lw=.8); ax[1].axvline(94.3e3 / 2, c='gray', ls=':', lw=.8)
for e in ('png', 'pdf'): fig.savefig(os.path.join(FIG, 'bode.' + e))
json.dump(res, open(os.path.join(OUT, 'fra.json'), 'w'), indent=1); print(res)
