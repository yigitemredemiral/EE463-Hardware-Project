"""Generate the drawn LTspice schematic of the final design (simulation/ltspice_RevF2/EE463_Buck_RevF2.asc).

Same circuit as the RevF1 simulation netlists (configuration G: VDMOS MOSFET models, LM74700-Q1 behavioural model,
compensation A, CRUN, 3 x 100 nF hot-loop capacitors) with the final RevF1 values (RFREQ 24.3k, RGH 4.7 Ohm).
Model-only parasitics (cable/board inductance, gate-loop inductance, trace resistance) are drawn too and marked.
Check: python tools/gen_asc.py --check  (LTspice -netlist on the .asc, compared with the RevF1 netlist topology)."""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'simulation', 'ltspice_RevF2')
LT = r'C:\Program Files\ADI\LTspice\LTspice.exe'
G = 16
PINS = {'res': {1: (16, 16), 2: (16, 96)}, 'cap': {1: (16, 0), 2: (16, 64)}, 'ind': {1: (16, 16), 2: (16, 96)},
        'voltage': {1: (0, 16), 2: (0, 96)}, 'nmos': {'D': (48, 0), 'G': (0, 80), 'S': (48, 96)},
        'schottky': {1: (16, 0), 2: (16, 64)}, 'bi': {1: (0, 0), 2: (0, 80)}, 'fra': {1: (0, -64), 2: (0, 0)},
        'LT6105': {6: (-96, -32), 1: (-96, 32), 4: (96, 0), 5: (96, 32), 2: (0, -96), 3: (0, 96)},
        'LT1636': {1: (-96, -32), 2: (-96, 32), 5: (96, 0), 3: (0, -96), 4: (-32, 96), 6: (32, 96)},
        'LT6654': {2: (-96, 0), 3: (96, 0), 1: (0, 96)},
        'LTC3895': {}}


def ltc3895_pins():
    t = open(os.path.join(HERE, '..', 'simulation', 'ltspice_RevF2', 'LTC3895.asy'), encoding='latin-1').read()
    out = {}
    for m in re.finditer(r'PIN (-?\d+) (-?\d+) \w+ \d+\s+PINATTR PinName (\S+)\s+PINATTR SpiceOrder (\d+)', t):
        out[m.group(3)] = (int(m.group(1)), int(m.group(2)))
    return out


def rot(p, r):
    x, y = p
    return {'R0': (x, y), 'R90': (-y, x), 'R180': (-x, -y), 'R270': (y, -x), 'M0': (-x, y)}[r]


class Asc:
    def __init__(self):
        self.items, self.wires, self.flags, self.texts, self.pos = [], [], [], [], {}

    def sym(self, kind, name, value, p1, r='R0', pin=None, extra=()):
        """place symbol so that its pin `pin` (default first pin) lands on point p1"""
        pins = PINS[kind]
        pin = pin if pin is not None else next(iter(pins))
        off = rot(pins[pin], r)
        org = (p1[0] - off[0], p1[1] - off[1])
        self.items.append((kind, name, value, org, r, extra))
        self.pos[name] = (kind, org, r)
        return org

    def pin(self, name, pin):
        kind, org, r = self.pos[name]
        o = rot(PINS[kind][pin], r)
        return (org[0] + o[0], org[1] + o[1])

    def w(self, *pts):
        for a, b in zip(pts, pts[1:]):
            assert a[0] == b[0] or a[1] == b[1], (a, b)
            if a != b:
                self.wires.append((a, b))
        return pts[-1]

    def flag(self, p, name):
        self.flags.append((p, name))

    def gnd(self, p):
        self.flags.append((p, '0'))

    def text(self, x, y, s, size=2):
        self.texts.append((x, y, s, size))

    # two-pin helpers: vertical with pin 1 on top / horizontal with pin 1 on the left
    def v(self, kind, name, value, top, flip=False):
        if flip:
            return self.sym(kind, name, value, top, 'R180', pin=2 if kind != 'cap' else 2) and None
        self.sym(kind, name, value, top, 'R0', pin=1)
        return self.pin(name, 2)

    def h(self, kind, name, value, left):
        self.sym(kind, name, value, left, 'R270', pin=1)
        return self.pin(name, 2)


