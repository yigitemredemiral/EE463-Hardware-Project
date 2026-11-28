"""RevG routing (KiCad python): power zones + grid A* router for the signal nets (F.Cu / B.Cu, through vias).
Ground and VIN fan out to the inner planes with a via next to each pad.
Usage: python.exe tools/revg_route.py <board.kicad_pcb>"""
import heapq, math, sys, time
import pcbnew

B = pcbnew.LoadBoard(sys.argv[1])
MM = pcbnew.FromMM
TO = lambda v: v / 1e6
G = 0.25                      # grid (mm), U1 pins (0.5 mm pitch) land on it
X0, Y0, W, H = 100.0, 100.0, 130.0, 78.0
NX, NY = int(W / G) + 1, int(H / G) + 1
TW, CL = 0.25, 0.2            # signal track width, clearance
OV = {}                       # net code -> cells always allowed (pad escape stubs)
VD, VDR = 0.6, 0.3            # signal via
LAY = [pcbnew.F_Cu, pcbnew.B_Cu]
NAME = {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B'}
FP = {f.GetReference(): f for f in B.Footprints()}
NETNAME = {n.GetNetCode(): n.GetNetname() for n in B.GetNetsByName().values()}


def net(n):
    return B.FindNet(n)


# ------------------------------------------------------------------ zones
def zone(netname, layer, pts, prio=0, clearance=0.3, minw=0.25, thermal=False, name=None):
    z = pcbnew.ZONE(B)
    z.SetLayer(layer)
    if netname:
        z.SetNet(net(netname))
    ol = z.Outline(); ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(minw))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(MM(0.3)); z.SetThermalReliefSpokeWidth(MM(0.5))
    if name:
        z.SetZoneName(name)
    B.Add(z)
    return z


def rect(x1, y1, x2, y2):
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


E = rect(X0 + 0.5, Y0 + 0.5, X0 + W - 0.5, Y0 + H - 0.5)
POUR = []       # (net, layer, polygon) used as router obstacles for other nets


def pour(netname, layer, pts, prio, **k):
    zone(netname, layer, pts, prio, **k)
    POUR.append((netname, layer, pts))


