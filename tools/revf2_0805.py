"""0603 -> 0805 conversion with a small placement search.

Run with the normal Python: python tools/revf2_0805.py <in.kicad_pcb> <out.kicad_pcb>
(the .kicad_pro with the board's design rules is copied next to every candidate).

For each 0603 part: swap to the KiCad stock 0805 footprint at the same place and try small shifts (track ends stay
inside the larger 0805 pad, so connectivity is kept). Every candidate board is checked with kicad-cli DRC (zones
refilled). The first candidate that adds no copper error (short, clearance, courtyard, mask bridge, unconnected,
dangling track) is kept. Parts with no clean position stay 0603 and are listed in <out>_0805_log.json."""
import os, sys, json, shutil, subprocess, glob
from concurrent.futures import ThreadPoolExecutor

K = r'C:\Program Files\KiCad\10.0\bin'
HERE = os.path.dirname(os.path.abspath(__file__))
BAD = {'shorting_items', 'clearance', 'courtyards_overlap', 'solder_mask_bridge', 'hole_clearance',
       'copper_edge_clearance', 'track_dangling', 'starved_thermal', 'via_dangling'}
SHIFTS = [(0, 0)] + [(dx, dy) for r in (0.127, 0.254, 0.381) for dx in (-r, 0, r) for dy in (-r, 0, r) if (dx, dy) != (0, 0)]

KIPY = r'''
import sys, os, json, pcbnew
sys.path.insert(0, r"%s")
from revf2_0805_ki import swap_one
src, ref, outdir, shifts = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
b = pcbnew.LoadBoard(src)
fp = b.FindFootprintByReference(ref); p0 = fp.GetPosition()
new = swap_one(b, fp)
for i, (dx, dy) in enumerate(shifts):
    new.SetPosition(pcbnew.VECTOR2I(p0.x + pcbnew.FromMM(dx), p0.y + pcbnew.FromMM(dy)))
    pcbnew.SaveBoard(os.path.join(outdir, 'c%%02d.kicad_pcb' %% i), b)
''' % HERE


def copper(pcb):
    rep = pcb[:-10] + '.json'
    subprocess.run([os.path.join(K, 'kicad-cli.exe'), 'pcb', 'drc', '--refill-zones', '--format', 'json', '-o', rep, pcb],
                   capture_output=True)
    d = json.load(open(rep))
    return sum(v['type'] in BAD for v in d['violations']) + len(d['unconnected_items'])


def main(src, dst):
    pro = src[:-10] + '.kicad_pro'
    work = os.path.join(os.path.dirname(os.path.abspath(dst)), 'opt_work'); os.makedirs(work, exist_ok=True)
    state = os.path.join(work, 'state.kicad_pcb'); shutil.copy(src, state); shutil.copy(pro, state[:-10] + '.kicad_pro')
    base = copper(state); print('baseline copper errors', base, flush=True)
    import re
    txt = open(src, encoding='utf-8').read()
    refs = sorted(set(re.findall(r'\(footprint "(?:Resistor|Capacitor)_SMD:[RC]_0603_1608Metric".*?\(property "Reference" "([^"]+)"', txt, re.S)))
    log = {}
    for ref in refs:
        cdir = os.path.join(work, ref); shutil.rmtree(cdir, ignore_errors=True); os.makedirs(cdir)
        kp = os.path.join(work, 'gen.py'); open(kp, 'w').write(KIPY)
        subprocess.run([os.path.join(K, 'python.exe'), kp, state, ref, cdir, json.dumps(SHIFTS)], capture_output=True)
        cands = sorted(glob.glob(os.path.join(cdir, 'c*.kicad_pcb')))
        for c in cands:
            shutil.copy(pro, c[:-10] + '.kicad_pro')
        with ThreadPoolExecutor(8) as ex:
            errs = list(ex.map(copper, cands))
        pick = next((i for i, e in enumerate(errs) if e <= base), None)
        if pick is None:
            log[ref] = {'result': 'kept 0603', 'errors': min(errs) - base}
        else:
            shutil.copy(cands[pick], state); log[ref] = {'result': '0805', 'shift_mm': SHIFTS[pick]}
        print(ref, log[ref], flush=True)
        shutil.rmtree(cdir, ignore_errors=True)
    shutil.copy(state, dst)
    json.dump(log, open(dst[:-10] + '_0805_log.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
