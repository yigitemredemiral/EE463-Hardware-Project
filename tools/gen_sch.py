"""Generate the readable RevF2 schematic (hardware/kicad_RevF2/EE463_Buck_RevF2.kicad_sch).

Input : the RevF1 schematic (same symbols, same symbol UUIDs -> the PCB link is kept).
Output: one A2 sheet drawn with real wires: input/protection, power stage, controller, current-limit loop and test
        points. Wires connect the parts inside a block; net labels connect the blocks (as a person would draw it).
Fields: Value / Footprint / MPN / Manufacturer / Datasheet come from tools/parts.py and the final PCB.
Check : python tools/kinet.py old.net new.net  (connectivity must be IDENTICAL; run_checks.sh does it).
Usage : python tools/gen_sch.py <RevF1.kicad_sch> <final.kicad_pcb> <out.kicad_sch>"""
import math, os, re, sys, uuid
from sx import parse, dump, Q, find, first, num
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts import PARTS

PROJECT = 'EE463_Buck_RevF2'
CCATH_UUID = '6f0c2a1e-5b7d-4c11-9a3e-2d8b4e7f1c01'
LEFT_FIELDS = {'CVCAP1', 'CCATH1', 'RRUNB1', 'CBOOT1'}
POWER_LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hardware', 'kicad_RevF2', 'libraries', 'symbols', 'power.kicad_sym')
U = lambda: Q(str(uuid.uuid4()))
R = lambda v: round(v, 4)


class Sheet:
    def __init__(self, src):
        self.root = parse(open(src, encoding='utf-8').read())
        self.lib = first(self.root, 'lib_symbols')
        self.syms = {self.prop(s, 'Reference'): s for s in find(self.root, 'symbol')}
        # RevF2 addition: CCATH1 (1 uF / 100 V, VIN-GND at the Q3 drain), cloned from CVCAP1 with a fixed UUID
        import copy
        c = copy.deepcopy(self.syms['CVCAP1'])
        for node in c:
            if isinstance(node, list) and node[0] == 'uuid':
                node[1] = Q(CCATH_UUID)
            if isinstance(node, list) and node[0] == 'pin':
                first(node, 'uuid')[1] = U()
            if isinstance(node, list) and node[0] == 'property' and node[1] == 'Reference':
                node[2] = Q('CCATH1')
        for inst in find(c, 'instances'):
            for pr in find(inst, 'project'):
                for pa in find(pr, 'path'):
                    first(pa, 'reference')[1] = Q('CCATH1')
        self.syms['CCATH1'] = c
        self.root.append(c)
        self.path = find(first(first(next(iter(self.syms.values())), 'instances'), 'project'), 'path')[0][1]
        self.P, self.segs, self.labels, self.gnds, self.ncs, self.texts = {}, [], [], [], [], []

    @staticmethod
    def prop(sym, name):
        for p in find(sym, 'property'):
            if p[1] == name:
                return p[2]

    def libdef(self, lib_id):
        return next(s for s in find(self.lib, 'symbol') if s[1] == lib_id)

    def lib_pins(self, lib_id):
        out = {}

        def walk(n):
            for c in n:
                if isinstance(c, list) and c and c[0] in ('symbol',):
                    walk(c)
                elif isinstance(c, list) and c and c[0] == 'pin':
                    at = first(c, 'at'); out[first(c, 'number')[1]] = (float(at[1]), float(at[2]))
        walk(self.libdef(lib_id))
        return out

    # ---- placement / drawing primitives
    def put(self, ref, x, y, rot=0, mirror=None):
        self.P[ref] = (R(x), R(y), rot, mirror)

    def pin(self, ref, n):
        x, y, rot, mir = self.P[ref]
        lib = first(self.syms[ref], 'lib_id')[1]
        px, py = self.lib_pins(lib)[str(n)]
        lx, ly = px, -py
        if mir == 'x':
            ly = -ly
        elif mir == 'y':
            lx = -lx
        a = math.radians(rot)
        return (R(x + lx * math.cos(a) + ly * math.sin(a)), R(y - lx * math.sin(a) + ly * math.cos(a)))

    def w(self, *pts):
        pts = [(R(p[0]), R(p[1])) for p in pts]
        for a, b in zip(pts, pts[1:]):
            if a != b:
                assert a[0] == b[0] or a[1] == b[1], ('not orthogonal', a, b)
                self.segs.append((a, b))
        return pts[-1]

    def lab(self, name, p, ang=0):
        self.labels.append((name, R(p[0]), R(p[1]), ang))

    def gnd(self, p, rot=0):
        self.gnds.append((R(p[0]), R(p[1]), rot))

    def nc(self, ref, n):
        self.ncs.append(self.pin(ref, n))

    def text(self, s, x, y, size=1.27, bold=False):
        self.texts.append((s, x, y, size, bold))

    # ---- helpers for two-pin parts
    def vpart(self, ref, x, ytop, flip=False):
        """vertical; pin 1 on top (flip: pin 2 on top). Returns (top, bottom) pin points."""
        self.put(ref, x, ytop + 3.81, 180 if flip else 0)
        return (x, R(ytop)), (x, R(ytop + 7.62))

    def hpart(self, ref, xl, y, pin1_left=True):
        self.put(ref, xl + 3.81, y, 90 if pin1_left else 270)
        return (R(xl), y), (R(xl + 7.62), y)

    def stub_label(self, ref, n, name, dx=0, dy=0, ang=None):
        p = self.pin(ref, n); e = self.w(p, (p[0] + dx, p[1] + dy))
        if ang is None:
            ang = 180 if dx < 0 else 0
        self.lab(name, e, ang)
        return e

    def stub_gnd(self, ref, n, dx=0, dy=0, rot=None):
        p = self.pin(ref, n); e = self.w(p, (p[0] + dx, p[1] + dy))
        if rot is None:
            rot = 270 if dx < 0 else 90 if dx > 0 else 0
        self.gnd(e, rot)
        return e