def make_zones():
    zone('GND', pcbnew.In1_Cu, E, 0)
    zone('GND', pcbnew.B_Cu, E, 0, thermal=False)
    zone('GND', pcbnew.F_Cu, E, 0, thermal=False)
    zone('/VIN', pcbnew.In2_Cu, rect(X0 + 0.5, Y0 + 0.5, 203.0, Y0 + H - 0.5), 1)
    zone('/VOUT', pcbnew.In2_Cu, rect(203.6, Y0 + 0.5, X0 + W - 0.5, Y0 + H - 0.5), 1)
    # B.Cu VIN band under the Q1 leg row (input MLCC pads)
    pour('/VIN', pcbnew.B_Cu, rect(150.0, 113.0, 178.4, 119.9), 3)
    # F.Cu power pours
    pour('Net-(J1-Pin_1)', pcbnew.F_Cu, rect(101.0, 122.6, 116.6, 129.5), 3)
    pour('/VIN_RAW', pcbnew.F_Cu, [(110.0, 105.5), (117.1, 105.5), (117.1, 110.4), (114.6, 110.4), (114.6, 120.0), (110.0, 120.0)], 3)
    pour('/SW', pcbnew.F_Cu, [(168.9, 116.2), (171.3, 116.2), (171.3, 118.55), (188.8, 118.55), (188.8, 114.0), (192.6, 114.0),
                              (192.6, 128.0), (188.8, 128.0), (188.8, 123.0), (171.3, 123.0), (171.3, 126.2), (168.9, 126.2)], 4)
    pour('/SENSEP', pcbnew.F_Cu, rect(199.4, 114.0, 207.9, 128.0), 4)
    pour('/VOUT', pcbnew.F_Cu, [(210.1, 118.6), (210.1, 113.6), (211.6, 113.6), (211.6, 108.9), (216.6, 108.9), (216.6, 113.6),
                                (221.0, 113.6), (221.0, 121.5), (227.5, 121.5), (227.5, 128.0), (216.6, 128.0), (216.6, 133.1),
                                (211.6, 133.1), (211.6, 128.0), (210.1, 128.0)], 4)
    # U1: INTVCC pin pairs joined outside the GND pin between them; VIN pin 30 to an In2 via
    for (xa, ya), (xb, yb), n, w in [((146.275, 116.5), (147.3, 116.5), '/INTVCC', 0.2), ((146.275, 117.5), (147.3, 117.5), '/INTVCC', 0.2),
                                    ((147.3, 116.5), (147.3, 117.5), '/INTVCC', 0.2), ((140.725, 120.0), (139.7, 120.0), '/INTVCC', 0.2),
                                    ((140.725, 121.0), (139.7, 121.0), '/INTVCC', 0.2), ((139.7, 120.0), (139.7, 121.0), '/INTVCC', 0.2),
                                    ((146.275, 120.5), (148.3, 120.5), '/VIN', 0.25),
                                    ((140.725, 117.5), (139.0, 117.5), '/SENSEP', 0.2), ((139.0, 117.5), (137.6, 116.1), '/SENSEP', 0.2),
                                    ((137.6, 116.1), (137.6, 114.6), '/SENSEP', 0.2), ((137.6, 114.6), (135.95, 114.6), '/SENSEP', 0.2),
                                    ((140.725, 118.0), (138.8, 118.0), '/VOUT', 0.2), ((138.8, 118.0), (137.1, 116.3), '/VOUT', 0.2),
                                    ((137.1, 116.3), (134.6, 116.3), '/VOUT', 0.2), ((134.6, 116.3), (134.05, 115.75), '/VOUT', 0.2),
                                    ((134.05, 115.75), (134.05, 114.6), '/VOUT', 0.2),
                                    ((140.725, 119.0), (138.4, 119.0), '/FB', 0.2), ((138.4, 119.0), (136.45, 120.95), '/FB', 0.2),
                                    ((140.725, 119.5), (139.0, 119.5), '/ITH', 0.2), ((139.0, 119.5), (139.0, 120.5), '/ITH', 0.2),
                                    ((140.725, 118.5), (136.45, 118.5), '/SS', 0.2)]:
        t = pcbnew.PCB_TRACK(B); t.SetStart(pcbnew.VECTOR2I(MM(xa), MM(ya))); t.SetEnd(pcbnew.VECTOR2I(MM(xb), MM(yb)))
        t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu); t.SetNet(net(n)); B.Add(t)
    v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(MM(148.6), MM(120.5))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
    v.SetNet(net('/VIN')); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); B.Add(v)
    v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(MM(139.0), MM(120.5))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
    v.SetNet(net('/ITH')); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); B.Add(v)
    # CHF1 (F.Cu) straight to the Q1 drain and the Q2 source
    for y1, y2, n in ((118.0, 120.3, '/VIN'), (121.8, 124.1, 'GND')):
        t = pcbnew.PCB_TRACK(B); t.SetStart(pcbnew.VECTOR2I(MM(167.5), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(167.5), MM(y2)))
        t.SetWidth(MM(1.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(net(n)); B.Add(t)


# ------------------------------------------------------------------ obstacle grid
def gi(x):
    return int(round((x - X0) / G))


def gj(y):
    return int(round((y - Y0) / G))


class Grid:
    def __init__(self):
        self.o = [bytearray(NX * NY) for _ in LAY]      # 0 free, else net id+1 (mod 250)... we store owner net code
        self.own = [dict() for _ in LAY]                 # cell -> set of netcodes blocking it (pads, pours)
        self.trk = [dict() for _ in LAY]                 # same for tracks / vias (never overridden)

    def block(self, li, x1, y1, x2, y2, code, circle=None, trk=False):
        i1, i2, j1, j2 = max(0, gi(x1)), min(NX - 1, gi(x2)), max(0, gj(y1)), min(NY - 1, gj(y2))
        own = (self.trk if trk else self.own)[li]
        for i in range(i1, i2 + 1):
            for j in range(j1, j2 + 1):
                if circle:
                    cx, cy, r = circle
                    if (X0 + i * G - cx) ** 2 + (Y0 + j * G - cy) ** 2 > r * r:
                        continue
                c = j * NX + i
                s = own.get(c)
                if s is None:
                    own[c] = {code}
                else:
                    s.add(code)

    def free(self, li, c, code):
        t = self.trk[li].get(c)
        if t is not None and t != {code}:
            return False
        s = self.own[li].get(c)
        return s is None or s == {code} or (li, c) in OV.get(code, ())


GR = Grid()
M = CL + TW / 2               # keep-out margin around foreign copper for a track centre


def add_pad(pd):
    code = pd.GetNetCode()
    bb = pd.GetBoundingBox()
    x1, y1, x2, y2 = TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())
    th = pd.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
    for li, L in enumerate(LAY):
        if th or pd.IsOnLayer(L):
            circ = None
            if pd.GetShape(L) == pcbnew.PAD_SHAPE_CIRCLE:
                circ = ((x1 + x2) / 2, (y1 + y2) / 2, (x2 - x1) / 2 + M)
            GR.block(li, x1 - M, y1 - M, x2 + M, y2 + M, code, circ)


def add_seg(li, a, b, w, code):
    (x1, y1), (x2, y2) = a, b
    r = w / 2 + M
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / (G / 2)))
    for k in range(n + 1):
        x = x1 + (x2 - x1) * k / n; y = y1 + (y2 - y1) * k / n
        GR.block(li, x - r, y - r, x + r, y + r, code, (x, y, r), trk=True)


