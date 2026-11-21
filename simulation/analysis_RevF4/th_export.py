"""KiCad python: copper raster (per layer, per net) + footprint/via data for the thermal and IR-drop models.
Usage: th_export.py board.kicad_pcb out.npz out.json"""
import pcbnew, sys, json, numpy as np
from PIL import Image, ImageDraw
RES = 0.1
b = pcbnew.LoadBoard(sys.argv[1]); mm, FM = pcbnew.ToMM, pcbnew.FromMM
e = b.GetBoardEdgesBoundingBox()
X0, Y0 = mm(e.GetLeft()), mm(e.GetTop()); NX, NY = int(round(mm(e.GetWidth()) / RES)), int(round(mm(e.GetHeight()) / RES))
LAY = {'F': pcbnew.F_Cu, 'In1': pcbnew.In1_Cu, 'In2': pcbnew.In2_Cu, 'B': pcbnew.B_Cu}
nets = {}
def nid(n):
    if n not in nets: nets[n] = len(nets) + 1
    return nets[n]
img = {k: Image.new('I', (NX, NY), 0) for k in LAY}
def draw(ps, im, v):
    d = ImageDraw.Draw(im)
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i); pts = [((mm(o.CPoint(k).x) - X0) / RES, (mm(o.CPoint(k).y) - Y0) / RES) for k in range(o.PointCount())]
        if len(pts) >= 3: d.polygon(pts, fill=v)
        for h in range(ps.HoleCount(i)):
            ho = ps.Hole(i, h); hp = [((mm(ho.CPoint(k).x) - X0) / RES, (mm(ho.CPoint(k).y) - Y0) / RES) for k in range(ho.PointCount())]
            if len(hp) >= 3: d.polygon(hp, fill=0)
def shp(it, L):
    ps = pcbnew.SHAPE_POLY_SET(); it.TransformShapeToPolygon(ps, L, 0, FM(0.005), pcbnew.ERROR_INSIDE); return ps
ZS = list(b.Zones())
for z in sorted(ZS, key=lambda z: z.GetAssignedPriority()):
    for k, L in LAY.items():
        if z.IsOnLayer(L): draw(z.GetFilledPolysList(L), img[k], nid(z.GetNetname()))
TR = list(b.GetTracks()); vias = []
for t in TR:
    v = nid(t.GetNetname())
    if t.GetClass() == 'PCB_VIA':
        for k, L in LAY.items(): draw(shp(t, L), img[k], v)
        vias.append([mm(t.GetPosition().x) - X0, mm(t.GetPosition().y) - Y0, v, mm(t.GetDrill())])
    else:
        for k, L in LAY.items():
            if t.GetLayer() == L: draw(shp(t, L), img[k], v)
fps = []
for f in b.GetFootprints():
    pads = []
    for p in f.Pads():
        v = nid(p.GetNetname()) if p.GetNetname() else 0
        for k, L in LAY.items():
            if p.IsOnLayer(L): draw(shp(p, L), img[k], v if v else 30000)
        bb = p.GetBoundingBox()
        pads.append(dict(num=p.GetNumber(), net=p.GetNetname(), c=[mm(p.GetPosition().x) - X0, mm(p.GetPosition().y) - Y0],
                         bb=[mm(bb.GetLeft()) - X0, mm(bb.GetTop()) - Y0, mm(bb.GetRight()) - X0, mm(bb.GetBottom()) - Y0]))
    cy = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else f.GetBoundingBox(False)
    fps.append(dict(ref=f.GetReference(), val=f.GetValue(), side='F' if f.GetLayer() == pcbnew.F_Cu else 'B',
                    c=[mm(f.GetPosition().x) - X0, mm(f.GetPosition().y) - Y0],
                    bb=[mm(bb.GetLeft()) - X0, mm(bb.GetTop()) - Y0, mm(bb.GetRight()) - X0, mm(bb.GetBottom()) - Y0], pads=pads))
np.savez_compressed(sys.argv[2], **{k: np.array(im, dtype=np.int32) for k, im in img.items()})
json.dump(dict(RES=RES, NX=NX, NY=NY, W=mm(e.GetWidth()), H=mm(e.GetHeight()), nets=nets, vias=vias, fps=fps), open(sys.argv[3], 'w'))
print('grid', NX, NY, 'nets', len(nets), 'vias', len(vias), 'fps', len(fps))
