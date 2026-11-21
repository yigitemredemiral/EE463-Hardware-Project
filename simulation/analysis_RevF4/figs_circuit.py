"""Circuit-simulation figures -> OUT/fig/*.png and OUT/circuit.json"""
import raw, numpy as np, json, os, re, glob
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OUT = os.environ.get('OUT', 'out'); FIG = os.path.join(OUT, 'fig'); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 150, 'savefig.bbox': 'tight',
                     'axes.prop_cycle': matplotlib.cycler(color=['#1f5aa6', '#d1495b', '#2a9d8f', '#e9a03b', '#6c4f9e', '#555555'])})
R = json.load(open('results.json')); C = {}
def get(d, n):
    for k in d:
        if k.lower() == n.lower(): return d[k]
    raise KeyError(n)
def save(name): plt.savefig(os.path.join(FIG, name)); plt.savefig(os.path.join(FIG, name.replace('.png', '.pdf'))); plt.close()

# ---------- steady-state waveforms (3 cycles) at 24 V and 48 V, 60 W
for tag, vin in (('s24', 24), ('s48', 48), ('h24', 24)):
    d = raw.read(tag + '.raw'); t = d['t']; g = lambda n: get(d, n)
    t1 = t[-1]; t0 = t1 - 3 / 94.3e3; m = t >= t0; tu = (t[m] - t0) * 1e6
    fig, ax = plt.subplots(5, 1, figsize=(7.2, 8.4), sharex=True)
    ax[0].plot(tu, g('V(sw)')[m]); ax[0].set_ylabel('V(SW) [V]')
    ax[1].plot(tu, g('V(gh)')[m] - g('V(sw)')[m], label='V$_{GS}$ Q1 (GH-SW)'); ax[1].plot(tu, g('V(gl)')[m], label='V$_{GS}$ Q2 (GL)'); ax[1].set_ylabel('Gate [V]'); ax[1].legend(loc='right', fontsize=7)
    ax[2].plot(tu, g('I(L1)')[m], label='I$_L$'); ax[2].plot(tu, g('Id(MQ1)')[m], label='I$_D$ Q1', alpha=.8); ax[2].plot(tu, g('Id(MQ2)')[m], label='I$_D$ Q2', alpha=.8); ax[2].set_ylabel('Current [A]'); ax[2].legend(loc='right', fontsize=7)
    vo = g('V(out)')[m]; ax[3].plot(tu, (vo - vo.mean()) * 1e3); ax[3].set_ylabel('V$_{OUT}$ AC [mV]')
    vi = g('V(in)')[m]; ax[4].plot(tu, (vi - vi.mean()) * 1e3, color='#e9a03b'); ax[4].set_ylabel('V$_{IN}$ AC [mV]'); ax[4].set_xlabel('t [µs]')
    fig.suptitle(f'Steady-state waveforms, V$_{{IN}}$={vin} V, P$_{{OUT}}$={R[tag]["Pout"]:.0f} W', y=0.995)
    save(f'ss_{tag}.png')
    # switching edge zoom
    sw = g('V(sw)'); mm_ = (t > t1 - 1 / 94.3e3) & (t <= t1); tt = t[mm_]; s = sw[mm_]
    k = np.flatnonzero((s[:-1] < vin / 2) & (s[1:] >= vin / 2))
    if len(k):
        tc = tt[k[0]]; w = (t > tc - 60e-9) & (t < tc + 120e-9); tn = (t[w] - tc) * 1e9
        fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True)
        ax[0].plot(tn, sw[w], label='V(SW)'); ax[0].plot(tn, g('V(qd)')[w], label='V(Q1 drain)'); ax[0].set_ylabel('[V]'); ax[0].legend(fontsize=7)
        ax[1].plot(tn, g('Id(MQ1)')[w], label='I$_D$ Q1'); ax[1].plot(tn, g('Id(MQ2)')[w], label='I$_D$ Q2'); ax[1].set_ylabel('[A]'); ax[1].set_xlabel('t [ns]'); ax[1].legend(fontsize=7)
        fig.suptitle(f'SW rising edge (V$_{{IN}}$={vin} V)'); save(f'edge_{tag}.png')
        C[f'sw_overshoot_{tag}'] = float(sw[w].max() - vin); C[f'sw_rise_ns_{tag}'] = float(np.ptp(tn[(sw[w] > .1 * vin) & (sw[w] < .9 * vin)])) if np.any((sw[w] > .1 * vin) & (sw[w] < .9 * vin)) else None
    # spectrum of output ripple
    m3 = t >= t1 - 2e-3; tt = np.linspace(t[m3][0], t1, 2 ** 16); vv = np.interp(tt, t, g('V(out)')) ; vv -= vv.mean()
    F = np.fft.rfftfreq(len(tt), tt[1] - tt[0]); A = 2 * np.abs(np.fft.rfft(vv * np.hanning(len(vv)))) / (len(vv) / 2)
    C[f'spec_{tag}'] = (F, A)

