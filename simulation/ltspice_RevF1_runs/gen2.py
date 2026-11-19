"""RevF1 additions on top of gen.make: LM74700-Q1 behavioural ideal diode, current-limited lab supply,
reverse-polarity PWL source, FRA run. All edits are explicit replacements (asserted in gen.rep)."""
import gen

# LM74700-Q1 behavioural model (NOT a TI model): regulates ANODE-CATHODE to 20 mV with a
# current-limited charge pump, fast gate pull-down on reverse (Vac < -11 mV), VGS clamp, UVLO.
# Values from datasheet (see paket1_sonuclar.md); IPUMP/VCLAMP are parameters.
IDEAL = """MRP CABLE GRP UNPROTECTED BSC026N08NS5
Bid UNPROTECTED GRP I=en_fw()*(max(ireg(),0)*0.5*(1-tanh((V(GRP,UNPROTECTED)-{VCLAMP})/0.1))+min(ireg(),0)) - (1-en_fw())*V(GRP,UNPROTECTED)/5
.func ireg() limit(0.2*(V(UNPROTECTED,CABLE)-0.02), -{IPUMP}, {IPUMP})
.func en_fw() 0.25*(1+tanh((V(UNPROTECTED)-3.9)/0.2))*(1+tanh((V(UNPROTECTED,CABLE)+0.011)/0.002))
RgLeak GRP UNPROTECTED 10Meg
Biq UNPROTECTED 0 I=80u*0.5*(1+tanh((V(UNPROTECTED)-3.9)/0.2))
.param IPUMP=11m VCLAMP=13
"""
# v2 (2026-11-11): same characteristic as v1 (20 mV forward regulation, 11 mA pump, -11 mV reverse turn-off,
# 13 V VGS clamp, 3.9 V UVLO, 80 uA IQ) but every transition is smoothed with tanh so the source has no
# discontinuity; v1 (hard if()) made the solver crawl when VIN ramped from 0 or stepped away from the prime state.

def ideal_diode():
    return [('DrevA UNPROTECTED CABLE RBQ20NS100A 2\n', IDEAL),
            ('DrevB UNPROTECTED CABLE RBQ20NS100A 2\n', ''),
            ('I(DrevA) I(DrevB)', 'I(MRP) V(GRP)')]

def lab_supply(ilim, csup='220u', ramp='2m'):
    return [('V1 SOURCE 0 {VIN}\n',
             f'V1 SRCI 0 PWL(0 0 {ramp} {{VIN}})\nBsup SRCI SOURCE I=min({ilim}, max(0, V(SRCI,SOURCE)/10m))\n'
             f'Csup SOURCE 0 {csup} Rser=20m\n')]

def reverse_then_forward(vneg=-48, vpos=24):
    return [('V1 SOURCE 0 {VIN}\n',
             f'V1 SOURCE 0 PWL(0 0 0.5m {vneg} 3m {vneg} 3.5m 0 5m 0 6m {vpos})\n')]

def fra_line(fstart=500, fend=50000):
    return [('@LOOP OUT FBOUT fstart=500 fend=16k oct=1 delay=6m pp0=50m pp1=50m f0=1k f1=2k tsettle=1m tavgmin=2m nmax=1',
             f'@LOOP OUT FBOUT fstart={fstart} fend={fend} oct=2 delay=1m pp0=40m pp1=15m f0=2k f1=10k tsettle=1m tavgmin=1m nmax=1')]