def build():
    a = Asc()
    PINS['LTC3895'] = ltc3895_pins()
    T = a.text
    # ---------------- input: source, LM74700-Q1 ideal diode (behavioural), board inductance, input capacitors
    T(-64, -400, ';1  INPUT: lab supply -> LM74700-Q1 ideal diode (Q3) -> input capacitors', 3)
    a.sym('voltage', 'V1', '{VIN}', (0, 0), pin=1)
    a.gnd(a.pin('V1', 2)); a.flag((0, 0), 'SOURCE')
    e = a.h('res', 'Rsource', '50m', (0, 0))                    # supply output resistance (model)
    # UNPROTECTED (= ANODE side) line
    a.sym('nmos', 'MQ3', 'BSC026N08NS5', (352, 0), 'R90', pin='S')
    s, d, g = a.pin('MQ3', 'S'), a.pin('MQ3', 'D'), a.pin('MQ3', 'G')
    a.w(e, (128, 0), (192, 0), (256, 0), (320, 0), s)
    a.flag((128, 0), 'UNPROTECTED')
    a.sym('bi', 'Biq', 'I=80u*0.5*(1+tanh((V(UNPROTECTED)-3.9)/0.2))', (192, 0), 'R0', pin=1)
    a.gnd(a.pin('Biq', 2))
    a.sym('bi', 'Bid', 'I=en_fw()*(max(ireg(),0)*0.5*(1-tanh((V(GRP,UNPROTECTED)-{VCLAMP})/0.1))+min(ireg(),0)) - (1-en_fw())*V(GRP,UNPROTECTED)/5',
          (256, 0), 'R180', pin=1)
    a.sym('res', 'RgLeak', '10Meg', (320, -96), 'R0', pin=1)
    a.w(a.pin('RgLeak', 2), (320, 0))
    top = a.pin('Bid', 2)
    a.w(top, (256, -96), (320, -96), (g[0], -96), g)
    a.flag((g[0], -96), 'GRP')
    T(32, -224, ';U5 LM74700-Q1 (behavioural): 20 mV forward regulation, -11 mV fast reverse turn-off, 11 mA gate pump', 2)
    # board inductance after Q3 (drain = converter side)
    a.w(d, (480, 0)); a.flag((480, 0), 'CABLE')
    e = a.h('ind', 'Lcable', '200n Rser=5m', (480, 0))
    IN = 0
    a.w(e, (1232, IN)); a.flag((592, IN), 'IN')
    a.sym('schottky', 'DVIN1', 'BAT46WJ', (624, IN), 'R180', pin=2); a.gnd(a.pin('DVIN1', 1))
    a.v('cap', 'CINcer', '10u Rser=3m Lser=1n', (720, IN)); a.gnd((720, 64))
    a.v('cap', 'CINbulk', '300u Rser=28m Lser=2.7n', (816, IN)); a.gnd((816, 64))
    T(560, 160, ';CINcer = 10 x 2.2u X7R (DC-bias derated to 10u), CINbulk = 3 x 100u', 2)
    T(560, 192, ';Lcable / Lloop / Rtrace / LgH / LgL: PCB and wiring parasitics (model only)', 2)
    # ---------------- power stage
    T(1200, -400, ';2  POWER STAGE: Q1/Q2 synchronous buck, L1 33u, RS1 4m shunt, COUT 2 x 330u', 3)
    e = a.h('ind', 'Lloop', '5n Rser=2m', (1232, IN))
    a.w(e, (1488, IN)); a.flag((1360, IN), 'QD')
    a.v('cap', 'CHF', '300n Rser=10m Lser=1n', (1392, IN)); a.gnd((1392, 64))
    a.sym('nmos', 'MQ1', 'BSC040N08NS5', (1488, IN), 'R0', pin='D')
    a.sym('nmos', 'MQ2', 'BSC026N08NS5', (1488, 192), 'R0', pin='D')
    a.gnd(a.pin('MQ2', 'S'))
    SW = 160
    a.w(a.pin('MQ1', 'S'), (1488, SW), a.pin('MQ2', 'D'))
    a.w((1488, SW), (1584, SW), (1680, SW), (1776, SW))
    a.flag((1584, SW), 'SW')
    # gate drive (TG -> RGH1 -> LgH -> GH, RGSH1 GH-SW)
    q1g, q2g = a.pin('MQ1', 'G'), a.pin('MQ2', 'G')
    e = a.h('res', 'RGH1', '4.7', (1104, q1g[1])); a.flag((1104, q1g[1]), 'TG')
    a.flag(e, 'GHI'); e = a.h('ind', 'LgH', '5n Rser=10m', e)
    a.w(e, (1408, q1g[1]), q1g); a.flag((1408, q1g[1]), 'GH')
    a.sym('res', 'RGSH1', '100k', (1408, q1g[1]), 'R0', pin=1)
    b = a.pin('RGSH1', 2); a.w(b, (1440, b[1]), (1440, SW), (1488, SW))
    e = a.h('res', 'RGL1', '2.2', (1104, q2g[1])); a.flag((1104, q2g[1]), 'BG')
    a.flag(e, 'GLI'); e = a.h('ind', 'LgL', '5n Rser=10m', e)
    a.w(e, (1408, q2g[1]), q2g); a.flag((1408, q2g[1]), 'GL')
    a.sym('res', 'RGSL1', '100k', (1408, q2g[1]), 'R0', pin=1); a.gnd(a.pin('RGSL1', 2))
    # snubber, bootstrap
    a.sym('res', 'RSN1', '2.2', (1680, SW), 'R0', pin=1)
    p = a.pin('RSN1', 2); a.flag(p, 'SNUB')
    a.sym('cap', 'CSN1', '1n', p, 'R0', pin=1); a.gnd(a.pin('CSN1', 2))
    a.sym('cap', 'CBOOT1', '1u', (1584, SW), 'R180', pin=2)
    a.flag(a.pin('CBOOT1', 1), 'BOOST')
    # inductor, trace, shunt, output
    e = a.h('ind', 'L1', '33u Rser=20m', (1776, SW))
    a.flag(e, 'LOUT'); e = a.h('res', 'Rtrace', '3m', e)
    a.flag(e, 'SENSEP'); e = a.h('res', 'RS1', '4m', e)
    a.w(e, (2336, SW)); a.flag((2064, SW), 'OUT')
    a.v('cap', 'COUT', '330u x2 Rser=20m Lser=3n', (2128, SW)); a.gnd((2128, SW + 64))
    a.sym('res', 'Rload', 'R={if(TEST==1,table(time,0,RL,7m,RL,7.01m,RFAULT,10m,RFAULT,10.01m,RL),RL)}', (2240, SW), 'R0', pin=1)
    a.gnd(a.pin('Rload', 2))
    a.sym('fra', '@LOOP', 'fstart=500 fend=16k oct=1 delay=6m pp0=50m pp1=50m f0=1k f1=2k tsettle=1m tavgmin=2m nmax=1',
          (2336, SW), 'R0', pin=1)
    a.flag(a.pin('@LOOP', 2), 'FBOUT')
    T(1904, 384, ';Rload: 2.4 Ohm (60 W) or 1.6 Ohm (90 W); TEST=1 steps it to RFAULT (0.5 Ohm) at 7-10 ms', 2)
    T(1904, 416, ';@LOOP: LTspice FRA injection point (OUT -> FBOUT) for loop-gain measurement', 2)

    # ---------------- controller
    T(-64, 880, ';3  CONTROLLER LTC3895 (peak current mode, forced continuous, fsw 94.3 kHz)', 3)
    U = (768, 1600)
    a.items.append(('LTC3895', 'XU1', 'LTC3895', U, 'R0', ())); a.pos['XU1'] = ('LTC3895', U, 'R0')
    up = lambda n: a.pin('XU1', n)
    stub = {'OVLO': ('OVLO', -64, 0), 'Freq': ('FREQ', -64, 0), 'Pgood': ('PGOOD', -64, 0), 'Run': ('RUN', -64, 0),
            'Mode': ('INTVCC', -64, 0), 'CPump_EN': ('INTVCC', -64, 0), 'PhaseMD': ('INTVCC', -64, 0),
            'SS': ('SS', -64, 0), 'Ith': ('ITH', -64, 0), 'Sense+': ('SENSEP', 64, 0), 'Sense-': ('OUT', 64, 0),
            'Vfb': ('FB', 64, 0), 'DRVset': ('INTVCC', 64, 0), 'DRVUV': ('INTVCC', 64, 0), 'TG': ('TG', 64, 0),
            'SW': ('SW', 64, 0), 'Boost': ('BOOST', 64, 0), 'BG': ('BG', 64, 0), 'Vin': ('IN', 0, -64),
            'INTVcc': ('INTVCC', 0, -64), 'EXTVcc': ('OUT', 0, -64), 'DRVcc': ('DRVCC', 0, 64)}
    for pn, (net, dx, dy) in stub.items():
        p = up(pn); e = a.w(p, (p[0] + dx, p[1] + dy)); a.flag(e, net)
    for pn in ('PLLIN', 'GND'):
        p = up(pn); e = a.w(p, (p[0], p[1] + 64)) if pn == 'GND' else a.w(p, (p[0] - 64, p[1])); a.gnd(e)
    p = up('Ilim'); a.gnd(a.w(p, (p[0] + 64, p[1])))
    p, q = up('NDRV'), up('DRVcc'); a.w(p, (p[0], p[1] + 32), (q[0], q[1] + 32))
    T(1056, 2192, ';Vprg and CLKout open. NDRV tied to DRVCC (internal LDO). EXTVcc = OUT.', 2)
    # support networks
    x0, y0 = 1264, 1024
    def chain(x, y, items, label_top=None, gnd_end=True):
        if label_top:
            a.w((x, y - 32), (x, y)); a.flag((x, y - 32), label_top)
        p = (x, y)
        for kind, name, value, mid in items:
            if kind == 'res':
                a.sym('res', name, value, p, 'R0', pin=1); p = a.pin(name, 2)
            else:
                a.sym('cap', name, value, p, 'R0', pin=1); p = a.pin(name, 2)
            if mid:
                a.flag(p, mid)
        if gnd_end:
            a.gnd(p)
        return p
    chain(1376, 1024, [('res', 'RFBT1', '140k', 'FB'), ('res', 'RFBB1', '10k', None)], 'FBOUT')
    T(1312, 960, ';VOUT = 0.8*(1+140k/10k) = 12 V', 2)
    chain(1600, 1024, [('res', 'RITH1', '8.2k', 'COMP'), ('cap', 'CITH1', '27n', None)], 'ITH')
    a.w((1600, 1024), (1696, 1024)); chain(1696, 1024, [('cap', 'CITHP1', '470p', None)])
    T(1536, 960, ';compensation A (fitted). B = 3.9k / 68n / 1n', 2)
    chain(1856, 1024, [('cap', 'CSS1', '100n', None)], 'SS')
    chain(1984, 1024, [('res', 'RFREQ1', '24.3k', None)], 'FREQ')
    chain(1376, 1408, [('res', 'RRUNT1', '130k', 'RUN'), ('res', 'RRUNB1', '10k', None)], 'IN')
    a.w(a.pin('RRUNT1', 2), (1472, a.pin('RRUNT1', 2)[1])); chain(1472, a.pin('RRUNT1', 2)[1], [('cap', 'CRUN1', '1n', None)])
    chain(1600, 1408, [('res', 'ROVT1', '825k', 'OVLO'), ('res', 'ROVB1', '17.4k', None)], 'IN')
    chain(1760, 1408, [('res', 'RPG1', '511k', None)], 'INTVCC', gnd_end=False); a.flag(a.pin('RPG1', 2), 'PGOOD')
    chain(1888, 1408, [('cap', 'CSENSE1', '1n', None)], 'SENSEP', gnd_end=False); a.flag(a.pin('CSENSE1', 2), 'OUT')
    T(1312, 1344, ';RUN on at 16.8 V, OVLO 58.1 V', 2)
    a.w((1376, 1792), (1664, 1792)); a.w((1376, 1760), (1376, 1792)); a.flag((1376, 1760), 'INTVCC')
    chain(1472, 1792, [('cap', 'CINT1', '0.1u', None)])
    chain(1568, 1792, [('cap', 'CAUX1', '1u', None)])
    a.sym('schottky', 'DAUX1', 'BAT54', (1664, 1792), 'R180', pin=2); a.gnd(a.pin('DAUX1', 1))
    chain(1824, 1792, [('cap', 'CDRV1', '4.7u', None)], 'DRVCC')

    # ---------------- current-limit loop
    T(2240, 880, ';4  AVERAGE CURRENT LIMIT 7.88 A: LT6105 (gain 20) + LT6654 1.25 V + LT1636 integrator -> clamps ITH', 3)
    a.items.append(('LT6105', 'XU2', 'LT6105', (2560, 1184), 'R0', ())); a.pos['XU2'] = ('LT6105', (2560, 1184), 'R0')
    a.items.append(('LT1636', 'XU3', 'LT1636', (3104, 1184), 'R0', ())); a.pos['XU3'] = ('LT1636', (3104, 1184), 'R0')
    a.items.append(('LT6654', 'XU4', 'LT6654-1.25', (2560, 1600), 'R0', ())); a.pos['XU4'] = ('LT6654', (2560, 1600), 'R0')
    p = a.pin('XU2', 6); a.sym('res', 'RCSP1', '100', p, 'R90', pin=1); a.flag(a.pin('RCSP1', 2), 'SENSEP')
    a.flag(p, 'CSP')
    p = a.pin('XU2', 1); a.sym('res', 'RCSN1', '100', p, 'R90', pin=1); a.flag(a.pin('RCSN1', 2), 'OUT')
    a.flag(p, 'CSN')
    p = a.pin('XU2', 2); a.flag(a.w(p, (p[0], p[1] - 32)), 'INTVCC')
    a.gnd(a.pin('XU2', 3))
    cs = a.pin('XU2', 4)
    a.w(cs, (2720, cs[1]), (2816, cs[1]), (2896, cs[1])); a.flag((2720, cs[1]), 'CS')
    chain(2720, cs[1], [('res', 'RCSO1', '2k', None)])
    chain(2816, cs[1], [('cap', 'CCS1', '10n', None)])
    a.sym('res', 'RERR1', '20k', (2896, cs[1]), 'R270', pin=1)
    errn = a.pin('RERR1', 2)
    m = a.pin('XU3', 2)
    a.w(errn, (2992, errn[1]), (2992, m[1]), m); a.flag((2992, m[1]), 'ERRN')
    a.w((2992, errn[1]), (2992, 928))
    a.sym('cap', 'CERR1', '10n', (2992, 928), 'R90', pin=2)
    a.w((2992, 928), (2992, 864)); a.sym('res', 'RLEAK1', '10Meg', (2992, 864), 'R90', pin=2)
    a.w(a.pin('CERR1', 1), (3168, 928)); a.w(a.pin('RLEAK1', 1), (3168, 864), (3168, 928), (3232, 928))
    a.flag((3232, 928), 'ITH')
    a.flag(a.pin('XU3', 1), 'ILIMREF')
    p = a.pin('XU3', 3); a.flag(a.w(p, (p[0], p[1] - 32)), 'INTVCC')
    a.gnd(a.pin('XU3', 4)); a.gnd(a.pin('XU3', 6))
    o = a.pin('XU3', 5); a.flag(o, 'CCOUT')
    a.sym('res', 'RISO1', '150', o, 'R270', pin=1)
    k = a.pin('RISO1', 2); a.flag(k, 'CLAMPK')
    a.sym('schottky', 'DCL1', 'BAT54', k, 'R90', pin=2)
    a.flag(a.pin('DCL1', 1), 'ITH')
    p = a.pin('XU4', 2); a.flag(a.w(p, (p[0] - 32, p[1])), 'INTVCC')
    a.gnd(a.pin('XU4', 1))
    vr = a.pin('XU4', 3); a.w(vr, (2752, vr[1]), (2848, vr[1])); a.flag((2752, vr[1]), 'VREF')
    chain(2752, vr[1], [('cap', 'CREF1', '1u', None)])
    chain(2848, vr[1], [('res', 'RSETT1', '11.8k', 'ILIMREF'), ('res', 'RSETB1', '12k', None)])
    T(2240, 1984, ';I_lim = 1.25*12/23.8/(20*4m) = 7.88 A. U3 output sits at the rail until the limit is reached.', 2)

    # ---------------- directives
    D = ['.param VIN=24 RL=2.4 TEST=0 RFAULT=0.5', '.param IPUMP=11m VCLAMP=13',
         '.func ireg() limit(0.2*(V(UNPROTECTED,CABLE)-0.02), -{IPUMP}, {IPUMP})',
         '.func en_fw() 0.25*(1+tanh((V(UNPROTECTED)-3.9)/0.2))*(1+tanh((V(UNPROTECTED,CABLE)+0.011)/0.002))',
         '.model BSC026N08NS5 VDMOS(Rg=1.9 Vto=3.0 Rd=20u Rs=412u Rb=1.37m Kp=70 Lambda=0.03 Cgdmin=29p Cgdmax=1.18n A=0.2 Cgs=4.9n Cjo=1.39n M=0.75 Is=49.5p VJ=2.5 N=1.12 TT=15n ksubthres=.1 mfg=Infineon Vds=80 Ron=2.6m Qg=74n)',
         '.model BSC040N08NS5 VDMOS(Rg=1.1 Vto=3.0 Rd=31u Rs=634u Rb=2.11m Kp=40.6 Lambda=0.03 Cgdmin=17p Cgdmax=0.685n A=0.2 Cgs=2.84n Cjo=0.81n M=0.75 Is=28.7p VJ=2.5 N=1.12 TT=15n ksubthres=.1 mfg=Infineon_scaled_from_BSC026 Vds=80 Ron=4.0m Qg=43n)',
         '.model BAT46WJ D(Is=.1703u N=1.06 Rs=1.3 Cjo=35p Vj=.4 M=.5 Eg=.69 XTI=2 Iave=.25 Vpk=100 mfg=NXP type=Schottky)',
         '.lib models/LT6105.lib', '.lib models/LT1636.lib', '.lib models/LT6654-1.25.sub', '.lib models/RevD_diodes.lib',
         '.options plotwinsize=0 threads=1', '.tran 0 14m 0 100n',
         '.save V(OUT) V(SW) V(IN) V(SOURCE) V(ITH) V(CS) V(CCOUT) V(GH) V(GL) I(L1) I(V1) I(Rload) Id(MQ1) Id(MQ2)']
    for i, d in enumerate(D):
        T(-64, 2400 + 32 * i, '!' + d, 2)
    T(-64, 2336, ';Run: 14 ms transient at VIN / RL above (steady state after ~8 ms). Official Infineon models: replace the two VDMOS .model lines.', 2)
    return a


