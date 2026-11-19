"""Final config FA = F + compensation A (RITH 8.2k, CITH 27n, CITHP 470p): re-check of transient-sensitive cases."""
import gen, gen2
ID = gen2.ideal_diode(); COMP = '27n Rser=8.2K Cpar=470p'; names = []
FAULT13 = [('7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL', '7m,RL,7.01m,RFAULT,13m,RFAULT,13.01m,RL')]
def mk(name, **kw):
    o = kw.pop('overrides', {}); o['replace'] = ID + o.get('replace', []); o['COMP'] = COMP
    names.append(gen.make(name, 'e', overrides=o, **kw))
for v in (20, 48): mk(f'RevF1_FA_{v}V_90W', vin=v, rl=1.6, state=f'RevF1_F_prime27_{v}V.state')
mk('RevF1_FA_limit13_48V_27', vin=48, test=1, tstop='19m', state='RevF1_F_prime27_48V.state', overrides={'replace': FAULT13})
mk('RevF1_FA_limit13_48V_hot70_L20n', vin=48, hot=True, test=1, tstop='19m', state='RevF1_F_prime70_48V.state', overrides={'replace': FAULT13})
for v, il in ((20, 6), (36, 3), (48, 3)):
    mk(f'RevF1_FA_start_{v}V_{il}A_90W', vin=v, rl=1.6, tstop='25m', state='none', overrides={'gear': 1, 'replace': gen2.lab_supply(il)})
print(' '.join(names))
