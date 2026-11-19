"""Config F = variant e (RFREQ 24.9k, RGH 6.8, Q1 BSC040 scaled model, Q2 BSC026) + LM74700 behavioural ideal
diode v2 (gen2.IDEAL) + RSETT 11.8k + ROVB 17.4k. Stage 'prime': VIN-specific prime states (cold, gear, CSS 22n),
lab-supply cold starts (CSS 100n). Stage 'main': steady state / limit / FRA from the matching prime, reverse tests."""
import sys, gen, gen2
ID = gen2.ideal_diode()
FAULT13 = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '7m,RL,7.01m,RFAULT,13m,RFAULT,13.01m,RL')]
stage = sys.argv[1]; css = sys.argv[2] if len(sys.argv) > 2 else None; names = []
def mk(name, **kw):
    o = kw.pop('overrides', {}); o['replace'] = ID + o.get('replace', [])
    if css and 'start' in name: o['CSS'] = css
    names.append(gen.make(name, 'e', overrides=o, **kw))
st = lambda v, t=27: f'RevF1_F_prime{t}_{v}V.state'
if stage == 'prime':
    for v in (20, 24, 36, 48): mk(f'RevF1_F_prime27_{v}V', vin=v, prime=True)
    mk('RevF1_F_prime70_48V', vin=48, hot=True, prime=True)
if stage in ('prime', 'start'):
    sfx = f'_CSS{css}' if css else ''
    for v, il in ((20, 6), (36, 3), (48, 3)):
        mk(f'RevF1_F_start_{v}V_{il}A_90W{sfx}', vin=v, rl=1.6, tstop='25m', state='none',
           overrides={'gear': 1, 'replace': gen2.lab_supply(il)})
if stage == 'main':
    for v in (20, 24, 36, 48): mk(f'RevF1_F_{v}V_60W', vin=v, state=st(v))
    for v in (20, 48): mk(f'RevF1_F_{v}V_90W', vin=v, rl=1.6, state=st(v))
    mk('RevF1_F_limit13_48V_27', vin=48, test=1, tstop='19m', state=st(48), overrides={'replace': FAULT13})
    mk('RevF1_F_limit13_48V_hot70_L20n', vin=48, hot=True, test=1, tstop='19m', state=st(48, 70), overrides={'replace': FAULT13})
    for v in (20, 24, 36, 48): mk(f'RevF1_F_fra_{v}V', vin=v, state=st(v), overrides={'fra': 1, 'replace': gen2.fra_line()})
    mk('RevF1_F_reverse48_only', vin=24, tstop='3m', state='none',
       overrides={'gear': 1, 'replace': [('V1 SOURCE 0 {VIN}\n', 'V1 SOURCE 0 PWL(0 0 0.5m -48 3m -48)\n')]})
    mk('RevF1_F_reverse48_then24V', vin=24, tstop='25m', state='none', overrides={'gear': 1, 'replace': gen2.reverse_then_forward(-48, 24)})
print(' '.join(names))
