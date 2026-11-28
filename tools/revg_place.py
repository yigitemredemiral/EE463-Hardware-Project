"""RevG board: footprints from the RevG netlist, placed at fixed coordinates (KiCad python).
Template = RevF4 board (stack-up, design rules, net classes); everything else is rebuilt.
Usage: python.exe tools/revg_place.py build/g.net hardware/kicad_RevF4/EE463_Buck_RevF4.kicad_pcb hardware/kicad_RevG/EE463_Buck_RevG.kicad_pcb"""
import os, re, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kinet import sexp, find, val

NET, TPL, OUT = sys.argv[1:4]
LIBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hardware', 'kicad_RevG', 'libraries', 'footprints')
MM = pcbnew.FromMM
X0, Y0, W, H = 100.0, 100.0, 130.0, 78.0

# ref: (x, y, rot, side)   side 'F' or 'B'
P = {
    # ---------------- input: J1 (wire entry faces left), fuse, ideal diode
    'J1': (105.75, 126.0, 270, 'F'), 'F1': (114.5, 121.0, 90, 'F'),
    'Q3': (121.08, 108.0, 180, 'F'), 'U5': (119.5, 115.0, 0, 'F'),
    'CVCAP1': (115.8, 113.6, 90, 'F'), 'CANODE1': (119.8, 119.0, 0, 'F'),
    'CCATH1': (124.0, 114.0, 90, 'F'), 'DVIN1': (124.0, 117.8, 90, 'F'),
    'TP1': (108.5, 111.0, 0, 'F'), 'TP2': (126.5, 104.0, 0, 'F'),
    # ---------------- bulk input capacitors: tight row below the input block
    'CINB1': (107.0, 141.0, 0, 'F'), 'CINB2': (118.0, 141.0, 0, 'F'), 'CINB3': (129.0, 141.0, 0, 'F'),
    # ---------------- power stage: Q1 tab up on HS1, Q2 tab down on HS2 (hot loop between the leg rows)
    'HS1': (167.5, 107.6, 0, 'F'), 'Q1': (164.96, 117.25, 0, 'F'),
    'HS2': (170.04, 134.5, 0, 'F'), 'Q2': (172.58, 124.85, 180, 'F'),
    'CHF1': (167.5, 121.05, 270, 'F'), 'CHF2': (167.5, 121.05, 270, 'B'), 'CHF3': (164.96, 121.05, 270, 'B'),
    'CIN1': (151.5, 121.0, 270, 'B'), 'CIN2': (155.0, 121.0, 270, 'B'), 'CIN3': (158.5, 121.0, 270, 'B'),
    'CIN4': (162.0, 121.0, 270, 'B'), 'CIN5': (158.9, 112.3, 90, 'B'),
    'CIN6': (162.4, 112.3, 90, 'B'), 'CIN7': (165.9, 112.3, 90, 'B'), 'CIN8': (169.4, 112.3, 90, 'B'),
    'CIN9': (172.9, 112.3, 90, 'B'), 'CIN10': (176.4, 112.3, 90, 'B'),
    'RSN1': (179.0, 121.0, 0, 'B'), 'CSN1': (182.5, 121.0, 0, 'B'),
    'TP5': (184.0, 121.0, 0, 'F'), 'TP6': (158.0, 124.2, 0, 'F'), 'TP7': (176.0, 126.5, 0, 'F'),
    # ---------------- output
    'L1': (196.0, 121.0, 0, 'F'), 'RS1': (209.0, 121.0, 0, 'F'), 'TP9': (206.0, 116.5, 0, 'F'),
    'COUT1': (214.0, 108.0, 90, 'F'), 'COUT2': (214.0, 134.0, 270, 'F'),
    'J2': (224.85, 123.5, 90, 'F'), 'TP4': (220.0, 141.5, 0, 'F'),
    # ---------------- controller U1 left of the stage, gate pins (right side) face Q1/Q2
    'U1': (143.5, 121.0, 0, 'F'),
    'ROVT1': (135.5, 108.0, 0, 'F'), 'ROVB1': (135.5, 110.6, 0, 'F'), 'CSENSE1': (135.0, 114.6, 180, 'F'),
    'CSS1': (135.5, 118.4, 180, 'F'), 'RFBT1': (135.5, 121.0, 0, 'F'), 'RFBB1': (135.5, 123.6, 0, 'F'),
    'RITH1': (135.5, 126.2, 0, 'F'), 'CITH1': (135.5, 128.8, 0, 'F'), 'CITHP1': (135.5, 131.4, 0, 'F'),
    'CINT1': (141.0, 128.6, 0, 'F'), 'RPG1': (135.5, 134.0, 0, 'F'), 'RFREQ1': (141.0, 131.2, 0, 'F'),
    'CAUX1': (130.5, 131.4, 0, 'F'), 'DAUX1': (130.5, 127.8, 0, 'F'),
    'RRUNT1': (130.5, 108.0, 0, 'F'), 'RRUNB1': (130.5, 110.6, 0, 'F'), 'CRUN1': (130.5, 113.2, 0, 'F'),
    'CDRV1': (149.6, 123.0, 0, 'F'), 'CBOOT1': (152.6, 125.6, 270, 'F'),
    'RGH1': (155.5, 117.25, 0, 'F'), 'RGSH1': (161.2, 120.0, 0, 'F'),
    'RGL1': (149.5, 129.0, 0, 'F'), 'RGSL1': (149.5, 131.6, 0, 'F'),
    'TP10': (131.0, 121.0, 0, 'F'), 'TP8': (131.0, 124.5, 0, 'F'), 'TP13': (131.0, 134.6, 0, 'F'),
    'TP15': (138.6, 134.2, 0, 'F'), 'TP14': (147.0, 133.0, 0, 'F'), 'TP16': (130.5, 104.5, 0, 'F'),
    'TP3': (108.0, 152.0, 0, 'F'),
    # ---------------- average current-limit loop (optional), bottom right
    'U2': (190.0, 149.0, 0, 'F'), 'RCSP1': (184.0, 144.8, 0, 'F'), 'RCSN1': (184.0, 147.6, 0, 'F'),
    'RCSO1': (195.5, 151.5, 90, 'F'), 'CCS1': (198.0, 151.5, 90, 'F'), 'TP11': (201.0, 149.0, 0, 'F'),
    'U3': (190.0, 161.0, 0, 'F'), 'RERR1': (183.5, 157.5, 0, 'F'), 'CERR1': (183.5, 161.0, 0, 'F'),
    'RLEAK1': (183.5, 164.0, 0, 'F'), 'RISO1': (196.5, 161.0, 0, 'F'), 'DCL1': (196.5, 165.5, 0, 'F'),
    'JP1': (178.0, 167.0, 90, 'F'),
    'C1': (185.6, 151.6, 90, 'F'), 'C2': (195.8, 157.0, 0, 'F'), 'C3': (210.2, 163.8, 90, 'F'),
    'U4': (206.0, 161.0, 0, 'F'), 'CREF1': (210.5, 157.5, 90, 'F'), 'RSETT1': (206.0, 166.0, 0, 'F'),
    'RSETB1': (206.0, 169.0, 0, 'F'), 'TP12': (202.0, 170.5, 0, 'F'),
    # ---------------- status LEDs + ON/OFF switch, bottom left edge
    'SW1': (124.0, 173.0, 0, 'F'),
    'RLED1': (140.0, 164.0, 0, 'F'), 'DLED1': (140.0, 168.0, 0, 'F'),
    'RLED2': (147.0, 164.0, 0, 'F'), 'DLED2': (147.0, 168.0, 0, 'F'),
    'RLED3': (154.0, 164.0, 0, 'F'), 'DLED3': (154.0, 168.0, 0, 'F'),
}
HOLES = [(104.0, 104.0), (226.0, 104.0), (104.0, 174.0), (226.0, 174.0)]


