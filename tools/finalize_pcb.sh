#!/usr/bin/env bash
# RevF2 PCB/schematic finalisation after the 0805 search (tools/revf2_0805.py -> build/opt.kicad_pcb):
#  1. CCATH1 placed on the Q3 drain pour (tools/add_ccath.py)
#  2. net /GND renamed to GND (the drawn schematic uses the GND power symbol)
#  3. footprint fields (value, MPN, manufacturer, datasheet, description) from tools/parts.py
#  4. schematic regenerated from the final PCB footprints, zones refilled, DRC + parity, footprint library saved
set -e
cd "$(dirname "$0")/.."
K="/c/Program Files/KiCad/10.0/bin"
P=hardware/kicad_RevF2/EE463_Buck_RevF2
cp build/opt.kicad_pcb build/f1.kicad_pcb; cp build/base.kicad_pro build/f1.kicad_pro
python tools/add_ccath.py build/f1.kicad_pcb build/f2.kicad_pcb 6f0c2a1e-5b7d-4c11-9a3e-2d8b4e7f1c01
cp build/f2.kicad_pcb $P.kicad_pcb
"$K/python.exe" tools/revf2_pcb.py gnd 2>&1 | grep -v -i swig || true
"$K/python.exe" tools/revf2_pcb.py fields 2>&1 | grep -v -i swig || true
bash build/mksch.sh ../$P.kicad_pcb > build/mksch.log 2>&1; head -4 build/mksch.log
"$K/kicad-cli.exe" pcb drc --refill-zones --save-board --schematic-parity --severity-all --format json -o build/drc_final.json $P.kicad_pcb > /dev/null
python -c "
import json, collections; d = json.load(open('build/drc_final.json'))
print('DRC', collections.Counter(v['type'] for v in d['violations']), '| unconnected', len(d['unconnected_items']), '| parity', collections.Counter(v['type'] for v in d['schematic_parity']))
for v in d['schematic_parity'][:12]: print('   ', v['description'][:110])"
