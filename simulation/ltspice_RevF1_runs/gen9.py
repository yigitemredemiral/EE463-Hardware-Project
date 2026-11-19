"""Official-model runs as single cold starts (no prime: the official models run ~12x slower than VDMOS).
Each run: uic, gear, CSS 4.7n (soft start ~0.4 ms; only to shorten these runs), Schottky input (as the original variant
study). Steady state: tstop 3 ms, measure 2.3-3.0 ms (settling checked). Hot 0.5 ohm event: 1.8-2.6 ms (tstop 2.6 ms)
-> VDS peaks / IL peak at the highest current. (.loadstate from a VDMOS prime is rejected: 'state file not compatible'.)
Chf variants model the HF decoupling path: D5E1 netlist value Lser 0.5 nH (already assumes caps at the FETs),
'old' realistic CHF1 path ~3 nH, 'new' CHF1 + CHF2/3 (3x100n) ~1 nH."""
import sys, gen, gen7
FAULT = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '1.8m,RL,1.81m,RFAULT,2.6m,RFAULT,2.61m,RL')]
CHF = {'old': [('Chf QD 0 100n Rser=30m Lser=500p', 'Chf QD 0 100n Rser=30m Lser=3n')],
       'new': [('Chf QD 0 100n Rser=30m Lser=500p', 'Chf QD 0 300n Rser=10m Lser=1n')]}
V = {'b': ('24.3k', '4.7', 'BSC026N08NS5'), 'c': ('24.3k', '4.7', 'BSC040N08NS5'),
     'd': ('24.3k', '3.3', 'BSC040N08NS5'), 'e': ('24.9k', '6.8', 'BSC040N08NS5')}
names = []
def mk(name, var, tstop='3m', **kw):
    o = kw.pop('overrides', {}); o['replace'] = gen7.official(var[2]) + o.get('replace', []); o['CSS'] = '4.7n'; o['gear'] = 1
    gen.make(name, var, extra=gen7.EXTRA, overrides=o, tstop=tstop, state='none', **kw)
    p = name + '.cir'; s = open(p, encoding='latin-1').read(); old = f'.tran 0 {tstop} 0 100n'
    assert s.count(old) == 1; s = s.replace(old, old + ' uic'); open(p, 'w', encoding='latin-1', newline='').write(s)
    names.append(name)
w = sys.argv[1]
if w == '1':
    for vin in (20, 24, 36, 48): mk(f'RevF1_Oe_{vin}V_60W', V['e'], vin=vin)
    mk('RevF1_Oe_48V_90W', V['e'], vin=48, rl=1.6)
    for k in 'edc': mk(f'RevF1_O{k}_fault_48V_hot70_L20n', V[k], tstop='2.6m', vin=48, hot=True, test=1, overrides={'replace': FAULT})
if w == '2':
    for r in ('5.6', '8.2', '10'): mk(f'RevF1_Orgh{r.replace(".", "p")}_48V_90W_27', ('24.9k', r, 'BSC040N08NS5'), vin=48, rl=1.6)
    for r in ('5.6', '6.8', '8.2', '10'): mk(f'RevF1_Orgh{r.replace(".", "p")}_48V_90W_hot70', ('24.9k', r, 'BSC040N08NS5'), vin=48, rl=1.6, hot=True)
    mk('RevF1_Ob_48V_90W', V['b'], vin=48, rl=1.6)
if w == '3':   # HF decoupling path variants at the hot 0.5 ohm event, RGH from argv[2]
    r = sys.argv[2]; v = ('24.9k', r, 'BSC040N08NS5'); tag = r.replace('.', 'p')
    for c in ('old', 'new'):
        mk(f'RevF1_Ochf{c}_rgh{tag}_fault_48V_hot70_L20n', v, tstop='2.6m', vin=48, hot=True, test=1, overrides={'replace': FAULT + CHF[c]})
if w == 'cal':   # method check: same short cold-start recipe with the original VDMOS models (compare with prime-based (e))
    import gen as _g
    for nm, kw in (('RevF1_Ve_48V_60W_short', dict(vin=48)), ('RevF1_Ve_48V_90W_short', dict(vin=48, rl=1.6))):
        _g.make(nm, V['e'], tstop='3m', state='none', overrides={'CSS': '4.7n', 'gear': 1}, **kw)
        p = nm + '.cir'; s = open(p, encoding='latin-1').read(); s = s.replace('.tran 0 3m 0 100n', '.tran 0 3m 0 100n uic')
        open(p, 'w', encoding='latin-1', newline='').write(s); names.append(nm)
print(' '.join(names))
