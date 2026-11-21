"""Thermal (5-min continuous run + steady state) and PCB current-density figures."""
import numpy as np, json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import thermal as th, pcbmodel as pm, irdrop as ir
OUT = os.environ.get('OUT', 'out'); FIG = os.path.join(OUT, 'fig'); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 150, 'savefig.bbox': 'tight'})
R = json.load(open('results.json')); RES = {}
def save(n): plt.savefig(os.path.join(FIG, n)); plt.savefig(os.path.join(FIG, n.replace('.png', '.pdf'))); plt.close()
W, H = pm.M['W'], pm.M['H']
LIM = {'Q1': 150, 'Q2': 150, 'Q3': 150, 'U1': 125, 'L1': 125, 'RS1': 155, 'COUT1': 105, 'COUT2': 105, 'CINB1': 105, 'CINB2': 105, 'CINB3': 105, 'RSN1': 155, 'U5': 125, 'J2': 105}
COMPS = ['Q1', 'Q2', 'Q3', 'U1', 'L1', 'RS1', 'RSN1', 'COUT1', 'COUT2', 'CINB1', 'CINB2', 'U5', 'J2']

def losses(r):
    P = r['loss']; misc = P['U1_drv_misc']
    return {'Q1': P['Q1'] + P['PCB_Cu'] / 2 + 0.15 * misc, 'Q2': P['Q2'] + P['PCB_Cu'] / 2 + 0.15 * misc, 'Q3': P['Q3'],
            'L1': P['L1_dcr'] + P['L1_core'], 'RS1': P['RS1'], 'RSN1': P['RSN1'], 'U1': 0.7 * misc,
            'CINB1': P['CIN'] / 3, 'CINB2': P['CIN'] / 3, 'CINB3': P['CIN'] / 3, 'COUT1': P['COUT'] / 2, 'COUT2': P['COUT'] / 2}

def tj(T, ref, L):
    return th.comp_temp(T, ref) + (L.get(ref, 0) * th.RTH_JC.get(ref, 0))

SCN = [('s24', '24 V / 60 W'), ('s48', '48 V / 60 W'), ('s20', '20 V / 60 W'), ('h24', '24 V / 90 W'), ('h48', '48 V / 90 W')]
SCN = [s for s in SCN if s[0] in R]
series = {}
for tag, lab in SCN:
    L = losses(R[tag]); hist = {c: [] for c in COMPS}; tt = []
    def rec(t, T):
        tt.append(t)
        for c in COMPS: hist[c].append(tj(T, c, L))
    t, T300 = th.transient(L, 300.0, rec)
    Tss = th.steady(L)
    RES[tag] = dict(label=lab, Ptot=sum(L.values()), loss=L,
                    rise300={c: hist[c][-1] for c in COMPS}, rise_ss={c: tj(Tss, c, L) for c in COMPS},
                    board_avg300=float(T300[:th.N1].mean()), board_avg_ss=float(Tss[:th.N1].mean()))
    series[tag] = (np.array(tt), {c: np.array(v) for c, v in hist.items()})
    np.save(f'T300_{tag}.npy', T300); np.save(f'Tss_{tag}.npy', Tss)
    print(tag, 'Ptot %.2f' % sum(L.values()), {c: round(v, 1) for c, v in RES[tag]['rise300'].items()})

# --- time curves (24/60 and 48/90)
for tag in ('s24', 'h48', 's48'):
    if tag not in series: continue
    t, h = series[tag]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for c in ['Q1', 'Q2', 'Q3', 'U1', 'L1', 'RS1', 'COUT1', 'CINB2']:
        ax.plot(t, 25 + h[c], label=c)
    ax.axvline(300, c='k', ls=':', lw=.8); ax.set_xlabel('t [s]'); ax.set_ylabel('T [°C] (T$_a$ = 25 °C)')
    ax.set_title(f'5-minute continuous run, {RES[tag]["label"]} (Q/U: junction, others: body)'); ax.legend(ncol=4, fontsize=7)
    save(f'th_time_{tag}.png')

# --- maps
def tmap(T, layer=0): return T[layer * th.N1:(layer + 1) * th.N1].reshape(th.NY, th.NX)
def outline(ax):
    for ref in ['Q1', 'Q2', 'Q3', 'U1', 'L1', 'RS1', 'COUT1', 'COUT2', 'CINB1', 'CINB2', 'CINB3', 'J1', 'J2', 'U2', 'U3']:
        f = pm.FPS[ref]; x0, y0, x1, y1 = f['bb']
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='w', lw=.6)); ax.text((x0 + x1) / 2, (y0 + y1) / 2, ref, color='w', fontsize=6, ha='center', va='center')
for tag in ('s24', 'h48'):
    if tag not in RES: continue
    T3, Ts = np.load(f'T300_{tag}.npy'), np.load(f'Tss_{tag}.npy')
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 2.9))
    vmax = 25 + tmap(Ts).max()
    for a, T, ttl in ((ax[0], T3, 't = 300 s (5 min)'), (ax[1], Ts, 'Steady state (t → ∞)')):
        im = a.imshow(25 + tmap(T), extent=(0, W, H, 0), cmap='inferno', vmin=25, vmax=vmax); outline(a); a.set_title(ttl, fontsize=9); a.grid(False)
        a.set_xlabel('x [mm]')
    ax[0].set_ylabel('y [mm]'); fig.colorbar(im, ax=ax, label='T [°C]', shrink=.9)
    fig.suptitle(f'Top layer (F.Cu) temperature, {RES[tag]["label"]}, T$_a$ = 25 °C'); save(f'th_map_{tag}.png')
    fig, ax = plt.subplots(1, 4, figsize=(9, 2.2))
    for l, k in enumerate(pm.LAYERS):
        im = ax[l].imshow(25 + tmap(T3, l), extent=(0, W, H, 0), cmap='inferno', vmin=25, vmax=25 + tmap(T3).max()); ax[l].set_title(k, fontsize=8); ax[l].grid(False); ax[l].set_xticks([]); ax[l].set_yticks([])
    fig.colorbar(im, ax=ax, shrink=.8, label='T [°C]'); fig.suptitle(f'Temperature per layer, t = 300 s, {RES[tag]["label"]}', fontsize=9); save(f'th_layers_{tag}.png')

