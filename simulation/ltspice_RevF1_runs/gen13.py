"""Final config H (official _L0 models for Q1/Q2; Q3 stays VDMOS BSC026: with Q3 official + the behavioural LM74700 source the OP/transient crawls; Q3 only conducts), no uic): variant c (RFREQ 24.3k, RGH 4.7, Q1 BSC040N08NS5) +
LM74700 behavioural v2 + compensation A (8.2k/27n/470p) + CRUN 1 nF + new HF path (Chf 3x100n, 1 nH).
Primes cold from the DC operating point (source stepping), gear, CSS 22n, 6 ms, VIN-specific."""
import sys
_argv = sys.argv; sys.argv = [sys.argv[0], "lib"]
import gen, gen2, gen7, gen10
sys.argv = _argv
V = ('24.3k', '4.7', 'BSC040N08NS5'); names = []
FAULT13 = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '7m,RL,7.01m,RFAULT,13m,RFAULT,13.01m,RL')]
def mk(name, **kw):
    o = kw.pop('overrides', {})
    o['replace'] = gen7.official(V[2]) + gen2.ideal_diode() + gen10.CHFNEW + o.get('replace', []); o['COMP'] = gen10.COMP
    names.append(gen.make(name, V, extra=gen7.EXTRA + gen10.CRUN, overrides=o, **kw))
st = lambda v, t=27: f'RevF1_H_prime{t}_{v}V.state'
if sys.argv[1] == 'prime':
    for v in (20, 24, 36, 48): mk(f'RevF1_H_prime27_{v}V', vin=v, prime=True)
    mk('RevF1_H_prime70_48V', vin=48, hot=True, prime=True)
else:
    for v in (20, 24, 36, 48): mk(f'RevF1_H_{v}V_60W', vin=v, state=st(v))
    for v in (20, 48): mk(f'RevF1_H_{v}V_90W', vin=v, rl=1.6, state=st(v))
    mk('RevF1_H_48V_90W_hot70_L20n', vin=48, rl=1.6, hot=True, state=st(48, 70))
    mk('RevF1_H_limit13_48V_hot70_L20n', vin=48, hot=True, test=1, tstop='19m', state=st(48, 70), overrides={'replace': FAULT13})
    mk('RevF1_H_short13_48V_hot70_L20n', vin=48, hot=True, test=1, rfault='5m', tstop='19m', state=st(48, 70), overrides={'replace': FAULT13})
    for v, rl, tag in ((20, 2.4, '60W'), (20, 1.6, '90W'), (48, 1.6, '90W')):
        mk(f'RevF1_H_fra_{v}V_{tag}', vin=v, rl=rl, state=st(v), overrides={'fra': 1, 'replace': [
            ('@LOOP OUT FBOUT fstart=500 fend=16k oct=1 delay=6m pp0=50m pp1=50m f0=1k f1=2k tsettle=1m tavgmin=2m nmax=1',
             '@LOOP OUT FBOUT fstart=500 fend=50000 oct=2 delay=3m pp0=40m pp1=15m f0=2k f1=10k tsettle=1m tavgmin=1m nmax=1')]})
print(' '.join(names))
