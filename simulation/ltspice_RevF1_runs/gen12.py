"""Variants c, d, e with official _L0 models, same procedure as the original variant study (24 V primes at 27/70 C with CSS 22n + gear,
14 ms runs from the prime, measure 12-14 ms; hot 0.5 ohm event 7-10 ms). Primes are cold (uic) because LTspice rejects
VDMOS states for the official-model circuit."""
import sys, gen, gen7
VV = {'c': ('24.3k', '4.7', 'BSC040N08NS5'), 'd': ('24.3k', '3.3', 'BSC040N08NS5'), 'e': ('24.9k', '6.8', 'BSC040N08NS5')}; names = []
def mk(name, k, uic=False, rep=(), **kw):
    V = VV[k]; o = kw.pop('overrides', {}); o['replace'] = gen7.official(V[2]) + list(rep) + o.get('replace', [])
    gen.make(name, V, extra=gen7.EXTRA, overrides=o, **kw)
    if uic:
        p = name + '.cir'; s = open(p, encoding='latin-1').read(); s = s.replace('.tran 0 6m 0 100n', '.tran 0 6m 0 100n uic')
        assert ' uic' in s; open(p, 'w', encoding='latin-1', newline='').write(s)
    names.append(name)
ks = sys.argv[2] if len(sys.argv) > 2 else 'cde'
for k in ks:
    if sys.argv[1] == 'prime':
        for hot in (False, True): mk(f'RevF1_OP{k}_prime{70 if hot else 27}', k, uic=True, vin=24, hot=hot, prime=True)
    else:
        for v in (20, 24, 36, 48): mk(f'RevF1_OP{k}_{v}V_60W', k, vin=v, state=f'RevF1_OP{k}_prime27.state')
        mk(f'RevF1_OP{k}_48V_90W', k, vin=48, rl=1.6, state=f'RevF1_OP{k}_prime27.state')
        mk(f'RevF1_OP{k}_limit_48V_hot70_L20n', k, vin=48, hot=True, test=1, state=f'RevF1_OP{k}_prime70.state')
        mk(f'RevF1_OP{k}_48V_90W_hot70_L20n', k, vin=48, rl=1.6, hot=True, state=f'RevF1_OP{k}_prime70.state')
print(' '.join(names))
