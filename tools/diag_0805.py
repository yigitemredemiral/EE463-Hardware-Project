"""Show which copper items block the 0603 -> 0805 change of one part (prints the DRC findings of the plain swap).
Usage: python tools/diag_0805.py <board.kicad_pcb> REF [dx dy]"""
import json, os, shutil, subprocess, sys, tempfile
K = r'C:\Program Files\KiCad\10.0\bin'
HERE = os.path.dirname(os.path.abspath(__file__))
src, ref = sys.argv[1], sys.argv[2]
dx, dy = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0.0, 0.0)
work = tempfile.mkdtemp()
out = os.path.join(work, 't.kicad_pcb')
code = f'''
import sys, pcbnew
sys.path.insert(0, r"{HERE}")
from revf2_0805_ki import swap_one
b = pcbnew.LoadBoard(r"{src}")
fp = b.FindFootprintByReference("{ref}"); p0 = fp.GetPosition()
n = swap_one(b, fp); n.SetPosition(pcbnew.VECTOR2I(p0.x + pcbnew.FromMM({dx}), p0.y + pcbnew.FromMM({dy})))
pcbnew.SaveBoard(r"{out}", b)
'''
open(os.path.join(work, 'g.py'), 'w').write(code)
subprocess.run([os.path.join(K, 'python.exe'), os.path.join(work, 'g.py')], capture_output=True)
shutil.copy(src[:-10] + '.kicad_pro', out[:-10] + '.kicad_pro')
subprocess.run([os.path.join(K, 'kicad-cli.exe'), 'pcb', 'drc', '--refill-zones', '--format', 'json', '-o', out[:-10] + '.json', out], capture_output=True)
d = json.load(open(out[:-10] + '.json'))
for v in d['violations']:
    if v['type'] in ('shorting_items', 'clearance', 'courtyards_overlap', 'solder_mask_bridge'):
        print(v['type'], '|', ' || '.join(f"{i['description'][:70]} @({i['pos']['x']:.2f},{i['pos']['y']:.2f})" for i in v['items']))
print('unconnected', len(d['unconnected_items']))