fig, ax = plt.subplots(figsize=(7.2, 3))
for tag in ('s24', 's48'):
    F, A = C.pop(f'spec_{tag}'); ax.semilogy(F / 1e3, A * 1e3 + 1e-6, label=f'{R[tag]["VIN"]} V')
ax.set_xlim(0, 1000); ax.set_ylim(1e-3, 100); ax.set_xlabel('f [kHz]'); ax.set_ylabel('V$_{OUT}$ amplitude [mV]'); ax.legend(); ax.set_title('Output ripple spectrum (60 W)')
save('spec_vout.png')
for k in [k for k in C if k.startswith('spec_')]: C.pop(k)

# ---------- efficiency and losses
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3))
for v, keys in ((24, ['l24_6', 'l24_15', 'l24_30', 's24', 'h24']), (48, ['l48_6', 'l48_15', 'l48_30', 's48', 'h48'])):
    ks = [k for k in keys if k in R]; ax[0].plot([R[k]['Pout'] for k in ks], [100 * R[k]['eff_with_core'] for k in ks], 'o-', label=f'{v} V')
ax[0].set_xlabel('P$_{OUT}$ [W]'); ax[0].set_ylabel('Efficiency [%]'); ax[0].legend(); ax[0].set_title('Efficiency vs load')
ks = [k for k in ('s20', 's24', 's36', 's48') if k in R]
ax[1].plot([R[k]['VIN'] for k in ks], [100 * R[k]['eff_with_core'] for k in ks], 'o-'); ax[1].set_xlabel('V$_{IN}$ [V]'); ax[1].set_title('Efficiency vs input (60 W)')
save('eff.png')
cats = ['Q1', 'Q2', 'Q3', 'L1_dcr', 'L1_core', 'RS1', 'CIN', 'COUT', 'RSN1', 'PCB_Cu', 'U1_drv_misc']
lab = ['Q1 (high side)', 'Q2 (low side)', 'Q3 (ideal diode)', 'L1 copper', 'L1 core*', 'RS1 shunt', 'C$_{IN}$ ESR', 'C$_{OUT}$ ESR', 'Snubber', 'PCB copper', 'Driver/IC/other']
ks = [k for k in ('s20', 's24', 's36', 's48', 'h24', 'h48') if k in R]
fig, ax = plt.subplots(figsize=(7.4, 3.6)); bot = np.zeros(len(ks))
cm = plt.get_cmap('tab20')
for i, c in enumerate(cats):
    v = np.array([R[k]['loss'][c] for k in ks]); ax.bar(range(len(ks)), v, bottom=bot, label=lab[i], color=cm(i)); bot += v
ax.set_xticks(range(len(ks))); ax.set_xticklabels([f"{R[k]['VIN']} V\n{R[k]['Pout']:.0f} W" for k in ks]); ax.set_ylabel('Loss [W]')
ax.legend(fontsize=7, ncol=2, loc='upper left'); ax.set_title('Loss breakdown'); save('loss_bar.png')