def add_poly(li, pts, code):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for i in range(max(0, gi(min(xs) - M)), min(NX - 1, gi(max(xs) + M)) + 1):
        for j in range(max(0, gj(min(ys) - M)), min(NY - 1, gj(max(ys) + M)) + 1):
            x, y = X0 + i * G, Y0 + j * G
            if inside(pts, x, y) or dist_poly(pts, x, y) < M:
                c = j * NX + i
                GR.own[li].setdefault(c, set()).add(code)


def inside(pts, x, y):
    c = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def dist_poly(pts, x, y):
    d = 1e9
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        dx, dy = x2 - x1, y2 - y1
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1)))
        d = min(d, math.hypot(x - x1 - t * dx, y - y1 - t * dy))
    return d


VIA_BLOCK = set()    # cells where a via may not go (THT holes, heatsink pads, edges)


def build_grid():
    for f in B.Footprints():
        for pd in f.Pads():
            add_pad(pd)
    for nn, L, pts in POUR:
        add_poly(LAY.index(L), pts, net(nn).GetNetCode())
    for t in B.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition(); r = TO(t.GetWidth(pcbnew.F_Cu)) / 2 + M
            for li in (0, 1):
                GR.block(li, TO(p.x) - r, TO(p.y) - r, TO(p.x) + r, TO(p.y) + r, t.GetNetCode(), (TO(p.x), TO(p.y), r), trk=True)
        else:
            li = LAY.index(t.GetLayer()) if t.GetLayer() in LAY else None
            if li is not None:
                s, e = t.GetStart(), t.GetEnd()
                add_seg(li, (TO(s.x), TO(s.y)), (TO(e.x), TO(e.y)), TO(t.GetWidth()), t.GetNetCode())
    # board edge keep-out
    for li in (0, 1):
        for i in range(NX):
            for j in list(range(0, int(0.8 / G) + 1)) + list(range(NY - int(0.8 / G) - 1, NY)):
                GR.own[li].setdefault(j * NX + i, set()).add(-1)
        for j in range(NY):
            for i in list(range(0, int(0.8 / G) + 1)) + list(range(NX - int(0.8 / G) - 1, NX)):
                GR.own[li].setdefault(j * NX + i, set()).add(-1)


# ------------------------------------------------------------------ A*
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
VIA_COST = 12.0
VR = VD / 2 + CL - TW / 2       # extra radius for a via beyond a track centre keep-out


VIAS = []


