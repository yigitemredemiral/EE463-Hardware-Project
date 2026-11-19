"""Hand (small-signal) model of the RevF1 voltage loop: LTC3895 peak-current-mode buck.
T(s) = Hdiv * gm/Y_ith(s) * Gi*Fh(s) * Zout(s)
 - Hdiv   = RFB_bot/(RFB_top+RFB_bot) = 10k/150k
 - gm     = error amplifier transconductance (LTC3895 datasheet: 2 mS)
 - Y_ith  = admittance seen by the ITH pin: (RITH + CITH) || CITHP || the external current-limit branch
            (CERR 10n + RERR 20k to the CS node, RCS 2k || CCS 10n). The CC op-amp is saturated and its clamp diode
            is off in normal operation, so that branch is passive, but the CS node carries 0.08 V/A of inductor
            current, which feeds back into ITH (kcs term).
 - Gi     = ITH-to-inductor-current gain (A/V) = 1/(Acs*Rsense); calibrated against the LTspice FRA
 - Fh     = sampling (subharmonic) double pole at fsw/2 with quality factor Q
 - Zout   = Rload || (ESR + 1/sC), C = 2 x 330 uF, ESR = 10 mOhm total
"""
import numpy as np
P = dict(gm=2e-3, Hdiv=10/150, C=660e-6, esr=10e-3, fsw=94.3e3, Gi=14.0, Q=0.6,
         Rerr=20e3, Cerr=10e-9, Rcs=2e3, Ccs=10e-9, Kcs=4e-3/100, td=0.0)
COMP = {'A': (8.2e3, 27e-9, 470e-12), 'B': (3.9e3, 68e-9, 1e-9), 'D5E1': (10e3, 22e-9, 470e-12),
        'oldB': (10e3, 33e-9, 470e-12)}

def loop(f, comp, Rload=2.4, **kw):
    p = dict(P, **kw); s = 2j*np.pi*np.asarray(f, float)
    R, C1, C2 = COMP[comp] if isinstance(comp, str) else comp
    Zcs = p['Rcs']/(1 + s*p['Rcs']*p['Ccs'])
    Zb = p['Rerr'] + 1/(s*p['Cerr']) + Zcs
    wn = np.pi*p['fsw']
    Fh = np.exp(-s*p['td'])/(1 + s/(wn*p['Q']) + (s/wn)**2)
    Yith = 1/(R + 1/(s*C1)) + s*C2 + (1 - p['Kcs']*Zcs*p['Gi']*Fh)/Zb
    Zc = p['esr'] + 1/(s*p['C'])
    Zout = Rload*Zc/(Rload + Zc)
    return p['Hdiv']*p['gm']/Yith*p['Gi']*Fh*Zout

def margins(comp, Rload=2.4, **kw):
    f = np.logspace(2, np.log10(45e3), 4000); T = loop(f, comp, Rload, **kw)
    mag = 20*np.log10(abs(T)); ph = np.degrees(np.unwrap(np.angle(T))) + 180
    k = np.flatnonzero((mag[:-1] > 0) & (mag[1:] <= 0))[0]
    j = np.flatnonzero((ph[:-1] > 0) & (ph[1:] <= 0))
    return f[k], ph[k], (-mag[j[0]] if len(j) else float('nan'))

if __name__ == '__main__':
    for c in ('D5E1', 'oldB', 'A', 'B'):
        print(c, 'fc %.0f Hz  PM %.1f deg  GM %.1f dB' % margins(c))