# ---------- startup
for tag, vin in (('start24', 24), ('start48', 48)):
    if not os.path.exists(tag + '.raw'): continue
    d = raw.read(tag + '.raw'); t = d['t'] * 1e3; g = lambda n: get(d, n)
    fig, ax = plt.subplots(4, 1, figsize=(7.2, 7), sharex=True)
    ax[0].plot(t, g('V(source)'), label='V$_{SOURCE}$'); ax[0].plot(t, g('V(in)'), label='V$_{IN}$ (board)'); ax[0].plot(t, g('V(out)'), label='V$_{OUT}$'); ax[0].set_ylabel('[V]'); ax[0].legend(fontsize=7)
    ax[1].plot(t, g('I(L1)'), lw=.5, label='I$_L$'); ax[1].plot(t, g('I(Rsource)'), lw=.8, label='I$_{IN}$'); ax[1].set_ylabel('[A]'); ax[1].legend(fontsize=7)
    ax[2].plot(t, g('V(ss)'), label='SS'); ax[2].plot(t, g('V(ith)'), label='ITH'); ax[2].plot(t, g('V(run)'), label='RUN'); ax[2].set_ylabel('[V]'); ax[2].legend(fontsize=7)
    ax[3].plot(t, g('V(intvcc)'), label='INTVCC'); ax[3].plot(t, g('V(pgood)'), label='PGOOD'); ax[3].set_ylabel('[V]'); ax[3].legend(fontsize=7); ax[3].set_xlabel('t [ms]')
    fig.suptitle(f'Start-up, V$_{{IN}}$={vin} V, 2.4 Ω (60 W)', y=.995); save(f'{tag}.png')
    vo = g('V(out)'); tt = t
    i90 = np.flatnonzero(vo > 0.9 * 12)[0] if np.any(vo > 10.8) else None; i10 = np.flatnonzero(vo > 1.2)[0] if np.any(vo > 1.2) else None
    C[tag] = dict(t_rise_ms=float(tt[i90] - tt[i10]) if i90 is not None else None, t_reg_ms=float(tt[i90]) if i90 is not None else None,
                  Vout_over=float(vo.max() - 12), Iin_pk=float(g('I(Rsource)').max()), IL_pk=float(g('I(L1)').max()))

# ---------- load step
if os.path.exists('step24.raw'):
    d = raw.read('step24.raw'); t = d['t']; g = lambda n: get(d, n)
    vo = g('V(out)'); il = g('I(L1)'); io = g('I(Rload)'); tm = t * 1e3
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5), sharey='row')
    for c, (ta, tb, ttl) in enumerate(((8.8e-3, 10e-3, '5 A → 2.5 A (9 ms)'), (11.8e-3, 13e-3, '2.5 A → 5 A (12 ms)'))):
        w = (t > ta) & (t < tb)
        ax[0, c].plot(tm[w], vo[w]); ax[0, c].set_title(ttl, fontsize=9)
        ax[1, c].plot(tm[w], il[w], lw=.6, label='I$_L$'); ax[1, c].plot(tm[w], io[w], label='I$_{OUT}$'); ax[1, c].set_xlabel('t [ms]')
    ax[0, 0].set_ylabel('V$_{OUT}$ [V]'); ax[1, 0].set_ylabel('[A]'); ax[1, 0].legend(fontsize=7)
    fig.suptitle('Load step, V$_{IN}$ = 24 V (60 W ↔ 30 W)'); save('loadstep.png')
    def dev(ta, tb):
        w = (t > ta) & (t < tb); base = raw.avg(t, vo, ta - 0.5e-3, ta); x = vo[w]
        k = np.flatnonzero(np.abs(x - base) > 0.01 * 12); ts = (t[w][k[-1]] - ta) * 1e3 if len(k) else 0
        return dict(undershoot=float(base - x.min()), overshoot=float(x.max() - base), settle_1pct_ms=float(ts))
    C['loadstep_down'] = dev(9e-3, 11.5e-3); C['loadstep_up'] = dev(12e-3, 14.5e-3)

