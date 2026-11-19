"""Plot steady-state waveforms of EE463_Buck_RevF2.asc (run it in LTspice first) -> reports/figures/ss_waveforms_24V_60W.png
and print V_out, ripple, efficiency in the last 2 ms."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ltspice_RevF1_runs'))
from ltraw_measure import read_raw

d = read_raw(os.path.join(HERE, 'EE463_Buck_RevF2.raw'))
t = d['time']; k = {n.lower(): n for n in d}
g = lambda n: d[k[n.lower()]]
m = t >= t[-1] - 2e-3
tt = t[m]
avg = lambda y: np.trapezoid(y[m], tt) / (tt[-1] - tt[0])
vout = g('V(out)'); il = g('I(L1)'); sw = g('V(sw)'); vin = g('V(source)'); iin = -g('I(V1)')
pin = avg(vin * iin); pout = avg(vout * g('I(Rload)'))
print(f'Vout {avg(vout):.4f} V, ripple {1e3 * (vout[m].max() - vout[m].min()):.1f} mVpp, Pout {pout:.2f} W, '
      f'Pin {pin:.2f} W, eff {100 * pout / pin:.2f} %, IL pk {il[m].max():.2f} A')
w = (t >= t[-1] - 50e-6)
fig, ax = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
ax[0].plot((t[w] - t[w][0]) * 1e6, vout[w], color='#1f77b4'); ax[0].set_ylabel('V_OUT (V)')
ax[1].plot((t[w] - t[w][0]) * 1e6, il[w], color='#d62728'); ax[1].set_ylabel('I_L1 (A)')
ax[2].plot((t[w] - t[w][0]) * 1e6, sw[w], color='#2ca02c'); ax[2].set_ylabel('V_SW (V)'); ax[2].set_xlabel('time (us)')
ax[0].set_title('RevF2 drawn LTspice schematic, 24 V / 60 W, steady state (simulation)')
for a in ax:
    a.grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(HERE, '..', '..', 'reports', 'figures', 'ss_waveforms_24V_60W.png')
fig.savefig(out, dpi=150)
print('saved', out)
