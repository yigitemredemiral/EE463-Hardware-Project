"""Dead time / gate overlap per switching edge. Usage: python deadtime.py <t0_ms> <t1_ms> name...
SW rising edge : dt_r = t(Q1 on) - t(Q2 off);  SW falling edge: dt_f = t(Q2 on) - t(Q1 off).
'on/off' = gate-source crossing VTH (3.0 V, datasheet typical VGS(th) of BSC040N08NS5 / BSC026N08NS5).
Measured at the driver pins (TG-SW, BG) and at the MOSFET package gate pins (GH-SW, GL; after RGH/RGL + LgH/LgL).
Negative dead time = overlap (both above VTH). overlap_ns = time per cycle with both gate-source voltages > VTH."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ltraw_measure import read_raw
VTH = 3.0
def cross(t, v, up):
    s = v > VTH; i = np.flatnonzero((~s[:-1] & s[1:]) if up else (s[:-1] & ~s[1:]))
    return t[i] + (VTH - v[i]) * (t[i + 1] - t[i]) / (v[i + 1] - v[i])
def pair(a_off, b_on):   # for each turn-off of a, next turn-on of b
    out = []
    for x in a_off:
        j = np.searchsorted(b_on, x - 300e-9)   # allow overlap up to 300 ns
        if j < len(b_on) and b_on[j] - x < 2e-6: out.append(b_on[j] - x)
    return np.array(out)
def analyse(d, t0, t1):
    t = d['time']; m = (t >= t0) & (t <= t1); t = t[m]; sw = d['V(sw)'][m]; r = {}
    for tag, hs, ls in (('pin', d['V(tg)'][m] - sw, d['V(bg)'][m]), ('gate', d['V(gh)'][m] - sw, d['V(gl)'][m])):
        h_on, h_off, l_on, l_off = cross(t, hs, True), cross(t, hs, False), cross(t, ls, True), cross(t, ls, False)
        dr, df = pair(l_off, h_on), pair(h_off, l_on)
        both = (hs > VTH) & (ls > VTH); ncyc = max(len(h_on), 1)
        r[f'dt_rise_{tag}_ns'] = float(np.median(dr) * 1e9) if len(dr) else None
        r[f'dt_rise_{tag}_min_ns'] = float(dr.min() * 1e9) if len(dr) else None
        r[f'dt_fall_{tag}_ns'] = float(np.median(df) * 1e9) if len(df) else None
        r[f'dt_fall_{tag}_min_ns'] = float(df.min() * 1e9) if len(df) else None
        r[f'overlap_{tag}_ns_per_cycle'] = float(np.sum(np.diff(t)[both[:-1]]) / ncyc * 1e9)
        r[f'VGS_{tag}_Q1_max'] = float(hs.max()); r[f'VGS_{tag}_Q2_max'] = float(ls.max())
    return r
if __name__ == '__main__':
    t0, t1 = float(sys.argv[1]) * 1e-3, float(sys.argv[2]) * 1e-3; db = 'results.json'; res = json.load(open(db))
    for n in sys.argv[3:]:
        d = {k.lower(): v for k, v in read_raw(n + '.raw').items()}; d = {('V(' + k[2:-1] + ')' if k.startswith('v(') else k): v for k, v in d.items()}
        r = analyse(d, t0, t1); res.setdefault(n, {}).update({'dead': r}); print(n, json.dumps({k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()}))
    json.dump(res, open(db, 'w'), indent=1)
