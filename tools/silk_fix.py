"""Move silkscreen reference texts so they do not overlap pads, other references or other silkscreen lines
(the 0805 parts are larger than the 0603 parts they replaced). Text size is kept at the board minimum 0.8 mm.
Run with KiCad's python.exe: python.exe tools/silk_fix.py <board.kicad_pcb>"""
import sys
import pcbnew

mm, MM = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
edge = b.GetBoardEdgesBoundingBox()


def box(item, grow=0.0):
    r = item.GetBoundingBox()
    if grow:
        r.Inflate(mm(grow))
    return r


def inter(a, c):
    return a.Intersects(c)


pads, silk = [], []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.F_Cu):
            pads.append(box(p, 0.15))
    for g in fp.GraphicalItems():
        if g.GetLayer() == pcbnew.F_SilkS and g.Type() != pcbnew.PCB_FIELD_T:
            silk.append((fp.GetReference(), box(g, 0.1)))
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.F_SilkS:
        silk.append(('', box(d, 0.1)))
for v in b.GetTracks():
    if v.Type() == pcbnew.PCB_VIA_T:
        pads.append(box(v, 0.1))

texts = {}
fps = [fp for fp in b.GetFootprints() if fp.Reference().IsVisible() and fp.Reference().GetLayer() == pcbnew.F_SilkS]
for fp in fps:
    t = fp.Reference()
    if t.GetTextHeight() < mm(0.8):
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); t.SetTextThickness(mm(0.12))
    texts[fp.GetReference()] = box(t, 0.05)


def bad(ref, r):
    if not edge.Contains(r):
        return True
    if any(inter(r, p) for p in pads):
        return True
    if any(inter(r, s) for owner, s in silk if owner != ref or True):
        return True
    return any(inter(r, o) for k, o in texts.items() if k != ref)


moved = kept = failed = 0
for fp in sorted(fps, key=lambda f: f.GetReference()):
    ref = fp.GetReference(); t = fp.Reference()
    if not bad(ref, texts[ref]):
        kept += 1; continue
    c = fp.GetBoundingBox(False, False)
    cx, cy = c.GetCenter().x, c.GetCenter().y
    w, h = c.GetWidth() / 2, c.GetHeight() / 2
    th = mm(0.8)
    cands = []
    for k in (0.7, 1.2, 1.8, 2.5):
        d = mm(k)
        cands += [(cx, cy - h - d), (cx, cy + h + d), (cx - w - d - mm(1.0), cy), (cx + w + d + mm(1.0), cy),
                  (cx - w - d, cy - h - d), (cx + w + d, cy - h - d), (cx - w - d, cy + h + d), (cx + w + d, cy + h + d)]
    best = None
    for ang in (t.GetTextAngleDegrees(), 0, 90):
        t.SetTextAngleDegrees(ang)
        for x, y in cands:
            t.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
            r = box(t, 0.05)
            if not bad(ref, r):
                best = (x, y, ang); break
        if best:
            break
    if best:
        t.SetTextAngleDegrees(best[2]); t.SetPosition(pcbnew.VECTOR2I(int(best[0]), int(best[1])))
        texts[ref] = box(t, 0.05); moved += 1
    else:
        t.SetVisible(False); texts.pop(ref, None); failed += 1   # shown on F.Fab / assembly drawing instead
        print('hidden on silk (no free place):', ref)
print(f'kept {kept}, moved {moved}, hidden {failed}')
pcbnew.SaveBoard(sys.argv[1], b)
