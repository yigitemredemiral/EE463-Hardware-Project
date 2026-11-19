# Bill of materials (RevF2)

**74 parts in 48 lines, 82.37 USD** for one board (DigiKey US cut-tape prices checked on 2026-11-19, qty-1 break unless noted; shipping, VAT and duty not included). Course budget: 100 USD per group.

| File | Use |
|---|---|
| `BOM_course_format.csv` / `.tsv` | Same columns as the course sponsorship sheet. Paste the `.tsv` into the copied sheet at cell A1; totals are formulas. |
| `BOM_full.csv` | Engineering BOM: references, values, footprints, manufacturer, datasheet links, notes. |

## Course rules applied

- **No Israel-made parts.** Vishay parts of RevF1 were replaced: shunt WSL25124L000FEA -> Yageo PA2512FKF7W0R004E (same 3.05 x 3.68 mm land pattern), snubber resistor CRCW12062R20FKEAHP -> Panasonic ERJ-P08J2R2V (anti-surge, 0.66 W; snubber dissipation 1 nF x 48 V^2 x 94.3 kHz = 0.22 W), BAT54-E3-08 -> onsemi BAT54LT1G (same SOT-23 pinout). No Vishay / Vitramon / Dale / Siliconix / Sfernice / BCcomponents part is left. Watch DigiKey substitutions: they often offer Vishay Vitramon capacitors.
- **0805 or larger.** All resistors and capacitors are 0805 or larger except: RCSO1, RERR1, RFBT1, ROVB1, RRUNT1, RSETT1. These sit in the densest routing next to the controller and the op amps; enlarging them would need re-routing. Their 0603 part numbers are standard Yageo values, linked as DigiKey searches (stock not checked one by one) (course rule: 0603 allowed for a few parts). No 0402.
- **Assembly:** reflow oven + paste dispenser (no stencil). Finest pitch: LTC3895 TSSOP-38, 0.5 mm.

## Order early / stock warnings

- `XAL1510-333MED` (L1): Coilcraft direct: 6.37 EUR at qty 1, in stock (2026-11-19); not sold by DigiKey. 2nd source on the same dual footprint: Wurth 74439370330 (DigiKey 7.27 USD, restock Jan-2027)
- `1715721` (J1, J2): DigiKey restock 03-Dec-2026
- `BAT46WJ,115` (DVIN1): backordered at DigiKey: order early or check Mouser/Farnell
- `RT0805BRD07100RL` (RCSN1, RCSP1): DigiKey 0 stock: order early; alt. Panasonic ERA-6AEB101V (0.1% 0805, not checked)

## Changes against the RevF1 BOM

| Ref | RevF1 | RevF2 | Reason |
|---|---|---|---|
| RS1 | Vishay WSL25124L000FEA | Yageo PA2512FKF7W0R004E | Israel-made rule; same land pattern |
| RSN1 | Vishay CRCW12062R20FKEAHP | Panasonic ERJ-P08J2R2V | Israel-made rule |
| DAUX1, DCL1 | Vishay BAT54-E3-08 | onsemi BAT54LT1G | Israel-made rule |
| 24 of the 30 0603 R/C | 0603 | 0805 (moved 0-0.38 mm on the PCB, DRC clean) | course package rule |
| CIN1-10 | TDK C3225X7R2A225K230AB | Samsung CL32B225KCJSNNE | TDK out of stock (same 2.2 uF / 100 V / 1210 X7R) |
| CINB1-3 | Panasonic EEU-FR2A101 | Rubycon 100ZLH100MEFC10X20 | out of stock (same 100 uF / 100 V, D10, P5) |
| CDRV1, CBOOT1, CREF1/CAUX1, CITH1, CSN1 | Murata/TDK (obsolete or not on DigiKey) | equivalents | availability |
| RGH1, RGL1, RERR1 | Yageo RC0805 | Panasonic ERJ-6 | Yageo value out of stock |
| CCATH1 | - | Yageo CC1206KKX7R0BB105 1 uF / 100 V | LM74700 CATHODE capacitor (hot-plug), see PCB notes |

## Spares

Compensation B parts (3.9 k, 68 nF C0G, 1 nF C0G) are bought for the line/load transient bonus. About 18 USD of the budget is left; useful extra spares: one more of each MOSFET and the LTC3895.