def write(a, path):
    L = ['Version 4', 'SHEET 1 3600 2900']
    for (x1, y1), (x2, y2) in a.wires:
        L.append(f'WIRE {x1} {y1} {x2} {y2}')
    for (x, y), n in a.flags:
        L.append(f'FLAG {x} {y} {n}')
    for kind, name, value, (x, y), r, extra in a.items:
        L.append(f'SYMBOL {kind} {x} {y} {r}')
        L.append(f'SYMATTR InstName {name}')
        L.append(f'SYMATTR Value {value}')
    for x, y, s, size in a.texts:
        L.append(f'TEXT {x} {y} Left {size} {s}')
    open(path, 'w', encoding='latin-1', newline='\n').write('\n'.join(L) + '\n')


def split_wires(a):
    pts = set()
    for w in a.wires:
        pts.update(w)
    for kind, name, value, org, r, extra in a.items:
        for pn in PINS[kind]:
            pts.add(a.pin(name, pn))
    pts.update(p for p, n in a.flags)
    out = []
    for p0, p1 in a.wires:
        inner = [p for p in pts if p not in (p0, p1) and (
            (p0[0] == p1[0] == p[0] and min(p0[1], p1[1]) < p[1] < max(p0[1], p1[1])) or
            (p0[1] == p1[1] == p[1] and min(p0[0], p1[0]) < p[0] < max(p0[0], p1[0])))]
        ch = sorted([p0, p1] + inner, key=lambda q: abs(q[0] - p0[0]) + abs(q[1] - p0[1]))
        out += list(zip(ch, ch[1:]))
    a.wires = out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a = build(); split_wires(a)
    write(a, os.path.join(OUT, 'EE463_Buck_RevF2.asc'))
    print('symbols', len(a.items), 'wires', len(a.wires), 'flags', len(a.flags))