def layout(s):
    T = s.text
    # ======================= 1  INPUT, REVERSE-POLARITY PROTECTION, INPUT FILTER ======================
    T('1  INPUT / REVERSE-POLARITY PROTECTION (LM74700-Q1 ideal diode) / INPUT FILTER', 25.4, 22.86, 2.0, True)
    Y = 60.96
    s.put('J1', 30.48, Y, 0, 'y')
    s.w(s.pin('J1', 2), (38.1, 63.5), (38.1, 66.04)); s.gnd((38.1, 66.04))
    s.put('Q3', 76.2, 58.42, 270)
    s.put('U5', 76.2, 40.64, 0, 'x')
    s.w(s.pin('J1', 1), s.pin('Q3', 1))                                  # VIN_RAW line
    s.lab('VIN_RAW', (36.83, Y))
    s.vpart('CANODE1', 43.18, Y); s.gnd((43.18, Y + 7.62))
    s.w(s.pin('U5', 3), (50.8, s.pin('U5', 3)[1]), (50.8, Y))       # EN -> ANODE
    s.w(s.pin('U5', 1), (58.42, s.pin('U5', 1)[1]), (58.42, 41.91))   # VCAP
    s.vpart('CVCAP1', 58.42, 41.91); s.w((58.42, 49.53), (58.42, Y))
    s.lab('IDVCAP', (58.42, 40.64), 180)
    s.w(s.pin('U5', 6), (s.pin('U5', 6)[0], Y))                         # ANODE
    s.w(s.pin('U5', 5), s.pin('Q3', 4))                                 # GATE
    s.lab('IDGATE', (76.2, 52.07))
    s.w(s.pin('U5', 4), (s.pin('U5', 4)[0], Y))                         # CATHODE -> VIN
    g = s.pin('U5', 2); s.w(g, (g[0], 27.94), (88.9, 27.94), (88.9, 30.48)); s.gnd((88.9, 30.48))
    T('Q3 source = connector side, drain = converter side. EN tied to ANODE.', 25.4, 86.36)
    T('No TVS: LM74700 ANODE abs. max 65 V (see docs).', 25.4, 90.17)
    # VIN line and input capacitors
    xs = [93.98 + 12.7 * k for k in range(14)]
    s.w(s.pin('Q3', 5), (314.96, Y))
    s.lab('VIN', (86.36, Y))
    s.put('DVIN1', xs[0], Y + 3.81, 270); s.gnd((xs[0], Y + 7.62))
    s.vpart('CCATH1', 88.9, Y); s.gnd((88.9, Y + 7.62))
    for x, ref in zip(xs[1:], ['CINB1', 'CINB2', 'CINB3'] + [f'CIN{i}' for i in range(1, 11)]):
        s.vpart(ref, x, Y); s.gnd((x, Y + 7.62))
    T('10 x 2.2 uF / 100 V X7R 1210 + 3 x 100 uF / 100 V electrolytic', 104.14, 81.28)

    # ======================= 2  POWER STAGE ======================
    T('2  SYNCHRONOUS BUCK POWER STAGE', 248.92, 22.86, 2.0, True)
    s.put('Q1', 279.4, 71.12); s.put('Q2', 279.4, 86.36)
    s.w(s.pin('Q1', 5), (281.94, Y))
    for i, x in enumerate((289.56, 302.26, 314.96)):
        s.vpart(f'CHF{i + 1}', x, Y); s.gnd((x, Y + 7.62))
    SW = 78.74
    s.w(s.pin('Q1', 1), (281.94, SW), s.pin('Q2', 5))
    s.put('L1', 330.2, SW, 90)
    s.w((271.78, SW), s.pin('L1', 1))
    s.lab('SW', (283.21, SW))
    s.stub_gnd('Q2', 1, dy=2.54)
    # gate drive
    s.hpart('RGH1', 257.81, 71.12); s.w(s.pin('RGH1', 2), s.pin('Q1', 4))
    s.stub_label('RGH1', 1, 'TG', dx=-2.54)
    s.lab('GH', (266.7, 71.12))
    s.vpart('RGSH1', 271.78, 71.12)
    s.hpart('RGL1', 257.81, 86.36); s.w(s.pin('RGL1', 2), s.pin('Q2', 4))
    s.stub_label('RGL1', 1, 'BG', dx=-2.54)
    s.lab('GL', (266.7, 86.36))
    s.vpart('RGSL1', 271.78, 86.36); s.gnd((271.78, 93.98))
    # snubber, bootstrap
    s.vpart('RSN1', 304.8, SW); s.w((304.8, 86.36), (304.8, 88.9)); s.lab('SNUB', (304.8, 87.63))
    s.vpart('CSN1', 304.8, 88.9); s.gnd((304.8, 96.52))
    s.vpart('CBOOT1', 320.04, 71.12); s.w((320.04, 71.12), (320.04, 68.58)); s.lab('BOOST', (320.04, 68.58))
    # inductor, shunt, output
    s.put('RS1', 345.44, SW, 90)
    s.w(s.pin('L1', 2), s.pin('RS1', 1)); s.lab('SENSEP', (335.28, SW))
    VO = s.pin('RS1', 2)
    s.w(VO, (393.7, SW)); s.lab('VOUT', (351.79, SW))
    for x, ref in ((360.68, 'COUT1'), (370.84, 'COUT2')):
        s.vpart(ref, x, SW); s.gnd((x, SW + 7.62))
    s.put('J2', 398.78, SW)
    s.w(s.pin('J2', 2), (391.16, 81.28), (391.16, 83.82)); s.gnd((391.16, 83.82))
    s.put('J3', 398.78, 93.98)
    s.w((381.0, SW), (381.0, 93.98), s.pin('J3', 1))
    s.w(s.pin('J3', 2), (391.16, 96.52), (391.16, 99.06)); s.gnd((391.16, 99.06))
    T('Hot loop Q1-Q2-CHF1..3 must be very short. RS1: Kelvin pickup at the pads.', 248.92, 109.22)
    T('J3: optional 12 V fan (DNP). Fan power counts in the efficiency.', 248.92, 113.03)
    T('fsw = 94.3 kHz (RFREQ 24.3k). L1 33 uH. COUT 2 x 330 uF polymer.', 248.92, 116.84)

    # ======================= 3  CONTROLLER ======================
    T('3  CONTROLLER LTC3895 (peak current mode) / SELF-SUPPLIED GATE DRIVE', 25.4, 142.24, 2.0, True)
    s.put('U1', 127.0, 190.5)
    L = {1: 'OVLO', 3: 'SENSEP', 4: 'VOUT', 5: 'SS', 6: 'FB', 7: 'ITH', 8: 'INTVCC', 10: 'INTVCC', 14: 'PGOOD'}
    for n, name in L.items():
        s.stub_label('U1', n, name, dx=-5.08)
    for n in (2, 11, 16):
        s.nc('U1', n)
    s.stub_gnd('U1', 9, dx=-2.54)
    a = s.pin('U1', 12); b = s.pin('U1', 13)
    s.w(a, (a[0] - 2.54, a[1]), (b[0] - 2.54, b[1]), b); s.gnd((a[0] - 2.54, a[1]), 270)
    s.stub_gnd('U1', 15, dx=-2.54)
    Rt = {17: 'FREQ', 18: 'INTVCC', 19: 'INTVCC', 20: 'TG', 21: 'SW', 22: 'BOOST', 24: 'BG', 26: 'DRVCC', 30: 'VIN',
          32: 'VOUT', 34: 'RUN', 36: 'INTVCC', 38: 'INTVCC'}
    for n, name in Rt.items():
        s.stub_label('U1', n, name, dx=5.08)
    p = s.pin('U1', 28); s.w(p, (p[0] + 2.54, p[1]), (p[0] + 2.54, s.pin('U1', 26)[1]))   # NDRV tied to DRVCC
    s.stub_gnd('U1', 37, dx=2.54)
    s.stub_gnd('U1', 39, dx=2.54)
    T('MODE = INTVCC: forced continuous. VPRG open: VFB = 0.8 V. ILIM = GND. DRVSET = INTVCC: DRVCC = 10 V.', 25.4, 231.14)
    T('EXTVCC = VOUT (12 V): no external auxiliary supply. NDRV tied to DRVCC (internal LDO).', 25.4, 234.95)
    T('GND pins 9/12/15/39 connected. Missing high-voltage pins of the FE38 package have no pad.', 25.4, 238.76)

    # clusters (left of U1)
    def chain_top(ref, x, ytop, label):
        s.w((x, ytop), (x, ytop - 2.54)); s.lab(label, (x, ytop - 2.54))
    x = 30.48                                          # FB divider
    s.vpart('RFBT1', x, 160.02); chain_top('RFBT1', x, 160.02, 'VOUT')
    s.w((x, 167.64), (x, 170.18)); s.lab('FB', (x, 168.91))
    s.vpart('RFBB1', x, 170.18); s.gnd((x, 177.8))
    T('VOUT = 0.8 V x (1 + 140k/10k) = 12.0 V', 25.4, 186.69)
    x = 48.26                                          # compensation A
    s.vpart('RITH1', x, 160.02); chain_top('RITH1', x, 160.02, 'ITH')
    s.w((x, 160.02), (60.96, 160.02))
    s.vpart('CITHP1', 60.96, 160.02); s.gnd((60.96, 167.64))
    s.w((x, 167.64), (x, 170.18)); s.lab('COMP', (x, 168.91))
    s.vpart('CITH1', x, 170.18); s.gnd((x, 177.8))
    T('Comp. A: 8.2k / 27n / 470p (fitted)', 40.64, 190.5)
    T('Comp. B: 3.9k / 68n / 1n (transient test)', 40.64, 194.31)
    x = 76.2                                           # soft start
    s.vpart('CSS1', x, 160.02); chain_top('CSS1', x, 160.02, 'SS'); s.gnd((x, 167.64))
    x = 91.44                                          # frequency
    s.vpart('RFREQ1', x, 160.02); chain_top('RFREQ1', x, 160.02, 'FREQ'); s.gnd((x, 167.64))
    x = 30.48                                          # RUN divider
    s.vpart('RRUNT1', x, 205.74); chain_top('RRUNT1', x, 205.74, 'VIN')
    s.w((x, 213.36), (x, 215.9)); s.lab('RUN', (x, 214.63))
    s.w((x, 215.9), (38.1, 215.9))
    s.vpart('RRUNB1', x, 215.9); s.gnd((x, 223.52))
    s.vpart('CRUN1', 38.1, 215.9); s.gnd((38.1, 223.52))
    x = 55.88                                          # OVLO divider
    s.vpart('ROVT1', x, 205.74); chain_top('ROVT1', x, 205.74, 'VIN')
    s.w((x, 213.36), (x, 215.9)); s.lab('OVLO', (x, 214.63))
    s.vpart('ROVB1', x, 215.9); s.gnd((x, 223.52))
    T('RUN on at 16.8 V; OVLO 58.1 V nom.', 25.4, 200.66)
    x = 71.12                                          # PGOOD pull-up
    s.vpart('RPG1', x, 205.74); chain_top('RPG1', x, 205.74, 'INTVCC')
    s.w((x, 213.36), (x, 215.9)); s.lab('PGOOD', (x, 215.9))
    x = 83.82                                          # sense filter
    s.vpart('CSENSE1', x, 205.74); chain_top('CSENSE1', x, 205.74, 'SENSEP')
    s.w((x, 213.36), (x, 215.9)); s.lab('VOUT', (x, 215.9))

    # clusters (right of U1)
    s.w((175.26, 160.02), (203.2, 160.02)); s.w((175.26, 160.02), (175.26, 157.48)); s.lab('INTVCC', (175.26, 157.48))
    s.vpart('CINT1', 175.26, 160.02); s.gnd((175.26, 167.64))
    s.vpart('CAUX1', 187.96, 160.02); s.gnd((187.96, 167.64))
    s.put('DAUX1', 203.2, 168.91, 90)
    s.gnd(s.w(s.pin('DAUX1', 1), (s.pin('DAUX1', 1)[0], s.pin('DAUX1', 1)[1] + 2.54)))
    s.nc('DAUX1', 2)
    s.vpart('CDRV1', 220.98, 160.02); chain_top('CDRV1', 220.98, 160.02, 'DRVCC'); s.gnd((220.98, 167.64))
    T('INTVCC 5 V / DRVCC 10 V bypass', 172.72, 186.69)

    # ======================= 4  AVERAGE CURRENT LIMIT LOOP ======================
    T('4  AVERAGE CURRENT LIMIT (7.88 A nominal): LT6105 sense amp + LT6654 reference + LT1636 integrator', 233.68, 142.24, 2.0, True)
    s.put('U2', 261.62, 187.96)
    q = s.pin('U2', 1); s.w(q, (246.38, q[1]), (246.38, 176.53))
    s.hpart('RCSN1', 236.22, 176.53, pin1_left=True); s.w(s.pin('RCSN1', 2), (246.38, 176.53))
    s.lab('CSN', (246.38, 180.34))
    s.stub_label('RCSN1', 1, 'VOUT', dx=-2.54)
    s.stub_label('U2', 2, 'INTVCC', dx=-5.08)
    s.nc('U2', 3); s.nc('U2', 6); s.nc('U2', 7)
    g = s.pin('U2', 4); s.w(g, (g[0] - 2.54, g[1])); s.gnd((g[0] - 2.54, g[1]), 270)
    q = s.pin('U2', 8); s.w(q, (279.4, q[1]), (279.4, 195.58)); s.lab('CSP', (276.86, q[1]))
    s.vpart('RCSP1', 279.4, 195.58, flip=True); s.w((279.4, 203.2), (279.4, 205.74)); s.lab('SENSEP', (279.4, 205.74))
    CS = s.pin('U2', 5)[1]
    s.w(s.pin('U2', 5), (304.8, CS)); s.lab('CS', (290.83, CS))
    s.vpart('RCSO1', 287.02, CS); s.gnd((287.02, CS + 7.62))
    s.vpart('CCS1', 297.18, CS); s.gnd((297.18, CS + 7.62))
    s.hpart('RERR1', 304.8, CS, pin1_left=True)
    s.put('U3', 327.66, 185.42)
    s.w(s.pin('RERR1', 2), s.pin('U3', 2))
    s.w((312.42, CS), (312.42, 170.18), (316.23, 170.18)); s.lab('ERRN', (312.42, 177.8))
    s.hpart('CERR1', 316.23, 170.18, pin1_left=False)
    s.w((312.42, 170.18), (312.42, 162.56), (316.23, 162.56))
    s.hpart('RLEAK1', 316.23, 162.56, pin1_left=False)
    s.w((323.85, 162.56), (327.66, 162.56), (327.66, 170.18))
    s.w((323.85, 170.18), (332.74, 170.18)); s.lab('ITH', (332.74, 170.18))
    s.nc('U3', 1); s.nc('U3', 8)
    q = s.pin('U3', 3); s.w(q, (311.15, q[1]), (311.15, 231.14), (297.18, 231.14)); s.lab('ILIMREF', (311.15, 213.36))
    g = s.pin('U3', 4); s.w(g, (313.69, g[1]), (313.69, 193.04)); s.gnd((313.69, 193.04))
    s.stub_gnd('U3', 5, dx=5.08)
    s.hpart('RISO1', 347.98, 184.15, pin1_left=True); s.w(s.pin('U3', 6), s.pin('RISO1', 1)); s.lab('CCOUT', (341.63, 184.15))
    s.put('DCL1', 373.38, 184.15, 180)
    s.w(s.pin('RISO1', 2), s.pin('DCL1', 3)); s.lab('CLAMPK', (356.87, 184.15))
    s.stub_label('DCL1', 1, 'ITH', dx=5.08)
    s.nc('DCL1', 2)
    q = s.pin('U3', 7); s.w(q, (342.9, q[1]), (342.9, 193.04)); s.lab('INTVCC', (342.9, 193.04))
    s.put('U4', 271.78, 220.98)
    a, b = s.pin('U4', 1), s.pin('U4', 2)
    s.w(a, (256.54, a[1]), (256.54, b[1]), b); s.w((256.54, b[1]), (254.0, b[1])); s.gnd((254.0, b[1]), 270)
    s.nc('U4', 3); s.nc('U4', 5)
    s.stub_label('U4', 4, 'INTVCC', dx=5.08)
    s.w(s.pin('U4', 6), (297.18, 223.52)); s.lab('VREF', (290.83, 223.52))
    s.vpart('CREF1', 287.02, 223.52); s.gnd((287.02, 231.14))
    s.vpart('RSETT1', 297.18, 223.52)
    s.w((297.18, 231.14), (297.18, 233.68))
    s.vpart('RSETB1', 297.18, 233.68); s.gnd((297.18, 241.3))
    T('I_lim = VREF x RSETB/(RSETT+RSETB) / (20 x 4 mOhm) = 1.25 x 12/23.8 / 0.08 = 7.88 A', 233.68, 250.19)
    T('Normally inactive (U3 output at the rail, DCL1 off). In overload DCL1 pulls ITH down.', 233.68, 254.0)

    # ======================= 5  TEST POINTS / POWER FLAGS ======================
    T('5  TEST POINTS (copper pads) AND ERC POWER FLAGS', 25.4, 252.73, 2.0, True)
    names = {'TP1': 'VIN_RAW', 'TP2': 'VIN', 'TP3': 'GND', 'TP4': 'VOUT', 'TP5': 'SW', 'TP6': 'GH', 'TP7': 'GL', 'TP8': 'ITH',
             'TP9': 'SENSEP', 'TP10': 'FB', 'TP11': 'CS', 'TP12': 'ILIMREF', 'TP13': 'INTVCC', 'TP14': 'DRVCC',
             'TP15': 'PGOOD', 'TP16': 'RUN'}
    for i, (ref, net) in enumerate(names.items()):
        x = 30.48 + 12.7 * i
        s.put(ref, x, 264.16)
        if net == 'GND':
            s.w((x, 264.16), (x, 266.7)); s.gnd((x, 266.7))
        else:
            s.w((x, 264.16), (x, 266.7)); s.lab(net, (x, 266.7))
    for i, (ref, net) in enumerate({'#FLG01': 'VIN_RAW', '#FLG02': 'VIN', '#FLG03': 'GND', '#FLG04': 'VOUT'}.items()):
        x = 238.76 + 12.7 * i
        s.put(ref, x, 264.16)
        s.w((x, 264.16), (x, 266.7))
        s.gnd((x, 266.7)) if net == 'GND' else s.lab(net, (x, 266.7))


