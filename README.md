# EE463 Hardware Project: 60 W Synchronous Buck Converter

METU EE463 Static Power Conversion I, Fall 2026, term project
([specification](https://github.com/odtu/EE463/blob/master/Hardware%20Project/EE463%20Hardware%20Project.md)).

20–48 V DC input, 12 V / 5 A (60 W) regulated output, closed-loop peak current-mode control, one input source,
own 4-layer PCB. Bonus targets: 90 W overload, 7.5 A-class current limit, reverse-polarity protection, efficiency,
line/load transient comparison.

| | |
|---|---|
| Topology | Synchronous buck, 94.3 kHz |
| Controller | Analog Devices LTC3895 (150 V, peak current mode), self-supplied from VIN and then from VOUT (EXTVCC) |
| Power stage | Infineon BSC040N08NS5 (high side), BSC026N08NS5 (low side), Coilcraft XAL1510-333 33 µH, 2 × 330 µF polymer |
| Protection | LM74700-Q1 ideal diode (reverse polarity), average current limit 7.88 A (LT6105 + LT6654 + LT1636), RUN/OVLO |
| PCB | 4 layers, 90 × 65 mm, KiCad 10 |
| Simulated efficiency | 97.3 % average at 60 W over 20/24/36/48 V *(simulation, not measured)* |

## Status (19 November 2026)

| Deadline | Item | Status |
|---|---|---|
| 22 Nov | Pre-report | Draft: [`reports/PreReport.md`](reports/PreReport.md) |
| 24–25 Nov | Feedback session | Schematic, PCB and simulations ready |
| 30 Nov | PCB files for sponsored production | Gerber/drill not generated yet (after the feedback session) |
| 4 Jan | Hardware demo | — |

Nothing has been ordered or sent to a manufacturer yet. No hardware measurement exists yet.

## Repository map

| Folder | Content |
|---|---|
| [`hardware/kicad_RevF4/`](hardware/kicad_RevF4/) | **Current board.** RevF2 schematic with the re-routed signals, constant-width power tracks, pad stitching pours and the course PCB-checker fixes. Passes the [course PCB checker](https://github.com/odtu/EE463/tree/master/Hardware%20Project/PCB-Checker) with 0 errors at 5 A and 7.5 A (only warning: 4 layers). Settings and waiver in `pcb_checker.json`. |
| [`hardware/kicad_RevF2/`](hardware/kicad_RevF2/) | KiCad 10 project. The schematic is drawn with wires (one A3 sheet, five blocks); the PCB is the RevF1 layout with 0805 parts, CCATH1 and the new part numbers. Printable copies: [schematic](hardware/kicad_RevF2/EE463_Buck_RevF2_schematic.pdf), [assembly top](hardware/kicad_RevF2/EE463_Buck_RevF2_assembly_top.pdf), [assembly bottom](hardware/kicad_RevF2/EE463_Buck_RevF2_assembly_bottom.pdf). |
| [`simulation/ltspice_RevF2/`](simulation/ltspice_RevF2/) | Drawn LTspice schematic of the final design (`EE463_Buck_RevF2.asc`) with its symbols and models. Open it in LTspice and run. |
| [`simulation/ltspice_RevF1_runs/`](simulation/ltspice_RevF1_runs/) | All RevF1 netlists, logs and scripts behind the numbers in the reports. |
| [`simulation/compensation_AB/`](simulation/compensation_AB/) | Loop-gain and transient comparison of compensation A and B. |
| [`calculations/`](calculations/) | Analytical design (duty cycle, ripple, stresses, losses, thermal). |
| [`bom/`](bom/) | Bill of materials in the course format, full BOM with datasheets, ordering notes. |
| [`reports/FinalReport/`](reports/FinalReport/) | Full report ([PDF](reports/FinalReport/EE463_Final_Report.pdf); design, circuit simulation, PCB and checker, 5-minute thermal analysis). Compile `main.tex` with pdfLaTeX; all numbers come from `values.tex`. PCB-checker reports in `pcb_checker/`. |
| [`simulation/analysis_RevF4/`](simulation/analysis_RevF4/) | Scripts behind the final report: LTspice batch runs, loss breakdown, loop gain, 4-layer thermal model, copper current flow. |
| [`reports/`](reports/) | Pre-report, control-loop section, figures. |
| [`docs/design_review/`](docs/design_review/) | Design review and revision notes (Turkish), RevD5E1 → RevF1 → RevF2. |
| [`tools/`](tools/) | Scripts that generate the schematic, the LTspice drawing, the BOM and run the checks. |

## Revision history

| Revision | Change |
|---|---|
| RevD5E1 | First complete design (Yasin): LTC3895, 145 kHz, Schottky reverse protection |
| RevF1 | Review and two rounds of changes: 94.3 kHz, BSC040 high side, compensation A, current limit 7.88 A, OVLO 58 V, LM74700 ideal diode, hot-loop capacitors, thermal vias, layout fixes |
| RevF2 | Readable schematic (KiCad and LTspice, drawn with wires); 24 of 30 former 0603 parts enlarged to 0805 (course rule) by moving them ≤ 0.38 mm, 6 resistors stay 0603; Vishay parts replaced (course rule: no Israel-made parts); CCATH1 1 µF / 100 V added at the LM74700 CATHODE (approved in the RevF1 review); BOM in the course format with prices and datasheets. ERC 0, DRC 0, parity 0. |
| **RevF4** | Signal re-route; constant track widths; pours instead of pad-to-via tracks; SW and Q2 source pours; course PCB-checker fixes (via-to-drill spacing, no vias in small pads, 0.4 mm via arrays at RS1 and Q2 sources). DRC 0, parity 0. |

## Checks

```bash
bash tools/run_checks.sh
```

- KiCad schematic connectivity = RevF1 netlist (net-by-net comparison), ERC, DRC with schematic parity.
- LTspice drawing: LTspice's own netlist of the `.asc` compared element by element with the RevF1 simulation netlist.

## Tools used

KiCad 10.0, LTspice 26.0, Python 3.12 (numpy, matplotlib). AI tools (Claude) were used for simulation scripting,
schematic drawing and checks; every result was checked against simulation, the datasheets or the netlist, as the
course rules require.
