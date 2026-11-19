"""Minimal LTspice binary .raw reader + steady-state measurements for RevD5E1 runs.
Usage: python ltraw_measure.py <file.raw> [t0_ms] [t1_ms]
Measures in window [t0,t1] (default 12-14 ms), trapezoidal time averages.
"""
import sys, re, numpy as np

def read_raw(path):
    with open(path, 'rb') as f:
        data = f.read()
    key = 'Binary:\n'.encode('utf-16-le')
    i = data.index(key)
    hdr = data[:i].decode('utf-16-le')
    body = data[i + len(key):]
    nvar = int(re.search(r'No\. Variables:\s*(\d+)', hdr).group(1))
    npt = int(re.search(r'No\. Points:\s*(\d+)', hdr).group(1))
    names = re.findall(r'^\t\d+\t(\S+)\t', hdr, re.M)
    dt = np.dtype([('time', '<f8')] + [(n, '<f4') for n in names[1:]])
    arr = np.frombuffer(body, dtype=dt, count=npt)
    out = {'time': np.abs(arr['time'])}
    for n in names[1:]:
        out[n] = arr[n].astype(np.float64)
    return out

def avg(t, y):
    return np.trapezoid(y, t) / (t[-1] - t[0])

def rms(t, y):
    return np.sqrt(avg(t, y * y))

def measure(path, t0=12e-3, t1=14e-3):
    d = read_raw(path)
    t = d['time']; m = (t >= t0) & (t <= t1)
    tt = t[m]; g = lambda k: d[k][m]
    vout = g('V(out)')
    r = {}
    r['Vout_avg_V'] = avg(tt, vout)
    r['Vout_ripple_mVpp'] = (vout.max() - vout.min()) * 1e3
    r['Iout_avg_A'] = avg(tt, g('I(Rload)'))
    r['Pout_W'] = avg(tt, vout * g('I(Rload)'))
    iin = -g('I(V1)')
    r['Pin_connector_W'] = avg(tt, g('V(unprotected)') * iin)
    r['Pin_source_W'] = avg(tt, g('V(source)') * iin)
    r['eff_connector_pct'] = 100 * r['Pout_W'] / r['Pin_connector_W']
    r['IL_peak_A'] = g('I(L1)').max(); r['IL_rms_A'] = rms(tt, g('I(L1)'))
    sw = g('V(sw)'); vin = g('V(in)')
    r['VDSH_max_V'] = (g('V(qd)') - sw).max(); r['VDSL_max_V'] = sw.max()
    r['PQH_W'] = avg(tt, (g('V(qd)') - sw) * g('Id(MQ1)'))
    r['PQL_W'] = avg(tt, sw * g('Id(MQ2)'))
    r['Prev_W'] = avg(tt, (g('V(unprotected)') - g('V(cable)')) * (g('I(DrevA)') + g('I(DrevB)')))
    # switching frequency: rising crossings of SW through Vin/2
    thr = vin.mean() / 2
    up = np.where((sw[:-1] < thr) & (sw[1:] >= thr))[0]
    tc = tt[up] + (thr - sw[up]) / (sw[up + 1] - sw[up]) * (tt[up + 1] - tt[up])
    per = np.diff(tc)
    r['fsw_kHz_mean'] = 1e-3 / per.mean(); r['fsw_kHz_min'] = 1e-3 / per.max(); r['fsw_kHz_max'] = 1e-3 / per.min()
    r['n_cycles'] = len(per)
    r['duty_mean'] = None
    r['V_ITH_avg'] = avg(tt, g('V(n008)')); r['V_CS_avg'] = avg(tt, g('V(cs)'))
    r['V_ILIMREF'] = avg(tt, g('V(ilimref)')); r['V_CCOUT_avg'] = avg(tt, g('V(ccout)'))
    r['I_Dclamp_avg_uA'] = avg(tt, g('I(Dclamp)')) * 1e6
    return r

if __name__ == '__main__':
    p = sys.argv[1]
    t0 = float(sys.argv[2]) * 1e-3 if len(sys.argv) > 2 else 12e-3
    t1 = float(sys.argv[3]) * 1e-3 if len(sys.argv) > 3 else 14e-3
    for k, v in measure(p, t0, t1).items():
        print(f'{k:22s} {v}')