def via_ok(c, code):
    x, y = xy(c)
    if any((x - a) ** 2 + (y - b) ** 2 < 1.0 for a, b in VIAS):
        return False
    i, j = c % NX, c // NX
    k = int(math.ceil(VR / G))
    for li in (0, 1):
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if di * di + dj * dj > (VR / G + 0.5) ** 2:
                    continue
                cc = (j + dj) * NX + i + di
                if not GR.free(li, cc, code):
                    return False
    return True


def astar(srcs, dsts, code, prefer=None, maxexp=400000):
    """srcs/dsts: sets of (layer, cell). returns path [(layer, cell)]"""
    tx = [(c % NX, c // NX) for _, c in dsts]
    def h(c):
        i, j = c % NX, c // NX
        return min(math.hypot(i - a, j - b) for a, b in tx) if len(tx) < 40 else 0
    pq = []; g = {}; par = {}
    for s in srcs:
        g[s] = 0; heapq.heappush(pq, (h(s[1]), 0, s))
    n = 0
    while pq:
        f, gc, s = heapq.heappop(pq)
        if gc > g.get(s, 1e18):
            continue
        if s in dsts:
            path = [s]
            while s in par:
                s = par[s]; path.append(s)
            return path[::-1]
        n += 1
        if n > maxexp:
            return None
        li, c = s
        i, j = c % NX, c // NX
        for di, dj, w in DIRS:
            ii, jj = i + di, j + dj
            if not (0 <= ii < NX and 0 <= jj < NY):
                continue
            cc = jj * NX + ii
            if not GR.free(li, cc, code):
                continue
            if di and dj and not (GR.free(li, j * NX + ii, code) or GR.free(li, jj * NX + i, code)):
                continue
            ns = (li, cc); ng = gc + w + (0.3 if prefer is not None and li != prefer else 0)
            if ns in par and False:
                continue
            p = par.get(s)
            if p is not None and p[0] == li:          # bend penalty
                pi, pj = p[1] % NX, p[1] // NX
                if (i - pi, j - pj) != (di, dj):
                    ng += 0.4
            if ng < g.get(ns, 1e18):
                g[ns] = ng; par[ns] = s; heapq.heappush(pq, (ng + h(cc), ng, ns))
        ns = (1 - li, c)
        ng = gc + VIA_COST
        if ng < g.get(ns, 1e18) and GR.free(1 - li, c, code) and via_ok(c, code) and c not in VIA_BLOCK:
            g[ns] = ng; par[ns] = s; heapq.heappush(pq, (ng + h(c), ng, ns))
    return None


def xy(c):
    return (X0 + (c % NX) * G, Y0 + (c // NX) * G)


def commit(path, code, w=TW):
    """turn a grid path into tracks/vias (merging straight runs)."""
    nets = B.FindNet(code) if False else None
    out = []
    k = 0
    while k < len(path) - 1:
        li, c = path[k]
        if path[k + 1][0] != li:
            v = pcbnew.PCB_VIA(B); x, y = xy(c)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR)); v.SetNetCode(code)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); B.Add(v); VIAS.append((x, y))
            r = VD / 2 + M
            for l2 in (0, 1):
                GR.block(l2, x - r, y - r, x + r, y + r, code, (x, y, r), trk=True)
            k += 1; continue
        m = k + 1
        d = None
        while m < len(path) and path[m][0] == li:
            a, b = xy(path[m - 1][1]), xy(path[m][1])
            dd = (round((b[0] - a[0]) / G), round((b[1] - a[1]) / G))
            if d is None:
                d = dd
            elif dd != d:
                break
            m += 1
        m -= 1
        a, b = xy(c), xy(path[m][1])
        t = pcbnew.PCB_TRACK(B); t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        t.SetWidth(MM(w)); t.SetLayer(LAY[li]); t.SetNetCode(code); B.Add(t)
        add_seg(li, a, b, w, code)
        out.append(t)
        k = m
    return out


def pad_cells(pd):
    """grid cells on the pad copper (where a track may end), per layer."""
    bb = pd.GetBoundingBox(); out = set()
    th = pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
    x1, y1, x2, y2 = TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())
    sh = min(x2 - x1, y2 - y1) / 2
    for li, L in enumerate(LAY):
        if not (th or pd.IsOnLayer(L)):
            continue
        for i in range(gi(x1 + min(0.15, sh * 0.6)), gi(x2 - min(0.15, sh * 0.6)) + 1):
            for j in range(gj(y1 + min(0.15, sh * 0.6)), gj(y2 - min(0.15, sh * 0.6)) + 1):
                if pd.HitTest(pcbnew.VECTOR2I(MM(X0 + i * G), MM(Y0 + j * G))):
                    out.add((li, j * NX + i))
        if not any(l == li for l, _ in out):
            c = pd.GetPosition(); out.add((li, gj(TO(c.y)) * NX + gi(TO(c.x))))
    return out


