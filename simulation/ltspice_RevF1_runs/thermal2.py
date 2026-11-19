"""Q1 junction temperature, rev 2 (hand model, NOT a measurement). Config H losses (official _L0 Q1/Q2).
Tj = Ta + P_Q1*theta_local + P_rest*theta_coupling.
Geometry (KiCad_RevF1 rev 2): 12 Q1 thermal vias (0.6/0.3 mm) of which 9 land in the B.Cu VIN island; exposed window
(B.Mask opening) 8.2 x 4.5 mm = 0.369 cm2 (Paket 1 assumed ~2 cm2 contact -> heatsink rows were optimistic).
(a) copper + vias, no heatsink: theta_local 38 K/W (Paket 1: 35 K/W with 25 vias; fewer vias -> +3 K/W, estimate).
(b) + insulated small heatsink on the 0.369 cm2 window, series path: theta_JC 1.4 + F.Cu spreading 2 + 9 vias in parallel
    (one 0.3 mm via, 25 um plating, 1.6 mm: ~174 K/W -> 19.3 K/W) + insulator (Sil-Pad 900S ~3.9 K*cm2/W / 0.369 cm2 = 10.6)
    + spreading into heatsink base from the small contact 3 + heatsink 18 K/W (natural) = 54.3 K/W, parallel with (a).
(c) (b) with 40 mm fan: heatsink 10 K/W, board path 24 K/W, coupling 3 K/W; fan 0.62 W counted in efficiency."""
import json
R = json.load(open('results.json'))
def g(n, k): return R[n][k]
cases = {}
for tag, n, iout in (('48V/60W', 'RevF1_H2_48V_60W', 5.0), ('48V/90W', 'RevF1_H_48V_90W', 7.5)):
    pq1 = g(n, 'PQ1'); p = pq1 + 0.7 * (12 / 48) * iout**2 * 4.0e-3
    prest = g(n, 'Pin_conn') - g(n, 'Pout') - pq1 - iout**2 * 0.020
    cases[tag] = (p, prest)
hs = 1.4 + 2 + 174 / 9 + 3.9 / 0.369 + 3 + 18
hsf = 1.4 + 2 + 174 / 9 + 3.9 / 0.369 + 3 + 10
par = lambda a, b: a * b / (a + b)
TH = {'(a) bakır + 12 termal via': (38.0, 5.0),
      f'(b) (a) + 0,37 cm² pencereye yalıtkan ped + 18 K/W soğutucu (yol {hs:.0f} K/W)': (par(38.0, hs), 5.0),
      f'(c) (b) + 40 mm fan (yol {hsf:.0f} K/W, kart 24 K/W)': (par(24.0, hsf), 3.0)}
print('| Soğutma | θ_yerel (K/W) | Nokta | Ta (°C) | P_Q1 (W) | Diğer kayıp (W) | Tj Q1 (°C) |\n|---|---|---|---|---|---|---|')
for name, (tl, tc) in TH.items():
    for tag, (p, prest) in cases.items():
        for ta in (25, 40):
            print(f'| {name} | {tl:.1f} | {tag} | {ta} | {p:.2f} | {prest:.2f} | {ta + p*tl + prest*tc:.0f} |')
