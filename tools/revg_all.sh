#!/usr/bin/env bash
# RevG: netlist -> placement -> routing (rip-up loop) -> DRC/parity -> course PCB checker
set -e
cd "$(dirname "$0")/.."
K="/c/Program Files/KiCad/10.0/bin"; P=hardware/kicad_RevG/EE463_Buck_RevG
C="${CHECKER:-../EE463/Hardware Project/PCB-Checker}"
"$K/kicad-cli.exe" sch export netlist -o build/g.net $P.kicad_sch >/dev/null
"$K/python.exe" -u tools/revg_place.py build/g.net hardware/kicad_RevF4/EE463_Buck_RevF4.kicad_pcb build/g_placed.kicad_pcb 2>&1 | grep -v -i swig | tail -1
python tools/revg_iter.py | tail -2
cp build/g_best.kicad_pcb $P.kicad_pcb
"$K/kicad-cli.exe" pcb drc --refill-zones --save-board --schematic-parity --severity-error --format json -o build/drc_full.json $P.kicad_pcb >/dev/null 2>&1
python -c "import json; d=json.load(open('build/drc_full.json')); print('DRC errors', len(d['violations']), '| unconnected', len(d['unconnected_items']), '| parity', len(d['schematic_parity']))"
mkdir -p build/chk
for m in "" "--overload"; do
  "$K/python.exe" "$C/check_pcb.py" $P.kicad_pcb $m -o build/chk/check${m:+_overload}.html 2>&1 | grep -v -i swig | grep -E "MUST|SHOULD|CHECK" || true
done
