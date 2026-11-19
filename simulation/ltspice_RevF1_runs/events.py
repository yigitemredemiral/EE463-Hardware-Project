"""Startup / reverse-polarity analysis. Usage: python events.py startup|reverse name..."""
import sys, os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ltraw_measure import read_raw, avg
def mrp_i(d):
    for k in ('Id(MRP)', 'I(MRP)'):
        if k in d: return d[k]
    return None
def startup(d):
    t = d['time']; vo = d['V(out)']; iin = -d['I(V1)']; vs = d['V(source)']
    r = {'t_end_ms': t[-1] * 1e3, 'Iin_max_A': float(iin.max()), 'Vsource_min_after_2ms': float(vs[t > 2.5e-3].min()),
         'Vsource_end': float(vs[-1]), 'Vout_max': float(vo.max()),
         'Vout_end_avg': float(avg(t[t > t[-1] - 1e-3], vo[t > t[-1] - 1e-3]))}
    ok = np.abs(vo - 12) <= 0.24; bad = np.flatnonzero(~ok)
    r['t_settle_2pct_ms'] = float(t[bad[-1]] * 1e3) if len(bad) and bad[-1] < len(t) - 1 else None
    # time spent in supply current limit (Iin within 2% of max) after 2.5 ms
    m = t > 2.5e-3; im = iin[m]; tm = t[m]
    lim = im >= 0.98 * im.max()
    r['t_in_ilim_ms'] = float(np.sum(np.diff(tm)[lim[:-1]]) * 1e3)
    # hiccup detection: RUN pin falling below 1.12 V after first rise
    run = d['V(run)']; up = np.flatnonzero(run > 1.2)
    r['RUN_drops_after_start'] = bool(len(up) and (run[up[0]:] < 1.1).any())
    return r
def reverse(d):
    t = d['time']; ph = (t > 1e-3) & (t < 3e-3)
    r = {'Vsrc_rev': float(d['V(unprotected)'][ph].mean()), 'VIN_min_during_rev': float(d['V(in)'][ph].min()),
         'VIN_max_abs_during_rev': float(np.abs(d['V(in)'][ph]).max()), 'INTVCC_min_rev': float(d['V(intvcc)'][ph].min()),
         'Iin_rev_max_mA': float(np.abs(d['I(V1)'][ph]).max() * 1e3), 'Vout_max_abs_rev': float(np.abs(d['V(out)'][ph]).max())}
    i = mrp_i(d)
    if i is not None: r['I_MRP_rev_max_mA'] = float(np.abs(i[ph]).max() * 1e3)
    vo = d['V(out)']; fw = t > 6e-3; ok = np.abs(vo - 12) <= 0.24; bad = np.flatnonzero(~ok & fw)
    r['t_reach_2pct_after_fwd_ms'] = float((t[bad[-1]] - 6e-3) * 1e3) if len(bad) and bad[-1] < len(t) - 1 else None
    tail = t > t[-1] - 1e-3
    r['Vout_final'] = float(avg(t[tail], vo[tail])); r['Vout_peak_after_fwd'] = float(vo[fw].max())
    if 'V(grp)' in d: r['VGS_MRP_final'] = float((d['V(grp)'] - d['V(unprotected)'])[tail].mean())
    r['Vdrop_MRP_final_mV'] = float((d['V(unprotected)'] - d['V(cable)'])[tail].mean() * 1e3)
    return r
if __name__ == '__main__':
    kind = sys.argv[1]; db = os.path.join(HERE, 'results.json'); res = json.load(open(db))
    for n in sys.argv[2:]:
        d = read_raw(os.path.join(HERE, n + '.raw'))
        res[n] = dict(kind=kind, **(startup(d) if kind == 'startup' else reverse(d)))
        print(n, json.dumps(res[n]))
    json.dump(res, open(db, 'w'), indent=1)
