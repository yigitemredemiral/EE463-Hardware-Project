"""RevF2 PCB edits on hardware/kicad_RevF2/EE463_Buck_RevF2.kicad_pcb (run with KiCad's python.exe).

1. Every 0603 resistor/capacitor -> KiCad stock 0805 footprint, same position, rotation, side and pad nets
   (course rule: 0805 or larger, 0603 only for a few parts, no 0402).
2. Value / MPN fields follow tools/parts.py (Vishay parts replaced; course rule: no Israel-made parts).
3. Saves every footprint used on the board into the project library EE463Footprints.pretty so the project is
   self-contained (removes the 'not found in library' warnings).
Usage: python.exe tools/revf2_pcb.py [swap|lib]"""
import os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.join(HERE, '..', 'hardware', 'kicad_RevF2')
PCB = os.path.join(PRJ, 'EE463_Buck_RevF2.kicad_pcb')
STOCK = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
SWAP = {'Resistor_SMD:R_0603_1608Metric': ('Resistor_SMD', 'R_0805_2012Metric'),
        'Capacitor_SMD:C_0603_1608Metric': ('Capacitor_SMD', 'C_0805_2012Metric')}


def set_field(fp, name, value):
    new = not fp.HasField(name)
    fp.SetField(name, value)
    if new:
        fp.GetField(name).SetVisible(False)


def swap(board, only=None):
    n = 0
    for fp in list(board.GetFootprints()):
        ref = fp.GetReference()
        lib = str(fp.GetFPID().GetLibNickname()) + ':' + str(fp.GetFPID().GetLibItemName())
        if lib in SWAP and (only is None or ref in only):
            nick, name = SWAP[lib]
            new = pcbnew.FootprintLoad(os.path.join(STOCK, nick + '.pretty'), name)
            assert new is not None, name
            new.SetParent(board)
            new.SetFPID(pcbnew.LIB_ID(nick, name))
            new.SetReference(ref); new.SetValue(fp.GetValue())
            new.SetPath(fp.GetPath())          # keeps the schematic link (symbol UUID)
            new.SetLayerAndFlip(fp.GetLayer()) if hasattr(new, 'SetLayerAndFlip') else None
            if fp.IsFlipped() and not new.IsFlipped():
                new.Flip(new.GetPosition(), False)
            new.SetOrientation(fp.GetOrientation())
            new.SetPosition(fp.GetPosition())
            for f in fp.GetFields():
                if f.GetName() not in ('Reference', 'Value', 'Footprint'):
                    set_field(new, f.GetName(), f.GetText())
            old = {p.GetNumber(): p.GetNet() for p in fp.Pads()}
            for p in new.Pads():
                p.SetNet(old[p.GetNumber()])
            rv = fp.Reference(); new.Reference().SetPosition(rv.GetPosition()); new.Reference().SetVisible(rv.IsVisible())
            new.Reference().SetTextAngle(rv.GetTextAngle())
            vv = fp.Value(); new.Value().SetPosition(vv.GetPosition()); new.Value().SetVisible(vv.IsVisible())
            board.Remove(fp); board.Add(new)
            n += 1
    return n


def fields(board):
    from make_bom import P0603, desc0603
    for fp in board.GetFootprints():
        p = PARTS.get(fp.GetReference())
        if not p:
            continue
        p = dict(p)
        if '0603' in str(fp.GetFPID().GetLibItemName()):
            p['mpn'], p['mfr'], _, p['datasheet'] = P0603[p['value']]
        fp.SetValue(p['value'].replace(' / ', '/'))
        desc = desc0603(p['desc']) if '0603' in str(fp.GetFPID().GetLibItemName()) else p['desc']
        set_field(fp, 'Description', desc)
        if not fp.HasField('Qualification'):
            set_field(fp, 'Qualification', 'Engineering review')
        set_field(fp, 'MPN', p['mpn'])
        set_field(fp, 'Manufacturer', p['mfr'])
        if p.get('datasheet'):
            set_field(fp, 'Datasheet', p['datasheet'])


def save_lib(board):
    lib = os.path.join(PRJ, 'libraries', 'footprints', 'EE463Footprints.pretty')
    done = set()
    if 'trim' in sys.argv:                             # CVCAP1 lost one silk line (clearance to U5): own library entry
        fp = board.FindFootprintByReference('CVCAP1')
        fp.SetFPID(pcbnew.LIB_ID('EE463Footprints', 'C_0805_2012Metric_SilkTrim'))
        rs = board.FindFootprintByReference('RS1')         # shunt land pattern (3.05 x 3.68 mm pads, 1.27 mm gap)
        rs.SetFPID(pcbnew.LIB_ID('EE463Footprints', 'R_2512_Shunt_Kelvin_3.05x3.68mm'))
    for fp in board.GetFootprints():
        fid = fp.GetFPID(); key = str(fid.GetLibNickname()) + ':' + str(fid.GetLibItemName())
        if key in done:
            continue
        done.add(key)
        nick = str(fid.GetLibNickname())
        path = os.path.join(PRJ, 'libraries', 'footprints', nick + '.pretty')
        os.makedirs(path, exist_ok=True)
        c = pcbnew.FOOTPRINT(fp)
        c.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T)); c.SetPosition(pcbnew.VECTOR2I(0, 0))
        if c.IsFlipped():
            c.Flip(c.GetPosition(), False)
        for p in c.Pads():
            p.SetNetCode(0)
        try:
            pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP).FootprintSave(path, c)
        except Exception as e:
            print('could not save', key, e)
    return sorted(done)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'test':     # test <in.kicad_pcb> <out.kicad_pcb> REF[,REF...]
        b = pcbnew.LoadBoard(sys.argv[2]); print(swap(b, set(sys.argv[4].split(','))), 'swapped')
        pcbnew.SaveBoard(sys.argv[3], b); sys.exit()
    board = pcbnew.LoadBoard(PCB)
    what = sys.argv[1] if len(sys.argv) > 1 else 'swap'
    if what == 'swap':
        print('swapped', swap(board)); fields(board)
    elif what == 'lib':
        print('\n'.join(save_lib(board)))
    elif what == 'fields':
        fields(board)
    elif what == 'gnd':                                  # the schematic uses the GND power symbol -> net 'GND'
        n = board.FindNet('/GND')
        if n:
            n.SetNetname('GND'); print('renamed /GND -> GND')
    pcbnew.SaveBoard(PCB, board)
