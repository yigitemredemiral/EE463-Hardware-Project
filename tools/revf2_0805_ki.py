"""KiCad-python side of revf2_0805.py: replace one 0603 footprint by the stock 0805 one (same place, nets, fields)."""
import os
import pcbnew

STOCK = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
SWAP = {'Resistor_SMD:R_0603_1608Metric': ('Resistor_SMD', 'R_0805_2012Metric'),
        'Capacitor_SMD:C_0603_1608Metric': ('Capacitor_SMD', 'C_0805_2012Metric')}


def set_field(fp, name, value):
    new = not fp.HasField(name)
    fp.SetField(name, value)
    if new:
        fp.GetField(name).SetVisible(False)


def swap_one(board, fp):
    nick, name = SWAP[str(fp.GetFPID().GetLibNickname()) + ':' + str(fp.GetFPID().GetLibItemName())]
    new = pcbnew.FootprintLoad(os.path.join(STOCK, nick + '.pretty'), name)
    new.SetParent(board); new.SetFPID(pcbnew.LIB_ID(nick, name))
    new.SetReference(fp.GetReference()); new.SetValue(fp.GetValue()); new.SetPath(fp.GetPath())
    if fp.IsFlipped():
        new.Flip(new.GetPosition(), False)
    new.SetOrientation(fp.GetOrientation()); new.SetPosition(fp.GetPosition())
    for f in fp.GetFields():
        if f.GetName() not in ('Reference', 'Value', 'Footprint'):
            set_field(new, f.GetName(), f.GetText())
    nets = {p.GetNumber(): p.GetNet() for p in fp.Pads()}
    for p in new.Pads():
        p.SetNet(nets[p.GetNumber()])
    r0, r1 = fp.Reference(), new.Reference()
    r1.SetPosition(r0.GetPosition()); r1.SetVisible(r0.IsVisible()); r1.SetTextAngle(r0.GetTextAngle())
    r1.SetTextSize(r0.GetTextSize()); r1.SetTextThickness(r0.GetTextThickness())
    new.Value().SetVisible(False)
    board.Remove(fp); board.Add(new)
    return new
