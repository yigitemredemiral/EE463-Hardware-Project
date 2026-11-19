"""Delete the silkscreen outline segment of a small part where it comes closer than the silk clearance to the
silkscreen of a neighbouring part (list from a kicad-cli DRC json). Run with KiCad's python.exe:
python.exe tools/silk_trim.py <board.kicad_pcb> <drc.json>"""
import json, sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2])); n = 0
for v in d['violations']:
    if v['type'] != 'silk_overlap':
        continue
    for it in v['items']:
        desc = it['description']
        if desc.startswith('Segment of '):
            ref = desc.split()[2]; fp = b.FindFootprintByReference(ref)
            x, y = pcbnew.FromMM(it['pos']['x']), pcbnew.FromMM(it['pos']['y'])
            for g in list(fp.GraphicalItems()):
                if g.GetLayer() == pcbnew.F_SilkS and g.HitTest(pcbnew.VECTOR2I(x, y), pcbnew.FromMM(0.05)):
                    fp.Remove(g); n += 1; break
            break
print('removed silk segments:', n)
pcbnew.SaveBoard(sys.argv[1], b)