# --- bar summary 300 s vs steady (Ta 25 and 40)
fig, ax = plt.subplots(figsize=(7.4, 3.4)); comps = ['Q1', 'Q2', 'Q3', 'U1', 'L1', 'RS1', 'COUT1', 'CINB2']; wdt = 0.8 / len(SCN)
for i, (tag, lab) in enumerate(SCN):
    ax.bar(np.arange(len(comps)) + i * wdt, [25 + RES[tag]['rise300'][c] for c in comps], wdt, label=lab)
ax.set_xticks(np.arange(len(comps)) + 0.4 - wdt / 2); ax.set_xticklabels(comps); ax.set_ylabel('T @ 300 s [°C]'); ax.legend(fontsize=7, ncol=3); ax.set_title('Temperatures after 5 minutes (T$_a$ = 25 °C)')
save('th_bar.png')

# --- copper / via maps
cov = pm.coverage(5)
fig, ax = plt.subplots(1, 4, figsize=(9, 2.2))
for l, k in enumerate(pm.LAYERS):
    ax[l].imshow(cov[k], extent=(0, W, H, 0), cmap='copper', vmin=0, vmax=1); ax[l].set_title(f'{k} (copper {100 * cov[k].mean():.0f} %)', fontsize=8); ax[l].grid(False); ax[l].set_xticks([]); ax[l].set_yticks([])
v = np.array(pm.M['vias']); ax[0].plot(v[:, 0], v[:, 1], '.', c='c', ms=1.5)
fig.suptitle('Copper used in the thermal model (KiCad RevF4) and vias', fontsize=9); save('copper.png')

# --- IR drop / current density
IRC = [('/SW', [('Q1', None, 2.5), ('Q2', None, 2.5)], [('L1', ['1'])], 'SW: Q1/Q2 → L1 (5 A)', ['F']),
       ('/VOUT', [('RS1', ['2'], 5.0)], [('J2', ['1'])], 'VOUT: RS1 → J2 (5 A)', ['F', 'In2']),
       ('GND', [('J2', ['2'], 5.0)], [('Q2', None), ('J1', ['2'])], 'GND return: J2 → Q2/J1 (5 A)', ['F', 'In1', 'B']),
       ('/VIN', [('Q3', None, 2.6)], [('Q1', None)], 'VIN: Q3 → Q1 (2.6 A, 24 V)', ['F', 'In2', 'B'])]
RES['ir'] = {}
for net, src, snk, ttl, lays in IRC:
    try: r = ir.solve(net, src, snk)
    except Exception as e: print('IR fail', net, e); continue
    jmax = max(np.nanmax(r['J'][k]) for k in lays if np.any(np.isfinite(r['J'][k])))
    RES['ir'][net] = dict(title=ttl, R_mohm=r['R'] * 1e3, P_mW=r['P'] * 1e3, Jmax=float(jmax), dV_mV=r['R'] * r['I'] * 1e3)
    fig, ax = plt.subplots(1, len(lays), figsize=(3.0 * len(lays) + 1, 2.6))
    ax = np.atleast_1d(ax)
    for a, k in zip(ax, lays):
        im = a.imshow(r['J'][k], extent=(0, W, H, 0), cmap='viridis', vmin=0, vmax=jmax); a.set_title(k, fontsize=8); a.grid(False)
        yy, xx = np.nonzero(sum(np.isfinite(r['J'][q]) for q in lays)); d = ir.DX
        a.set_xlim(xx.min() * d - 1, xx.max() * d + 1); a.set_ylim(yy.max() * d + 1, yy.min() * d - 1)
    fig.colorbar(im, ax=list(ax), label='Current density [A/mm]', shrink=.9)
    fig.suptitle(f'{ttl}: R = {r["R"] * 1e3:.2f} mΩ, P = {r["P"] * 1e3:.0f} mW, J$_{{max}}$ = {jmax:.1f} A/mm', fontsize=9)
    save('ir_' + net.strip('/').lower() + '.png')
    print(net, RES['ir'][net])
json.dump(RES, open(os.path.join(OUT, 'thermal.json'), 'w'), indent=1, default=float)