def net_cells(code):
    """cells already belonging to the net (tracks, vias): used to grow a tree."""
    s = set()
    for t in B.GetTracks():
        if t.GetNetCode() != code:
            continue
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition(); c = gj(TO(p.y)) * NX + gi(TO(p.x)); s |= {(0, c), (1, c)}
        elif t.GetLayer() in LAY:
            li = LAY.index(t.GetLayer()); a, b = t.GetStart(), t.GetEnd()
            n = max(1, int(TO((b - a).EuclideanNorm()) / G))
            for k in range(n + 1):
                x = TO(a.x + (b.x - a.x) * k / n); y = TO(a.y + (b.y - a.y) * k / n)
                s.add((li, gj(y) * NX + gi(x)))
    return s


def route_net(pads, code, prefer=None, w=TW, anchor=None):
    """connect pads (list) into a tree; anchor = extra target cells (e.g. a pour)."""
    pads = list(pads)
    tree = set(anchor) if anchor else set()
    if B.FindNet(code) is None and False:
        pass
    if NETNAME.get(code) in ('/ITH', '/FB', '/SS'):
        tree |= net_cells(code)
    if not tree:
        tree = pad_cells(pads.pop(0))
    ok = True
    while pads:
        # nearest remaining pad first
        best = None
        for pd in pads:
            c = pd.GetPosition(); i, j = gi(TO(c.x)), gj(TO(c.y))
            d = min(abs((cc % NX) - i) + abs((cc // NX) - j) for _, cc in tree) if len(tree) < 4000 else 0
            if best is None or d < best[0]:
                best = (d, pd)
        pd = best[1]; pads.remove(pd)
        src = pad_cells(pd)
        if src & tree:
            tree |= src; continue
        path = astar(src, tree, code, prefer)
        if not path:
            print('   FAIL', pd.GetParentFootprint().GetReference(), pd.GetNumber(), pd.GetNetname())
            ok = False; continue
        commit(path, code, w)
        tree |= set(path) | src
    return ok


# ------------------------------------------------------------------ plane fan-out vias
def fanout(pd, code, plane_layers_ok=True):
    """short stub from an SMD pad to a new via (GND / VIN to the inner planes)."""
    li = 0 if pd.IsOnLayer(pcbnew.F_Cu) else 1
    c = pd.GetPosition(); px, py = TO(c.x), TO(c.y)
    bb = pd.GetBoundingBox(); hw, hh = TO(bb.GetWidth()) / 2, TO(bb.GetHeight()) / 2
    best = None
    for r in [0.0, 0.6, 0.9, 1.2, 1.5, 1.9, 2.4, 3.0]:
        for a in range(0, 360, 30):
            x = px + (hw + r) * math.cos(math.radians(a)) if r else px
            y = py + (hh + r) * math.sin(math.radians(a)) if r else py
            if r == 0:
                continue
            i, j = gi(x), gj(y); cc = j * NX + i
            if not (0 <= i < NX and 0 <= j < NY) or cc in VIA_BLOCK:
                continue
            if via_ok(cc, code):
                OV.setdefault(code, set()).update(pad_cells(pd))
                path = astar({x for x in pad_cells(pd) if x[0] == li}, {(li, cc)}, code, maxexp=4000)
                if path:
                    best = (path, cc); break
        if best:
            break
    if not best:
        print('   FANOUT FAIL', pd.GetParentFootprint().GetReference(), pd.GetNumber()); return False
    path, cc = best
    commit(path, code, 0.4)
    x, y = xy(cc)
    v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR)); v.SetNetCode(code)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); B.Add(v); VIAS.append((x, y))
    r = VD / 2 + M
    for l2 in (0, 1):
        GR.block(l2, x - r, y - r, x + r, y + r, code, (x, y, r), trk=True)
    return True


