"""Paket 3 - compensation A/B: FRA vs hand model, load/line step metrics, figures.
Run after gen_p3.py: python analyse_p3.py  -> figures in docs/paket3_assets/, numbers in p3_results.json"""
import os, sys, json, glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ltspice_RevF1_runs'))
from ltraw_measure import read_raw
from fra import read_complex_raw
import comp_model as cm
OUT = os.path.join(HERE, '..', '..', 'reports', 'figures'); os.makedirs(OUT, exist_ok=True)
COL = {'A': '#1f77b4', 'B': '#d62728'}
LBL = {'A': 'A: 8.2 k / 27 nF / 470 pF', 'B': 'B: 3.9 k / 68 nF / 1 nF'}
FSW = 94.3e3
res = {}

# ---------------------------------------------------------------- FRA
def fra_file(name):
    for pat in (name + '.fra.raw', name + '.fra', name + '*.fra*'):
        g = glob.glob(os.path.join(HERE, pat))
        if g: return g[0]
    raise FileNotFoundError(name)

def fra(name):
    _, d = read_complex_raw(fra_file(name))
    f = np.abs(d['frequency'].real); k = [x for x in d if x.lower() != 'frequency'][0]
    T = d[k]; o = np.argsort(f); f, T = f[o], T[o]
    # LTspice .fra phase convention: displayed phase = 180 deg + angle(loop), i.e. the stored quantity is -T
    return f, -T

def margins(f, T):
    mag = 20*np.log10(abs(T)); ph = np.degrees(np.unwrap(np.angle(T))) + 180
    ph -= 360*np.round((ph[0] - 90)/360)
    lf = np.log10(f); r = {}
    k = np.flatnonzero((mag[:-1] > 0) & (mag[1:] <= 0))
    if len(k):
        k = k[0]; x = mag[k]/(mag[k] - mag[k+1])
        r['fc_Hz'] = float(10**(lf[k] + x*(lf[k+1] - lf[k]))); r['PM_deg'] = float(ph[k] + x*(ph[k+1] - ph[k]))
        j = [m for m in range(k, len(f) - 1) if ph[m] > 0 >= ph[m+1]]
        if j:
            m = j[0]; y = ph[m]/(ph[m] - ph[m+1]); r['GM_dB'] = float(-(mag[m] + y*(mag[m+1] - mag[m])))
            r['f180_Hz'] = float(10**(lf[m] + y*(lf[m+1] - lf[m])))
        else:
            r['GM_dB_lower_bound'] = float(-mag[-1]); r['f_max_Hz'] = float(f[-1])
    return r, mag, ph

def fit(vin):
    """Calibrate Gi and Q of the hand model on the FRA of compensation A only (points up to 12 kHz)."""
    f, T = fra(f'P3_A_fra_{vin}V'); m = f <= 12e3
    best = None
    for Gi in np.arange(8, 30, 0.1):
        for Q in np.arange(0.2, 2.01, 0.05):
            M = cm.loop(f[m], 'A', Gi=Gi, Q=Q, fsw=FSW)
            e = np.sum(np.abs(np.log(M/T[m]))**2)
            if best is None or e < best[0]: best = (e, Gi, Q)
    return dict(Gi=float(round(best[1], 2)), Q=float(round(best[2], 2)))

# one calibration (48 V, compensation A) is used for every curve; B and the 20 V curves are predictions
PFIT = fit(48); res['model_fit'] = PFIT
fig, ax = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True)
fm = np.logspace(np.log10(100), np.log10(40e3), 600)
for col, vin in enumerate((20, 48)):
    p = PFIT
    for c in 'AB':
        f, T = fra(f'P3_{c}_fra_{vin}V'); r, mag, ph = margins(f, T); res[f'fra_{c}_{vin}V'] = r
        Tm = cm.loop(fm, c, fsw=FSW, **p); rm, magm, phm = margins(fm, Tm); res[f'model_{c}_{vin}V'] = rm
        ax[0, col].semilogx(fm, magm, color=COL[c], label=LBL[c] + ' (hand model)')
        ax[0, col].semilogx(f, mag, 'o', color=COL[c], ms=4, label=c + ' (LTspice FRA)')
        ax[1, col].semilogx(fm, phm, color=COL[c]); ax[1, col].semilogx(f, ph, 'o', color=COL[c], ms=4)
    ax[0, col].set_title(f'Loop gain, VIN = {vin} V, 60 W (2.4 $\\Omega$)'); ax[0, col].axhline(0, color='k', lw=0.6)
    ax[1, col].axhline(0, color='k', lw=0.6); ax[1, col].set_xlabel('Frequency (Hz)')
    ax[0, col].set_ylim(-40, 50); ax[1, col].set_ylim(-30, 120)
    for a in ax[:, col]: a.grid(True, which='both', alpha=0.3)
