"""Official-model (gen7) variant re-check and RGH sweep (Schottky input, as in the original variant study).
stage prime: cold primes (gear + uic, CSS 22n, 6 ms) at 24 V for b/c/d/e, 27 C and 70 C hot corner.
stage main : steady state 6 ms from the prime (measure last 2 ms), hot 0.5 ohm limit event 2..8 ms (tstop 12 ms),
             RGH sweep 5.6/6.8/8.2/10 ohm at 48 V / 90 W, 27 C nominal and 70 C hot corner."""
import sys, gen, gen7
FAULT = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '2m,RL,2.01m,RFAULT,8m,RFAULT,8.01m,RL')]
V = {'b': ('24.3k', '4.7', 'BSC026N08NS5'), 'c': ('24.3k', '4.7', 'BSC040N08NS5'),
     'd': ('24.3k', '3.3', 'BSC040N08NS5'), 'e': ('24.9k', '6.8', 'BSC040N08NS5')}
names = []
def mk(name, var, uic=False, **kw):
    o = kw.pop('overrides', {}); o['replace'] = gen7.official(var[2]) + o.get('replace', [])
    gen.make(name, var, extra=gen7.EXTRA, overrides=o, **kw)
    if uic:
        p = name + '.cir'; s = open(p, encoding='latin-1').read()
        assert s.count('.tran 0 ') == 1
        s = s.replace('.tran 0 6m 0 100n', '.tran 0 6m 0 100n uic'); assert ' uic' in s
        open(p, 'w', encoding='latin-1', newline='').write(s)
    names.append(name)
stage = sys.argv[1]
if stage == 'prime':
    for k, v in V.items():
        for hot in (False, True):
            mk(f'RevF1_O{k}_prime{70 if hot else 27}', v, uic=True, vin=24, hot=hot, prime=True)
else:
    for k, v in V.items():
        for vin in (20, 24, 36, 48): mk(f'RevF1_O{k}_{vin}V_60W', v, vin=vin, tstop='6m', state=f'RevF1_O{k}_prime27.state')
        mk(f'RevF1_O{k}_48V_90W', v, vin=48, rl=1.6, tstop='6m', state=f'RevF1_O{k}_prime27.state')
        mk(f'RevF1_O{k}_limit_48V_hot70_L20n', v, vin=48, hot=True, test=1, tstop='12m', state=f'RevF1_O{k}_prime70.state',
           overrides={'replace': FAULT})
    for r in ('5.6', '6.8', '8.2', '10'):
        v = ('24.9k', r, 'BSC040N08NS5'); tag = r.replace('.', 'p')
        if r != '6.8': mk(f'RevF1_Orgh{tag}_48V_90W_27', v, vin=48, rl=1.6, tstop='6m', state='RevF1_Oe_prime27.state')
        mk(f'RevF1_Orgh{tag}_48V_90W_hot70', v, vin=48, rl=1.6, hot=True, tstop='6m', state='RevF1_Oe_prime70.state')
print(' '.join(names))
