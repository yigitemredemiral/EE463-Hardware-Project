"""Place CCATH1 (1 uF / 100 V X7R 1206, VIN-GND) on the Q3 drain pour, with a GND via to the solid In1 plane.
Approved in the RevF1 review (hot plug: LM74700 CATHODE peak 67 V -> 53 V in simulation).
Candidate positions are generated with KiCad's python and checked with kicad-cli DRC; the first clean one is kept.
Usage: python tools/add_ccath.py <in.kicad_pcb> <out.kicad_pcb> <symbol-uuid>"""
import json, os, shutil, subprocess, sys, glob
from concurrent.futures import ThreadPoolExecutor

K = r'C:\Program Files\KiCad\10.0\bin'
BAD = {'shorting_items', 'clearance', 'courtyards_overlap', 'solder_mask_bridge', 'hole_clearance',
       'copper_edge_clearance', 'track_dangling', 'via_dangling', 'starved_thermal', 'silk_over_copper', 'silk_overlap',
       'drill_out_of_range', 'hole_to_hole'}

GEN = r'''
import sys, json, pcbnew, os
src, outdir, uid, cands = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
mm = pcbnew.FromMM
for i, (x, y, rot, vdx, vdy) in enumerate(cands):
    b = pcbnew.LoadBoard(src)
    fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Capacitor_SMD.pretty", "C_1206_3216Metric")
    fp.SetParent(b); fp.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_1206_3216Metric"))
    fp.SetReference("CCATH1"); fp.SetValue("1u/100V X7R")
    fp.SetPath(pcbnew.KIID_PATH("/" + uid))
    fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    vin = b.FindNet("/VIN"); gnd = b.FindNet("GND") or b.FindNet("/GND")
    for p in fp.Pads():
        p.SetNet(vin if p.GetNumber() == "1" else gnd)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); fp.Reference().SetTextThickness(mm(0.12))
    fp.Reference().SetPosition(pcbnew.VECTOR2I(mm(x), mm(y - 1.6))); fp.Value().SetVisible(False)
    b.Add(fp)
    p2 = [p for p in fp.Pads() if p.GetNumber() == "2"][0].GetPosition()
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(p2.x + mm(vdx), p2.y + mm(vdy)))
    v.SetDrill(mm(0.3)); v.SetWidth(mm(0.6)); v.SetNet(gnd); b.Add(v)
    t = pcbnew.PCB_TRACK(b); t.SetStart(p2); t.SetEnd(v.GetPosition()); t.SetWidth(mm(0.5))
    t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t)
    pcbnew.SaveBoard(os.path.join(outdir, "c%03d.kicad_pcb" % i), b)
'''


def drc(pcb):
    rep = pcb[:-10] + '.json'
    subprocess.run([os.path.join(K, 'kicad-cli.exe'), 'pcb', 'drc', '--refill-zones', '--format', 'json', '-o', rep, pcb], capture_output=True)
    d = json.load(open(rep))
    return sum(v['type'] in BAD for v in d['violations']) + len(d['unconnected_items'])


def main(src, dst, uid):
    work = os.path.join(os.path.dirname(os.path.abspath(dst)), 'ccath_work'); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    pro = src[:-10] + '.kicad_pro'
    base = os.path.join(work, 'base.kicad_pcb'); shutil.copy(src, base); shutil.copy(pro, base[:-10] + '.kicad_pro')
    b0 = drc(base); print('baseline', b0, flush=True)
    cands = []
    for y in (98.2, 98.6, 99.0, 98.0, 99.4):
        for x in (116.0, 117.0, 115.0, 118.0, 114.0, 113.0, 112.0, 111.0, 110.0):
            for rot in (0, 180):
                for vdx, vdy in ((0, 1.5), (0, -1.4), (1.6, 0), (-1.6, 0)):
                    cands.append((x, y, rot, vdx, vdy))
    kp = os.path.join(work, 'gen.py'); open(kp, 'w').write(GEN)
    for start in range(0, len(cands), 24):
        chunk = cands[start:start + 24]
        cdir = os.path.join(work, f'b{start}'); os.makedirs(cdir)
        subprocess.run([os.path.join(K, 'python.exe'), kp, base, cdir, uid, json.dumps(chunk)], capture_output=True)
        files = sorted(glob.glob(os.path.join(cdir, 'c*.kicad_pcb')))
        for f in files:
            shutil.copy(pro, f[:-10] + '.kicad_pro')
        with ThreadPoolExecutor(8) as ex:
            errs = list(ex.map(drc, files))
        print(start, errs, flush=True)
        ok = [i for i, e in enumerate(errs) if e <= b0]
        if ok:
            i = ok[0]; shutil.copy(files[i], dst); print('placed', chunk[i]); return chunk[i]
    print('no clean position found'); return None


if __name__ == '__main__':
    main(*sys.argv[1:4])
