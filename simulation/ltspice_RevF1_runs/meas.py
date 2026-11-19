"""Measurements for RevF1 runs -> results.json (merged). Usage: python meas.py kind name [name...]
kinds: ss (steady state 12-14 ms), fault (TEST=1: event 7-10 ms, recovery after 10 ms), startup"""
import os, sys, json, numpy as np
ALIAS = {'Id(MQ1)': 'I(VaQ1)', 'Id(MQ2)': 'I(VaQ2)'}
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ltraw_measure import read_raw, avg, rms

def edges_fsw(t, sw, vin):
    hi, lo = .7 * vin, .3 * vin; st = sw[0] > hi; e = []
    for i in np.flatnonzero((sw[1:] > hi) & (sw[:-1] <= hi)):
        e.append(t[i + 1])
    e = np.array(e)
    # hysteresis filter: keep edges separated by a dip below lo
    keep = [e[0]] if len(e) else []
    for x in e[1:]:
        m = (t > keep[-1]) & (t < x)
        if (sw[m] < lo).any(): keep.append(x)
    p = np.diff(keep); return 1e-3 / p.mean() if len(p) else float('nan')

def ird(d, m):
    if 'I(VaRP)' in d: return -d['I(VaRP)'][m]
    for k in ('Id(MRP)', 'I(MRP)', 'Is(MRP)'):
        if k in d: return -d[k][m] if k.startswith('Id') else d[k][m]
    raise KeyError('MRP current not saved')

def ss(d, t0=12e-3, t1=14e-3):
    t = d['time']; m = (t >= t0) & (t <= t1); tt = t[m]; g = lambda k: d[k][m]
    vout = g('V(out)'); iin = -g('I(V1)'); sw = g('V(sw)'); qd = g('V(qd)')
    r = dict(Vout=avg(tt, vout), ripple_mVpp=(vout.max() - vout.min()) * 1e3, Iout=avg(tt, g('I(Rload)')),
             Pout=avg(tt, vout * g('I(Rload)')), Pin_conn=avg(tt, g('V(unprotected)') * iin),
             IL_pk=g('I(L1)').max(), IL_rms=rms(tt, g('I(L1)')),
             VDSH_max=(qd - sw).max(), VDSL_max=sw.max(),
             PQ1=avg(tt, (qd - sw) * g('Id(MQ1)')), PQ2=avg(tt, sw * g('Id(MQ2)')),
             Prev=avg(tt, (g('V(unprotected)') - g('V(cable)')) * (g('I(DrevA)') + g('I(DrevB)'))) if 'I(DrevA)' in d else
                  avg(tt, (g('V(unprotected)') - g('V(cable)')) * ird(d, m)),
             CCOUT=avg(tt, g('V(ccout)')), ITH=avg(tt, g('V(n008)')),
             Vout_1st_half=avg(tt[:len(tt)//2], vout[:len(tt)//2]))
    r['eff_conn'] = 100 * r['Pout'] / r['Pin_conn']
    r['fsw_kHz'] = edges_fsw(tt, sw, g('V(in)').mean())
    return r

def fault(d, tev=10e-3, tstart=7e-3):
    t = d['time']; g = lambda k, m: d[k][m]
    allm = t > 0.2e-3
    ev = (t >= tev - 1e-3) & (t <= tev); rec = t > tev; pre = (t >= tstart - 1e-3) & (t <= tstart)
    vout = d['V(out)']
    r = dict(VDSH_max_all=(d['V(qd)'] - d['V(sw)'])[allm].max(), VDSL_max_all=d['V(sw)'][allm].max(),
             Iout_fault=avg(t[ev], d['I(Rload)'][ev]), Vout_fault=avg(t[ev], vout[ev]),
             IL_pk_all=d['I(L1)'][allm].max(), Vout_pre=avg(t[pre], vout[pre]),
             Vout_rec_peak=vout[rec].max(), Vout_end=avg(t[t > t[-1] - 0.5e-3], vout[t > t[-1] - 0.5e-3]),
             IQ1_pk=d['Id(MQ1)'][allm].max())
    # recovery time into +-2% band permanently
    tr = t[rec]; vr = vout[rec]; bad = np.flatnonzero(np.abs(vr - 12) > 0.24)
    r['t_rec_2pct_ms'] = (tr[bad[-1]] - tev) * 1e3 if len(bad) else 0.0
    return r

if __name__ == '__main__':
    kind = sys.argv[1]; db = os.path.join(HERE, 'results.json')
    res = json.load(open(db)) if os.path.exists(db) else {}
    for n in sys.argv[2:]:
        try:
            d = read_raw(os.path.join(HERE, n + '.raw'))
            for a, b in ALIAS.items():
                if a not in d and b in d: d[a] = d[b]
            if kind == 'ss': r = ss(d)
            elif kind == 'sslast': r = ss(d, d['time'][-1] - 2e-3, d['time'][-1])
            elif kind.startswith('ss@'):   # ss@<t0_ms>@<t1_ms>
                a, b = kind.split('@')[1:]; r = ss(d, float(a) * 1e-3, float(b) * 1e-3)
            elif kind.startswith('fault@'):   # fault@<start_ms>@<end_ms>
                a, b = kind.split('@')[1:]; r = fault(d, float(b) * 1e-3, float(a) * 1e-3)
            else: r = fault(d, 13e-3 if kind == 'fault13' else 10e-3)
            res[n] = dict(kind=kind, **r)
            print(n, {k: round(v, 4) if isinstance(v, float) else v for k, v in res[n].items()}, flush=True)
        except Exception as e:
            res[n] = dict(kind=kind, error=str(e)); print(n, 'ERROR', e)
    json.dump(res, open(db, 'w'), indent=1)
