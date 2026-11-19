"""Compensation candidates for config F (FRA at 4 VIN). A: RITH 8.2k / CITH 27n; B: RITH 10k / CITH 33n (CITHP 470p kept)."""
import gen, gen2
ID = gen2.ideal_diode(); names = []
CAND = {'A': '27n Rser=8.2K Cpar=470p', 'B': '33n Rser=10K Cpar=470p'}
for c, spec in CAND.items():
    for v in (20, 24, 36, 48):
        names.append(gen.make(f'RevF1_F_fra{c}_{v}V', 'e', vin=v, state=f'RevF1_F_prime27_{v}V.state',
                              overrides={'fra': 1, 'COMP': spec, 'replace': ID + gen2.fra_line()}))
print(' '.join(names))