# --------------------------------------------------------------------------- output
def fields_for(s, ref, kind):
    x, y, rot, mir = s.P[ref]
    if kind == 'v':
        return (x + 2.032, y - 1.27, 'left'), (x + 2.032, y + 1.27, 'left')
    if kind == 'h':
        return (x, y - 2.54, None), (x, y + 2.54, None)
    if kind == 'ic':
        h = {'U1': 22.86, 'U2': 7.62, 'U3': 7.62, 'U4': 6.35}[ref]
        return (x, y - h, None), (x, y + h, None)
    if kind == 'u5':
        return (x + 10.16, y - 3.81, 'left'), (x + 10.16, y - 1.27, 'left')
    if kind == 'q':
        if rot == 270:
            return (x + 7.62, y - 6.35, 'left'), (x + 7.62, y - 3.81, 'left')
        return (x + 5.08, y + 2.54, 'left'), (x + 5.08, y + 5.08, 'left')
    if kind == 'j':
        return (x - 2.54, y - 2.54, None), (x - 2.54, y + 5.08, None)
    if kind == 'tp':
        return (x, y - 4.445, None), (x + 1.905, y + 1.905, 'left')
    if kind == 'flag':
        return (x, y + 2.54, None), (x, y - 4.445, None)
    if kind == 'd180':
        return (x, y - 3.81, None), (x, y + 3.81, None)
    return (x + 3.81, y - 1.27, 'left'), (x + 3.81, y + 1.27, 'left')