# ---------- line step
if os.path.exists('line.raw'):
    d = raw.read('line.raw'); t = d['t']; g = lambda n: get(d, n); tm = t * 1e3; vo = g('V(out)')
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True)
    w = t > 8e-3
    ax[0].plot(tm[w], g('V(source)')[w], label='V$_{SOURCE}$'); ax[0].plot(tm[w], g('V(in)')[w], label='V$_{IN}$'); ax[0].set_ylabel('[V]'); ax[0].legend(fontsize=7)
    ax[1].plot(tm[w], vo[w]); ax[1].set_ylabel('V$_{OUT}$ [V]'); ax[1].set_xlabel('t [ms]')
    fig.suptitle('Line step 24 V → 36 V → 24 V (100 µs ramp), 60 W'); save('linestep.png')
    C['linestep'] = dict(dev_up=float(np.abs(vo[(t > 9e-3) & (t < 11e-3)] - 12).max()), dev_down=float(np.abs(vo[(t > 12e-3) & (t < 14e-3)] - 12).max()))

# ---------- fault (0.5 ohm, 7-10 ms)
if os.path.exists('fault.raw'):
    d = raw.read('fault.raw'); t = d['t']; g = lambda n: get(d, n); tm = t * 1e3
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 5.6), sharex=True)
    ax[0].plot(tm, g('V(out)')); ax[0].set_ylabel('V$_{OUT}$ [V]')
    ax[1].plot(tm, g('I(L1)'), lw=.5, label='I$_L$'); ax[1].plot(tm, g('I(Rload)'), label='I$_{OUT}$'); ax[1].axhline(7.88, ls='--', c='k', lw=.8, label='I$_{LIM}$ 7.88 A'); ax[1].set_ylabel('[A]'); ax[1].legend(fontsize=7)
    ax[2].plot(tm, g('V(ith)'), label='ITH'); ax[2].set_ylabel('[V]'); ax[2].set_xlabel('t [ms]'); ax[2].legend(fontsize=7)
    fig.suptitle('Overload: R$_{LOAD}$ 2.4 Ω → 0.5 Ω (7–10 ms), V$_{IN}$ = 24 V'); save('fault.png')
    w = (t > 8.5e-3) & (t < 10e-3)
    C['fault'] = dict(Iout_avg=float(raw.avg(t, g('I(Rload)'), 8.5e-3, 10e-3)), IL_pk=float(g('I(L1)')[(t > 7e-3) & (t < 10e-3)].max()),
                      Vout_avg=float(raw.avg(t, g('V(out)'), 8.5e-3, 10e-3)), Vout_over_recovery=float(g('V(out)')[t > 10e-3].max() - 12))

# ---------- FRA
import importlib.util
spec = importlib.util.spec_from_file_location('fra', r'..\..\simulation\ltspice_RevF1_runs\fra.py'); fra = importlib.util.module_from_spec(spec); spec.loader.exec_module(fra)
fig, ax = plt.subplots(2, 1, figsize=(7.2, 5), sharex=True); C['fra'] = {}
for v in (20, 24, 36, 48):
    fn = f'fra{v}.fra'
    if not os.path.exists(fn): fn = f'fra{v}.fra.raw'
    if not os.path.exists(fn): continue
    o = fra.analyse(fn); tb = np.array(o['table'])
    ax[0].semilogx(tb[:, 0], tb[:, 1], 'o-', ms=3, label=f'{v} V'); ax[1].semilogx(tb[:, 0], ((tb[:, 2] + 180) % 360) - 180, 'o-', ms=3)
    C['fra'][v] = {k: o.get(k) for k in ('fc_Hz', 'PM_deg', 'GM_dB', 'GM_lower_bound_dB')}
ax[0].axhline(0, c='k', lw=.8); ax[0].set_ylabel('|T| [dB]'); ax[0].legend(fontsize=7)
ax[1].set_ylabel('Phase [°]'); ax[1].set_xlabel('f [Hz]'); ax[1].axhline(0, c='k', lw=.8)
fig.suptitle('Loop gain (LTspice FRA, switching model, 60 W)'); save('bode.png')
json.dump(C, open(os.path.join(OUT, 'circuit.json'), 'w'), indent=1, default=float)
print(json.dumps(C, indent=1, default=float))