def pads_of(netname):
    n = net(netname); out = []
    for f in B.Footprints():
        for pd in f.Pads():
            if pd.GetNetCode() == n.GetNetCode():
                out.append(pd)
    return out


def P(ref, num):
    return next(p for p in FP[ref].Pads() if p.GetNumber() == str(num))


def main():
    t0 = time.time()
    make_zones()
    for f in B.Footprints():          # THT holes: no vias inside
        for pd in f.Pads():
            if pd.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) or f.GetReference().startswith(('H', 'HS')):
                bb = pd.GetBoundingBox()
                for i in range(gi(TO(bb.GetLeft()) - 0.8), gi(TO(bb.GetRight()) + 0.8) + 1):
                    for j in range(gj(TO(bb.GetTop()) - 0.8), gj(TO(bb.GetBottom()) + 0.8) + 1):
                        VIA_BLOCK.add(j * NX + i)
    for f in B.Footprints():          # no via inside / next to an SMD pad (solder wicking)
        for pd in f.Pads():
            if pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not (f.GetReference() == 'U1' and pd.GetNumber() == '39'):
                bb = pd.GetBoundingBox(); mg = 0.3 if f.GetReference() == 'U1' else 0.55
                for i in range(gi(TO(bb.GetLeft()) - mg), gi(TO(bb.GetRight()) + mg) + 1):
                    for j in range(gj(TO(bb.GetTop()) - mg), gj(TO(bb.GetBottom()) + mg) + 1):
                        VIA_BLOCK.add(j * NX + i)
    build_grid()
    # escape stubs for fine-pitch pads (cells along the pad axis, outward; GND pins of U1 also inward to the EP)
    for f in B.Footprints():
        fc = f.GetPosition()
        for pd in f.Pads():
            if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or not pd.GetNetCode():
                continue
            bb = pd.GetBoundingBox(); w, h = TO(bb.GetWidth()), TO(bb.GetHeight())
            if min(w, h) > 0.62 or max(w, h) > 2.5:
                continue
            c = pd.GetPosition(); px, py = TO(c.x), TO(c.y); li = 0 if pd.IsOnLayer(pcbnew.F_Cu) else 1
            if w > h:
                d = 1 if px > TO(fc.x) else -1; ax = 0
            else:
                d = 1 if py > TO(fc.y) else -1; ax = 1
            dirs = [-d] if (f.GetReference() == 'U1' and pd.GetNetname() == 'GND') else [d]
            for dd in dirs:
                for k in range(0, int((max(w, h) / 2 + 1.3) / G) + 1):
                    x = px + (dd * k * G if ax == 0 else 0); y = py + (dd * k * G if ax == 1 else 0)
                    OV.setdefault(pd.GetNetCode(), set()).add((li, gj(y) * NX + gi(x)))
                    GR.own[li].setdefault(gj(y) * NX + gi(x), set()).add(pd.GetNetCode())
    # U1 exposed pad: 3 x 5 thermal vias to the GND planes
    gcode = net('GND').GetNetCode(); u = FP['U1'].GetPosition()
    for dx in (-0.8, 0.0, 0.8):
        for dy in (-1.8, -0.9, 0.0, 0.9, 1.8):
            v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(u.x + MM(dx), u.y + MM(dy))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
            v.SetNetCode(gcode); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); B.Add(v); VIAS.append((TO(u.x) + dx, TO(u.y) + dy))
            x, y = TO(u.x) + dx, TO(u.y) + dy; rr = 0.3 + M
            for l2 in (0, 1):
                GR.block(l2, x - rr, y - rr, x + rr, y + rr, gcode, (x, y, rr), trk=True)
    print('grid', round(time.time() - t0, 1), 's')
    SKIP = {'GND', '/VIN', 'Net-(J1-Pin_1)'}
    POWER_POUR = {'/SW', '/SENSEP', '/VOUT', '/VIN_RAW'}
    # 1. GND / VIN fan-out of SMD pads that are not on a pour
    POURED = {('/VIN', 'B'), }
    for nn, plane in (('GND', None), ('/VIN', None)):
        code = net(nn).GetNetCode()
        for pd in pads_of(nn):
            if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            ref = pd.GetParentFootprint().GetReference()
            if ref.startswith(('CIN', 'CHF', 'COUT', 'U1')) and nn == 'GND' and ref != 'U1':
                continue          # on the B.Cu / F.Cu GND pour already
            if nn == '/VIN' and ref.startswith(('CIN', 'CHF')):
                continue
            if ref == 'U1' and nn == '/VIN':
                continue
            if ref == 'U1':
                if pd.GetNumber() != '39':
                    route_net([pd], code, w=0.25, anchor=pad_cells(P('U1', 39)))
                continue
            fanout(pd, code)
    print('fanout', round(time.time() - t0, 1), 's')
    # 2. signal nets, shortest first
    nets = {}
    for f in B.Footprints():
        for pd in f.Pads():
            n = pd.GetNetname()
            if n and n not in SKIP and not n.startswith('unconnected'):
                nets.setdefault(n, []).append(pd)
    import os
    FIRST = os.environ.get('FIRST', '/SW,/BOOST,/TG,/BG,/SS,/VOUT,/ITH').split(',')
    order = [n for n in FIRST if n in nets] + sorted([n for n in nets if n not in FIRST], key=lambda n: (n in POWER_POUR, len(nets[n])))
    fails = 0
    for n in order:
        pads = nets[n]
        code = net(n).GetNetCode()
        anchor = None
        if n in POWER_POUR:
            pts = next(p for nn, L, p in POUR if nn == n)
            anchor = set()
            for i in range(NX):
                for j in range(NY):
                    pass
            big = [pd for pd in pads if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or TO(pd.GetBoundingBox().GetWidth()) > 2.5]
            pads = [pd for pd in pads if pd not in big]
            anchor = set().union(*[pad_cells(pd) for pd in big])
            xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
            for i in range(gi(min(xs)), gi(max(xs)) + 1):
                for j in range(gj(min(ys)), gj(max(ys)) + 1):
                    x, y = X0 + i * G, Y0 + j * G
                    if inside(pts, x, y) and dist_poly(pts, x, y) > 0.5 and GR.free(0, j * NX + i, code):
                        anchor.add((0, j * NX + i))
            if n == '/SW':
                anchor |= pad_cells(P('Q2', 2))
        if len(pads) + (1 if anchor else 0) < 2:
            continue
        fine = any(min(TO(p.GetBoundingBox().GetWidth()), TO(p.GetBoundingBox().GetHeight())) < 0.45 for p in nets[n])
        if not route_net(pads, code, anchor=anchor, w=0.2 if fine else TW):
            fails += 1
    print('fails', fails, 'time', round(time.time() - t0, 1), 's')
    # remove vias that only touch one layer (dangling)
    for v in [t for t in B.GetTracks() if t.GetClass() == 'PCB_VIA']:
        p = v.GetPosition(); lay = set()
        for t in B.GetTracks():
            if t.GetClass() != 'PCB_VIA' and t.GetNetCode() == v.GetNetCode() and (t.GetStart() == p or t.GetEnd() == p):
                lay.add(t.GetLayer())
        if len(lay) == 1 and NETNAME.get(v.GetNetCode()) not in ('GND', '/VIN', '/VOUT'):
            other = pcbnew.B_Cu if pcbnew.F_Cu in lay else pcbnew.F_Cu
            onpad = any(pd.GetNetCode() == v.GetNetCode() and pd.IsOnLayer(other) and pd.HitTest(p)
                        for f in B.Footprints() for pd in f.Pads())
            if not onpad:
                print('   dangling via', NETNAME.get(v.GetNetCode()), TO(p.x), TO(p.y))
    B.Save(sys.argv[1])


main()
