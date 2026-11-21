"""Extract steady-state metrics and loss breakdown from the LTspice runs -> results.json"""
import raw, numpy as np, json, os, sys
FSW = 94.3e3
def get(d, n):
    for k in d:
        if k.lower() == n.lower(): return d[k]
    raise KeyError(n)

def steady(name, vin, rl, t0=12e-3, t1=14e-3):
    d = raw.read(name + '.raw'); t = d['t']; g = lambda n: get(d, n)
    A = lambda y: raw.avg(t, y, t0, t1); R = lambda y: raw.rms(t, y, t0, t1)
    m = (t >= t0) & (t <= t1)
    vout = g('V(out)'); iload = g('I(Rload)'); il = g('I(L1)')
    o = {}
    o['VIN'] = vin; o['RL'] = rl
    o['Vout'] = A(vout); o['Iout'] = A(iload); o['Pout'] = A(vout * iload)
    # Ripple: average over cycles of p-p (last 1 ms)
    m2 = (t >= t1 - 1e-3) & (t <= t1)
    o['Vout_pp'] = vout[m2].max() - vout[m2].min()
    o['IL_pp'] = il[m2].max() - il[m2].min(); o['IL_avg'] = A(il); o['IL_rms'] = R(il); o['IL_pk'] = il[m].max()
    # board input power at UNPROTECTED (after the lab-supply source resistance)
    iin = -g('I(V1)')
    o['Pin_src'] = A(g('V(source)') * iin); o['Pin'] = A(g('V(unprotected)') * g('I(Rsource)'))
    o['Iin'] = A(g('I(Rsource)')); o['Iin_rms'] = R(g('I(Rsource)'))
    o['eff'] = o['Pout'] / o['Pin']
    P = {}
    P['Q1'] = A((g('V(qd)') - g('V(sw)')) * g('Id(MQ1)'))
    P['Q2'] = A(g('V(sw)') * g('Id(MQ2)'))
    P['Q3'] = A((g('V(cable)') - g('V(unprotected)')) * g('Id(MQ3)'))
    P['L1_dcr'] = o['IL_rms'] ** 2 * 0.020
    # XAL1510-333 core loss estimate (Coilcraft model scaling, 94 kHz): k * dI^2.2  calibrated ~0.12 W at 2 A p-p
    P['L1_core'] = 0.12 * (o['IL_pp'] / 2.0) ** 2.2
    P['RS1'] = R(g('I(RS1)')) ** 2 * 4e-3
    P['CIN'] = R(g('I(CINcer)')) ** 2 * 3e-3 + R(g('I(CINbulk)')) ** 2 * 28e-3
    P['COUT'] = R(g('I(COUT)')) ** 2 * 10e-3
    P['RSN1'] = 1e-9 * vin ** 2 * FSW
    model_parasitic = o['IL_rms'] ** 2 * 3e-3 + R(g('Id(MQ1)')) ** 2 * 2e-3     # Rtrace + Lloop Rser (board copper)
    P['PCB_Cu'] = model_parasitic
    known = sum(P.values()) - P['L1_core']
    P['U1_drv_misc'] = max(o['Pin'] - o['Pout'] - known, 0.0)          # gate drive, IC, Rg, residual
    o['loss'] = P; o['Ptot_model'] = o['Pin'] - o['Pout']
    o['Ptot_with_core'] = o['Ptot_model'] + P['L1_core']
    o['eff_with_core'] = o['Pout'] / (o['Pout'] + o['Ptot_with_core'])
    o['ITH'] = A(g('V(ith)')); o['Vin_pp'] = g('V(in)')[m2].max() - g('V(in)')[m2].min()
    o['D'] = A((g('V(sw)') > vin / 2).astype(float))
    return o

if __name__ == '__main__':
    runs = {'s20': (20, 2.4), 's24': (24, 2.4), 's36': (36, 2.4), 's48': (48, 2.4), 'h24': (24, 1.6), 'h48': (48, 1.6),
            'l24_30': (24, 4.8), 'l24_15': (24, 9.6), 'l24_6': (24, 24), 'l48_30': (48, 4.8), 'l48_15': (48, 9.6), 'l48_6': (48, 24)}
    res = {}
    for n, (v, rl) in runs.items():
        if not os.path.exists(n + '.raw'): print('missing', n); continue
        try: res[n] = steady(n, v, rl); r = res[n]
        except Exception as e: print(n, 'ERR', e); continue
        print(f"{n:7s} Vout={r['Vout']:.4f} Pout={r['Pout']:.2f} Pin={r['Pin']:.2f} eff={100*r['eff']:.2f}% ripple={1e3*r['Vout_pp']:.1f}mV "
              f"ILpp={r['IL_pp']:.2f} D={r['D']:.3f} " + ' '.join(f"{k}={v:.3f}" for k, v in r['loss'].items()))
    json.dump(res, open('results.json', 'w'), indent=1)
