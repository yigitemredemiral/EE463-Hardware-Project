"""Q1 junction-temperature estimate for RevF1 (variant e, BSC040N08NS5). Hand model, NOT a measurement.
Tj = Ta + P_Q1*theta_local + P_rest*theta_coupling   (all K/W, see paket1_sonuclar.md for sources)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))
def g(n, k): return R[n][k]
# Q1 loss from LTspice (27 C model) + Rds(on) temperature rise of conduction part (x1.7 at ~100 C)
cases = {}
for tag, n, iout in (('48V/60W', 'RevF1_F_48V_60W', 5.0), ('48V/90W', 'RevF1_F_48V_90W', 7.5)):
    pq1 = g(n, 'PQ1'); d = 12 / 48; pcond = d * iout**2 * 4.0e-3
    p = pq1 + 0.7 * pcond
    prest = g(n, 'Pin_conn') - g(n, 'Pout') - g(n, 'PQ1') - iout**2 * 0.020   # L1 DCR loss stays in L1 body
    cases[tag] = (p, prest)
TH = {  # name: (theta_local, theta_coupling, fan_W)
    '(a) bakır dökümü + termal via (4 kat)': (35.0, 5.0, 0.0),
    '(b) (a) + alt yüzde açık bakıra yalıtkan pedle küçük soğutucu': (15.6, 5.0, 0.0),
    '(c) (b) + 40 mm 12 V fan (0,62 W, çıkıştan)': (9.4, 3.0, 0.62),
}
rows = []
for name, (tl, tc, pf) in TH.items():
    for tag, (p, prest) in cases.items():
        for ta in (25, 40):
            rows.append((name, tag, ta, p, prest, ta + p * tl + prest * tc))
print('| Soğutma | Nokta | Ta (°C) | P_Q1 (W) | Diğer kart kaybı (W) | Tj Q1 (°C) |')
print('|---|---|---|---|---|---|')
for r in rows:
    print(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]:.2f} | {r[4]:.2f} | {r[5]:.0f} |')
# efficiency with fan
eff = {}
for v in (20, 24, 36, 48):
    n = f'RevF1_F_{v}V_60W'; pin = g(n, 'Pin_conn'); pout = g(n, 'Pout'); e0 = pout / pin
    eff[v] = (100 * e0, 100 * pout / (pin + 0.62 / e0))
print('\n| VIN | η (fan yok) % | η (fan dahil) % |\n|---|---|---|')
for v, (a, b) in eff.items(): print(f'| {v} V | {a:.2f} | {b:.2f} |')
print(f'| ort. | {sum(a for a,b in eff.values())/4:.2f} | {sum(b for a,b in eff.values())/4:.2f} |')
