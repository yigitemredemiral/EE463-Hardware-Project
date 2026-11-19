"""Config G (VDMOS models, fast) = F (e + LM74700 v2) + compensation A + CRUN 1n (RUN-GND, fitted) + new HF path
(Chf 3x100n, Lser 1 nH: CHF1 + CHF2/CHF3). Used for checks that do not depend on MOSFET model detail:
FRA at 90 W, short-circuit recovery, hot plug, RUN threshold with CRUN, LM74500 vs LM74700 loss."""
import sys, gen, gen2
COMP = '27n Rser=8.2K Cpar=470p'
CHFNEW = [('Chf QD 0 100n Rser=30m Lser=500p', 'Chf QD 0 300n Rser=10m Lser=1n')]
CRUN = '\nCrun RUN 0 1n'
SHORT = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '7m,RL,7.01m,RFAULT,13m,RFAULT,13.01m,RL')]
# LM74500-Q1 behavioural: charge pump keeps the FET fully on (VGS ~12 V, datasheet CP on/off 10.3-13 V), no reverse
# current blocking; same UVLO and gate pull-down when disabled / input below UVLO.
IDEAL500 = """MRP CABLE GRP UNPROTECTED BSC026N08NS5
Bid UNPROTECTED GRP I=en5()*0.3m*0.5*(1-tanh((V(GRP,UNPROTECTED)-12)/0.2)) - (1-en5())*V(GRP,UNPROTECTED)/5
.func en5() 0.5*(1+tanh((V(UNPROTECTED)-3.9)/0.2))
RgLeak GRP UNPROTECTED 10Meg
Biq UNPROTECTED 0 I=80u*en5()
"""
def ideal(which='700'):
    r = gen2.ideal_diode()
    if which == '500': r = [(a, IDEAL500 if 'MRP CABLE' in b else b) for a, b in r]
    return r
names = []
def mk(name, which='700', crun=True, chf=True, extra='', **kw):
    o = kw.pop('overrides', {}); o['replace'] = ideal(which) + (CHFNEW if chf else []) + o.get('replace', []); o['COMP'] = COMP
    names.append(gen.make(name, 'e', overrides=o, extra=(CRUN if crun else '') + extra, **kw))
st = lambda v, t=27: f'RevF1_G_prime{t}_{v}V.state'
stage = sys.argv[1]
if stage == 'prime':
    for v in (20, 48): mk(f'RevF1_G_prime27_{v}V', vin=v, prime=True)
    mk('RevF1_G_prime70_48V', vin=48, hot=True, prime=True)
    mk('RevF1_G500_prime27_20V', which='500', vin=20, prime=True)
    for cab, (L, R) in {'1u': ('1u', '50m'), '0p5u': ('0.5u', '20m')}.items():   # hot plug: board dead, 48 V applied at 1 us
        mk(f'RevF1_G_hotplug48_cable{cab}', vin=48, tstop='3m', state='none', overrides={'gear': 1, 'replace': [
            ('V1 SOURCE 0 {VIN}\n', 'V1 SOURCE 0 PWL(0 0 1u 0 1.001u 48)\n'),
            ('Rsource SOURCE UNPROTECTED 50m', f'Rsource SOURCE NCAB {R}\nLcab NCAB UNPROTECTED {L}\nCanode UNPROTECTED 0 22n')]})
    for c in (True, False):   # RUN threshold: VIN ramps 0 -> 20 V in 20 ms, 2.4 ohm
        mk(f'RevF1_G_runramp_{"crun" if c else "nocrun"}', crun=c, vin=20, tstop='22m', state='none',
           overrides={'gear': 1, 'replace': [('V1 SOURCE 0 {VIN}\n', 'V1 SOURCE 0 PWL(0 0 20m 20)\n')]})
elif stage == 'main':
    for v in (20, 48): mk(f'RevF1_G_fra90_{v}V', vin=v, rl=1.6, state=st(v), overrides={'fra': 1, 'replace': [
        ('@LOOP OUT FBOUT fstart=500 fend=16k oct=1 delay=6m pp0=50m pp1=50m f0=1k f1=2k tsettle=1m tavgmin=2m nmax=1',
         '@LOOP OUT FBOUT fstart=500 fend=50000 oct=2 delay=3m pp0=40m pp1=15m f0=2k f1=10k tsettle=1m tavgmin=1m nmax=1')]})
    for v, t, hot in ((48, 27, False), (48, 70, True), (20, 27, False)):
        mk(f'RevF1_G_short_{v}V_{t}' + ('_hot_L20n' if hot else ''), vin=v, hot=hot, test=1, rfault='5m', tstop='19m',
           state=st(v, t), overrides={'replace': SHORT})
    mk('RevF1_G_20V_90W', vin=20, rl=1.6, state=st(20))
    mk('RevF1_G500_20V_90W', which='500', vin=20, rl=1.6, state='RevF1_G500_prime27_20V.state')
print(' '.join(names))