PF = {}


def comps_and_nets(path):
    t = sexp(open(path, encoding='utf-8').read())
    comps = {}
    for c in find(find(t, 'components')[0], 'comp'):
        ref = val(c, 'ref'); sp = find(c, 'sheetpath')[0]
        comps[ref] = dict(fp=val(c, 'footprint'), value=val(c, 'value'), uuid=val(find(c, 'tstamps')[0], 'tstamps') if False else find(c, 'tstamps')[0][1],
                          fields={val(f, 'name'): f[2] for fs in find(c, 'fields') for f in find(fs, 'field') if len(f) > 2})
    pads = {}
    for n in find(find(t, 'nets')[0], 'net'):
        name = val(n, 'name')
        for nd in find(n, 'node'):
            pads[(val(nd, 'ref'), val(nd, 'pin'))] = name
            PF[(val(nd, 'ref'), val(nd, 'pin'))] = (val(nd, 'pinfunction') or '', val(nd, 'pintype') or '')
    return comps, pads


def main():
    comps, pads = comps_and_nets(NET)
    b = pcbnew.LoadBoard(TPL)
    for x in list(b.Tracks()) + list(b.Zones()) + list(b.GetDrawings()):
        b.Delete(x)
    for x in list(b.Footprints()):
        b.Delete(x)
    nets = {}
    for name in sorted(set(pads.values())):
        ni = b.FindNet(name)
        if not ni:
            ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
        nets[name] = ni
    missing = set(comps) - set(P)
    assert not missing, ('no position', sorted(missing))
    for ref, c in sorted(comps.items()):
        lib, name = c['fp'].split(':')
        fp = pcbnew.FootprintLoad(os.path.join(LIBS, lib + '.pretty'), name)
        assert fp, c['fp']
        fp.SetReference(ref); fp.SetValue(c['value']); fp.SetFPIDAsString(c['fp'])
        fp.SetPath(pcbnew.KIID_PATH('/' + c['uuid']))
        fp.SetDNP(False); fp.SetExcludedFromBOM(False)
        for k in [k for k in c['fields'] if k not in ('Footprint',)]:
            if k in c['fields']:
                fp.SetField(k, c['fields'][k])
                fp.GetField(k).SetVisible(False)
        b.Add(fp)
        x, y, rot, side = P[ref]
        rf = fp.Reference()
        if not ref.startswith(('J', 'HS', 'L1', 'U1', 'SW')):
            rf.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); rf.SetTextThickness(MM(0.12))
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        if side == 'B':
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetOrientationDegrees(rot)
        for pd in fp.Pads():
            n = pads.get((ref, pd.GetNumber()))
            if n:
                pd.SetNet(nets[n])
            pf = PF.get((ref, pd.GetNumber()))
            if pf:
                pd.SetPinFunction(pf[0]); pd.SetPinType(pf[1])
    for i, (x, y) in enumerate(HOLES):
        fp = pcbnew.FootprintLoad(os.path.join(LIBS, 'MountingHole.pretty'), 'MountingHole_3.2mm_M3')
        fp.SetReference(f'H{i + 1}'); fp.Reference().SetVisible(False); fp.SetBoardOnly(True); fp.SetFPIDAsString('MountingHole:MountingHole_3.2mm_M3'); fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); b.Add(fp)
    r = pcbnew.PCB_SHAPE(b); r.SetShape(pcbnew.SHAPE_T_RECT); r.SetLayer(pcbnew.Edge_Cuts); r.SetWidth(MM(0.1))
    r.SetStart(pcbnew.VECTOR2I(MM(X0), MM(Y0))); r.SetEnd(pcbnew.VECTOR2I(MM(X0 + W), MM(Y0 + H))); b.Add(r)
    def text(s, x, y, size, layer=pcbnew.F_SilkS, bold=False, thick=0.15):
        tx = pcbnew.PCB_TEXT(b); tx.SetText(s); tx.SetLayer(layer)
        tx.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); tx.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        tx.SetTextThickness(MM(thick if not bold else size * 0.15)); tx.SetBold(bold)
        if layer == pcbnew.B_SilkS:
            tx.SetMirrored(True)
        b.Add(tx)
    # back side: team / names
    BS = pcbnew.B_SilkS
    text('EE463 POWER ELECTRONICS', 140.0, 150.0, 2.2, BS, True)
    text('TEAM CMPS', 140.0, 155.5, 3.0, BS, True)
    for k, s in enumerate(['Yiğit Emre Demiral', 'Tunahan Ceylan', 'Yasin Baytemir']):
        text(s, 140.0, 161.0 + 3.2 * k, 2.0, BS)
    text('12 V / 60 W synchronous buck  -  RevG  -  METU 2026', 152.0, 170.0, 1.5, BS)
    # front labels
    text('IN 20-48 V', 108.0, 134.0, 1.5); text('+', 103.0, 126.0, 2.0, bold=True); text('-', 103.0, 131.1, 2.0, bold=True)
    text('12 V OUT', 224.5, 110.6, 1.2); text('+', 224.85, 128.4, 2.0, bold=True); text('-', 224.85, 113.4, 2.0, bold=True)
    text('IN', 140.0, 170.5, 1.2); text('OUT', 147.0, 170.5, 1.2); text('FAULT', 154.0, 170.5, 1.2)
    text('ON/OFF', 124.0, 169.0, 1.3); text('CL LOOP', 178.0, 163.0, 1.2)
    text('EE463 TEAM CMPS  12V/60W BUCK  RevG', 165.0, 175.5, 1.5, bold=True)
    b.Save(OUT)
    print('placed', len(comps), 'nets', len(nets))


main()
