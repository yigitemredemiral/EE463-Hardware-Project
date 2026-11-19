#!/usr/bin/env bash
# RevF2 checks: schematic connectivity vs RevF1, ERC, DRC + schematic parity, LTspice drawing vs RevF1 netlist.
set -e
cd "$(dirname "$0")/.."
K="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
LT="/c/Program Files/ADI/LTspice/LTspice.exe"
P=hardware/kicad_RevF2/EE463_Buck_RevF2
mkdir -p build
"$K" sch export netlist $P.kicad_sch -o build/new.net >/dev/null
python tools/kinet.py hardware/kicad_RevF2/reference/RevF1_netlist.net build/new.net --ignore CCATH1 | tail -2
"$K" sch erc --severity-all -o build/erc.rpt $P.kicad_sch >/dev/null; grep "ERC messages" build/erc.rpt
"$K" pcb drc --schematic-parity --severity-all --format json -o build/drc.json $P.kicad_pcb >/dev/null
python -c "import json; d=json.load(open('build/drc.json')); print('DRC violations', len(d['violations']), '| unconnected', len(d['unconnected_items']), '| parity', len(d['schematic_parity']))"
( cd simulation/ltspice_RevF2 && "$LT" -netlist EE463_Buck_RevF2.asc && sleep 2 )
python tools/cmp_spice.py simulation/ltspice_RevF2/EE463_Buck_RevF2.net simulation/ltspice_RevF1_runs/RevF1_G_20V_90W.cir | tail -1