ax[0, 0].set_ylabel('|T| (dB)'); ax[1, 0].set_ylabel('Phase + 180° (deg)'); ax[0, 1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'bode_A_vs_B.png'), dpi=160); plt.close(fig)

# ---------------------------------------------------------------- steps
def smooth(t, y, T=1/FSW):
    """Moving average over one switching period on a uniform grid (removes switching ripple)."""
    dt = 0.5e-6; tu = np.arange(t[0], t[-1], dt); yu = np.interp(tu, t, y)
    n = max(1, int(round(T/dt))); k = np.ones(n)/n
    return tu[n:-n], np.convolve(yu, k, mode='same')[n:-n]

def step_metrics(tu, v, t_ev, t_end, band=0.060):
    m = (tu >= t_ev) & (tu < t_end); tt, vv = tu[m], v[m]
    vfin = vv[tt > tt[-1] - 0.5e-3].mean(); dev = vv - vfin
    i = np.argmax(abs(dev)); outside = np.flatnonzero(abs(dev) > band)
    ts = (tt[outside[-1]] - t_ev) if len(outside) else 0.0
    # opposite-sign excursion after the main peak = overshoot of the recovery
    back = dev[i:]*(-np.sign(dev[i]))
    return dict(peak_dev_mV=float(dev[i]*1e3), t_peak_us=float((tt[i] - t_ev)*1e6),
                settle_60mV_ms=float(ts*1e3), recovery_overshoot_mV=float(max(back.max(), 0)*1e3), v_final=float(vfin))

def step_fig(kind, cases, events, fname, extra):
    fig, ax = plt.subplots(3, len(cases), figsize=(5.5*len(cases), 7), sharex=True, squeeze=False)
    for col, (vin, title) in enumerate(cases):
        for c in 'AB':
            d = read_raw(os.path.join(HERE, f'P3_{c}_{kind}_{vin}V.raw')); t = d['time']
            tu, v = smooth(t, d['V(out)']); _, il = smooth(t, d['I(L1)']); _, x = smooth(t, d[extra[0]])
            ax[0, col].set_xlim(8.5, tu[-1]*1e3); ax[0, col].plot(tu*1e3, v, color=COL[c], label=LBL[c]); ax[1, col].plot(tu*1e3, il, color=COL[c])
            ax[2, col].plot(tu*1e3, x, color=COL[c])
            for ev, (t0, t1) in events.items():
                res[f'{kind}_{c}_{vin}V_{ev}'] = step_metrics(tu, v, t0, t1)
            m = t > t[-1] - 0.3e-3
            res[f'{kind}_{c}_{vin}V_ripple_mVpp'] = float((d['V(out)'][m].max() - d['V(out)'][m].min())*1e3)
        ax[0, col].set_title(title); ax[2, col].set_xlabel('Time (ms)')
        for y in (11.76, 12.24): ax[0, col].axhline(y, color='gray', ls='--', lw=0.7)
        for a in ax[:, col]: a.grid(True, alpha=0.3)
    ax[0, 0].set_ylabel('VOUT (V), cycle-averaged'); ax[1, 0].set_ylabel('Inductor current (A)'); ax[2, 0].set_ylabel(extra[1])
    ax[0, 0].legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(OUT, fname), dpi=160); plt.close(fig)

step_fig('load', [(20, 'Load step 5 A -> 2.5 A -> 5 A, VIN = 20 V'), (48, 'Load step 5 A -> 2.5 A -> 5 A, VIN = 48 V')],
         {'unload': (9e-3, 13e-3), 'load': (13e-3, 17e-3)}, 'load_step_A_vs_B.png', ('I(Rload)', 'Load current (A)'))
step_fig('line', [(20, 'Line step 20 V -> 30 V -> 20 V, 60 W')],
         {'rise': (9e-3, 13e-3), 'fall': (13e-3, 18e-3)}, 'line_step_A_vs_B.png', ('V(in)', 'VIN at converter (V)'))
json.dump(res, open(os.path.join(HERE, 'p3_results.json'), 'w'), indent=1)
for k, v in res.items(): print(k, json.dumps(v))
