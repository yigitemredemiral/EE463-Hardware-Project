"""All numbers used in the LaTeX report -> OUT/values.tex as \val{key} macros."""
import json, os, numpy as np, raw
OUT = os.environ['OUT']; V = {}
R = json.load(open('results.json')); C = json.load(open(os.path.join(OUT, 'circuit.json')))
TH = json.load(open(os.path.join(OUT, 'thermal.json'))); FRA = json.load(open(os.path.join(OUT, 'fra.json')))
CK = {m: json.load(open(os.path.join(OUT, 'checker', f'check{m}.json'), encoding='utf-8')) for m in ('', '_overload')}
def put(k, v, n=2): V[k] = f'{v:.{n}f}' if isinstance(v, float) else str(v)
for k, r in R.items():
    put(f'{k}.vout', r['Vout'], 3); put(f'{k}.pout', r['Pout'], 1); put(f'{k}.pin', r['Pin'], 2)
    put(f'{k}.eff', 100 * r['eff_with_core'], 2); put(f'{k}.effnc', 100 * r['eff'], 2)
    put(f'{k}.ilpp', r['IL_pp'], 2); put(f'{k}.ilpk', r['IL_pk'], 2); put(f'{k}.d', r['D'], 3)
    put(f'{k}.ptot', r['Ptot_with_core'], 2); put(f'{k}.vinpp', 1e3 * r['Vin_pp'], 0)
    for q, w in r['loss'].items(): put(f'{k}.loss.{q}', w, 3)
for k in ('s20', 's24', 's36', 's48', 'h24', 'h48'):
    d = raw.read(k + '.raw', ['t', 'V(out)', 'V(sw)']); t = d['t']; m = t >= t[-1] - 5 / 94.3e3
    put(f'{k}.rip', 1e3 * float(np.ptp(d['V(out)'][m])), 1); put(f'{k}.swpk', float(d['V(sw)'][m].max()), 1)
put('eff.avg', 100 * np.mean([R[k]['eff_with_core'] for k in ('s20', 's24', 's36', 's48')]), 2)
for k in ('start24', 'start48'):
    for q, w in C[k].items(): put(f'{k}.{q}', w * (1e3 if q == 'Vout_over' else 1), 1 if q != 'Vout_over' else 0)
put('ls.under', 1e3 * C['loadstep_up']['undershoot'], 0); put('ls.over', 1e3 * C['loadstep_down']['overshoot'], 0)
put('ls.settle', 1e3 * max(C['loadstep_up']['settle_1pct_ms'], C['loadstep_down']['settle_1pct_ms']) / 1e3, 2)
put('line.up', 1e3 * C['linestep']['dev_up'], 0); put('line.down', 1e3 * C['linestep']['dev_down'], 0)
put('fault.iout', C['fault']['Iout_avg'], 2); put('fault.ilpk', C['fault']['IL_pk'], 1); put('fault.vout', C['fault']['Vout_avg'], 2)
put('fault.rec', 1e3 * C['fault']['Vout_over_recovery'], 0)
for v, o in FRA.items(): put(f'fra{v}.fc', o['fc_Hz'] / 1e3, 2); put(f'fra{v}.pm', o['PM_deg'], 0)
for k, o in TH.items():
    if k == 'ir':
        for n, q in o.items():
            n = n.strip('/').lower(); put(f'ir.{n}.r', q['R_mohm'], 2); put(f'ir.{n}.p', q['P_mW'], 0); put(f'ir.{n}.j', q['Jmax'], 2); put(f'ir.{n}.dv', q['dV_mV'], 1)
        continue
    put(f'th.{k}.ptot', o['Ptot'], 2); put(f'th.{k}.board300', 25 + o['board_avg300'], 1); put(f'th.{k}.boardss', 25 + o['board_avg_ss'], 1)
    for c, w in o['rise300'].items(): put(f'th.{k}.{c}.t300', 25 + w, 1); put(f'th.{k}.{c}.ss40', 40 + o['rise_ss'][c], 1)
    for c, w in o['loss'].items(): put(f'th.{k}.{c}.p', w, 2)
for m, ck in CK.items():
    for s, n in ck['counts'].items(): put(f'chk{m}.{s}', n)
with open(os.path.join(OUT, 'values.tex'), 'w', encoding='utf-8') as f:
    for k, v in sorted(V.items()): f.write('\\expandafter\\def\\csname v@' + k + '\\endcsname{' + v + '}\n')
print(len(V), 'values')
