"""Batch 3b: final config F = variant e (RFREQ 24.9k, RGH 6.8, Q1 BSC040 scaled, Q2 BSC026)
+ LM74700 behavioural ideal diode + RSETT 11.8k + ROVB 17.4k."""
import gen, gen2
ID = gen2.ideal_diode()
FAULT13 = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '7m,RL,7.01m,RFAULT,13m,RFAULT,13.01m,RL')]
names = []
def mk(name, **kw):
    o = kw.pop('overrides', {})
    o['replace'] = ID + o.get('replace', [])
    names.append(gen.make(name, 'e', overrides=o, **kw))
for v in (20, 24, 36, 48):
    mk(f'RevF1_F_{v}V_60W', vin=v, state='RevF1_F_prime27.state')
for v in (20, 48):
    mk(f'RevF1_F_{v}V_90W', vin=v, rl=1.6, state='RevF1_F_prime27.state')
mk('RevF1_F_limit13_48V_27', vin=48, test=1, tstop='19m', state='RevF1_F_prime27.state',
   overrides={'replace': FAULT13})
mk('RevF1_F_limit13_48V_hot70_L20n', vin=48, hot=True, test=1, tstop='19m', state='RevF1_F_prime70.state',
   overrides={'replace': FAULT13})
for v in (20, 24, 36, 48):
    mk(f'RevF1_F_fra_{v}V', vin=v, state='RevF1_F_prime27.state',
       overrides={'fra': 1, 'replace': gen2.fra_line()})
for v, il in ((20, 6), (36, 3), (48, 3)):
    mk(f'RevF1_F_start_{v}V_{il}A_90W', vin=v, rl=1.6, tstop='25m', state='none',
       overrides={'gear': 1, 'replace': gen2.lab_supply(il)})
open('b3b.txt', 'w').write(' '.join(names))
print(' '.join(names))