def eff(size=1.27, justify=None, hide=False, bold=False):
    e = ['effects', ['font', ['size', num(size), num(size)]] + ([['bold', 'yes']] if bold else [])]
    if justify:
        e.append(['justify', justify])
    if hide:
        e.append(['hide', 'yes'])
    return e


def pcb_footprints(pcb):
    t = open(pcb, encoding='utf-8').read()
    return {r: f for f, r in re.findall(r'\(footprint "([^"]+)".*?\(property "Reference" "([^"]+)"', t, re.S)}


def build(src, pcb, out):
    s = Sheet(src)
    layout(s)
    fps = pcb_footprints(pcb)
    missing = set(s.syms) - set(s.P)
    assert not missing, missing
    # ---- symbols
    out_syms = []
    for ref, sym in s.syms.items():
        x, y, rot, mir = s.P[ref]
        lib = first(sym, 'lib_id')[1]
        kind = ('v' if rot in (0, 180) else 'h') if lib in ('Device:R', 'Device:C', 'Device:C_Polarized', 'Device:L') else \
            'ic' if ref in ('U1', 'U2', 'U3', 'U4') else 'u5' if ref == 'U5' else 'q' if ref.startswith('Q') else \
            'j' if ref.startswith('J') else 'tp' if ref.startswith('TP') else 'flag' if ref.startswith('#FLG') else \
            'd180' if (ref == 'DCL1') else 'v' if ref in ('DVIN1', 'DAUX1') else 'other'
        (rx, ry, rj), (vx, vy, vj) = fields_for(s, ref, kind)
        if ref in LEFT_FIELDS:
            rx, vx, rj, vj = x - 2.032, x - 2.032, 'right', 'right'
        if ref in ('DVIN1', 'DAUX1'):
            (rx, ry, rj), (vx, vy, vj) = (x + 5.08, y - 1.27, None), (x + 5.08, y + 1.27, None)
        if rot == 180 and kind == 'v':
            sw = {'left': 'right', 'right': 'left'}
            rj, vj = sw.get(rj, rj), sw.get(vj, vj)
        new = [c for c in sym if not (isinstance(c, list) and c[0] in ('at', 'mirror', 'property'))]
        at = ['at', num(x), num(y), str(rot)]
        new.insert(2, at)
        if mir:
            new.insert(3, ['mirror', mir])
        part = PARTS.get(ref)
        props = {}
        for p in find(sym, 'property'):
            props[str(p[1])] = str(p[2])
        if part:
            props['Value'] = part['value'].replace(' / ', '/'); props['MPN'] = part['mpn']; props['Manufacturer'] = part['mfr']
            props['Datasheet'] = part['datasheet']; props['Description'] = part['desc']
        if ref in fps:
            props['Footprint'] = fps[ref]
            if part and '0603' in fps[ref]:
                from make_bom import P0603, desc0603
                props['MPN'], props['Manufacturer'], _, props['Datasheet'] = P0603[part['value']]
                props['Description'] = desc0603(part['desc'])
        plist = []
        fang = '90' if rot in (90, 270) else '0'
        if fang == '90':
            rj = vj = None
        for name, value in props.items():
            if name == 'Reference':
                plist.append(['property', Q(name), Q(value), ['at', num(rx), num(ry), fang],
                              eff(1.27, rj, hide=ref.startswith('#'))])
            elif name == 'Value':
                hide = kind == 'tp'
                plist.append(['property', Q(name), Q(value), ['at', num(vx), num(vy), fang], eff(1.0 if kind in ('v', 'h') else 1.27, vj, hide=hide)])
            else:
                plist.append(['property', Q(name), Q(value), ['at', num(x), num(y), '0'], eff(1.27, None, hide=True)])
        idx = next(i for i, c in enumerate(new) if isinstance(c, list) and c[0] == 'uuid') + 1
        new[idx:idx] = plist
        for inst in find(new, 'instances'):
            for pr in find(inst, 'project'):
                pr[1] = Q(PROJECT)
        out_syms.append(new)
    # ---- GND symbols
    gdef = next(c for c in parse(open(POWER_LIB, encoding='utf-8').read()) if isinstance(c, list) and c[0] == 'symbol' and c[1] == 'GND')
    gdef = strip(gdef); gdef[1] = Q('power:GND')
    libsyms = first(s.root, 'lib_symbols')
    if not any(c[1] == 'power:GND' for c in find(libsyms, 'symbol')):
        libsyms.append(gdef)
    for i, (x, y, rot) in enumerate(s.gnds):
        ref = f'#PWR{i + 1:03d}'
        vpos = {0: (x, y + 3.81), 90: (x + 3.81, y), 270: (x - 3.81, y), 180: (x, y - 3.81)}[rot]
        out_syms.append(['symbol', ['lib_id', Q('power:GND')], ['at', num(x), num(y), str(rot)], ['unit', '1'],
                         ['exclude_from_sim', 'no'], ['in_bom', 'yes'], ['on_board', 'yes'], ['dnp', 'no'], ['uuid', U()],
                         ['property', Q('Reference'), Q(ref), ['at', num(x), num(y + 6.35), '0'], eff(1.27, hide=True)],
                         ['property', Q('Value'), Q('GND'), ['at', num(vpos[0]), num(vpos[1]), '0'], eff(1.27, hide=rot != 0)],
                         ['property', Q('Footprint'), Q(''), ['at', num(x), num(y), '0'], eff(1.27, hide=True)],
                         ['property', Q('Datasheet'), Q(''), ['at', num(x), num(y), '0'], eff(1.27, hide=True)],
                         ['pin', Q('1'), ['uuid', U()]],
                         ['instances', ['project', Q(PROJECT), ['path', Q(s.path), ['reference', Q(ref)], ['unit', '1']]]]])
    # ---- wires: split at T points, junctions
    pts = set()
    for a, b in s.segs:
        pts.add(a); pts.add(b)
    pinpts = []
    for ref in s.syms:
        lib = first(s.syms[ref], 'lib_id')[1]
        for n in s.lib_pins(lib):
            pinpts.append(s.pin(ref, n))
    pinpts += [(x, y) for x, y, r in s.gnds]
    lab_pts = [(x, y) for _, x, y, _ in s.labels]
    allpts = pts | set(pinpts) | set(lab_pts)
    segs = []
    for a, b in s.segs:
        inner = [p for p in allpts if p not in (a, b) and on_seg(p, a, b)]
        chain = sorted([a, b] + inner, key=lambda p: (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
        segs += [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
    deg = {}
    for a, b in segs:
        deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
    for p in pinpts:
        if p in deg:
            deg[p] += 1
    junctions = [p for p, d in deg.items() if d >= 3]
    for name, x, y, ang in s.labels:
        assert (x, y) in deg, ('label not on a wire', name, x, y)
    # ---- assemble
    root = s.root
    keep = [c for c in root if not (isinstance(c, list) and c[0] in ('symbol', 'wire', 'label', 'junction', 'no_connect', 'text', 'global_label'))]
    first(keep, 'paper')[1] = Q('A3')
    tb = first(keep, 'title_block')
    tb[:] = ['title_block', ['title', Q('EE463 12 V / 60 W Synchronous Buck Converter (20-48 V in)')], ['date', Q('2026-11-19')],
             ['rev', Q('F2')], ['company', Q('METU EE463 Hardware Project')],
             ['comment', '1', Q('Readable redraw of RevF1 + RevF2 part changes (0805 parts, no Vishay parts)')],
             ['comment', '2', Q('Connectivity identical to the PCB (checked with kicad-cli netlist compare)')]]
    body = keep[:-1] if isinstance(keep[-1], list) and keep[-1][0] == 'embedded_fonts' else keep
    tail = [keep[-1]] if body is not keep else []
    items = []
    for a, b in segs:
        items.append(['wire', ['pts', ['xy', num(a[0]), num(a[1])], ['xy', num(b[0]), num(b[1])]], ['stroke', ['width', '0'], ['type', 'default']], ['uuid', U()]])
    for x, y in junctions:
        items.append(['junction', ['at', num(x), num(y)], ['diameter', '0'], ['color', '0', '0', '0', '0'], ['uuid', U()]])
    for x, y in s.ncs:
        items.append(['no_connect', ['at', num(x), num(y)], ['uuid', U()]])
    for name, x, y, ang in s.labels:
        items.append(['label', Q(name), ['at', num(x), num(y), str(ang)], eff(1.27, 'right bottom' if ang == 180 else 'left bottom'), ['uuid', U()]])
    for t, x, y, size, bold in s.texts:
        items.append(['text', Q(t), ['exclude_from_sim', 'no'], ['at', num(x), num(y), '0'], eff(size, 'left', bold=bold), ['uuid', U()]])
    doc = body + items + out_syms + tail
    txt = dump(doc)
    txt = txt.replace('(justify right bottom)', '(justify right bottom)').replace('(justify left bottom)', '(justify left bottom)')
    open(out, 'w', encoding='utf-8', newline='\n').write(txt + '\n')
    print('symbols', len(out_syms), 'wires', len(segs), 'junctions', len(junctions), 'labels', len(s.labels), 'gnd', len(s.gnds))


def on_seg(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False


def strip(node):
    """drop KiCad-10-only tokens from a library symbol so a 2025 schematic header still parses."""
    drop = {'duplicate_pin_numbers_are_jumpers', 'in_pos_files', 'show_name', 'do_not_autoplace'}
    out = []
    for c in node:
        if isinstance(c, list):
            if c and c[0] in drop:
                continue
            if c and c[0] == 'power':
                out.append(['power']); continue
            out.append(strip(c))
        else:
            out.append(c)
    return out


if __name__ == '__main__':
    build(*sys.argv[1:4])
