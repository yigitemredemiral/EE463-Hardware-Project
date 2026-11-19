# Bill of materials (RevF2)

**74 parts used, 1173 pieces bought (MOQ), 48 lines, 80.91 USD** for one board (DigiKey US cut-tape prices, or Ozdisan prices for the lines with a Turkish link, checked on 2026-11-19; shipping, VAT and duty not included). Course budget: 100 USD per group.

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
- `BAT46WJ,115` (DVIN1): Ozdisan: 6562 in stock (DigiKey backordered)

## Turkish stock (Ozdisan, checked 2026-11-19)

27 of 48 lines are in stock at Ozdisan (link in the "Turkish Supplier Link" column). Where the DigiKey part was not stocked in Turkey, it was replaced by an equivalent that is (same value, package, tolerance or better, dielectric class, voltage/power). Prices of these lines are Ozdisan prices (USD, VAT excluded); the quantity is rounded up to the Ozdisan minimum order (for example 100 pcs for Royal Ohm resistors, a few cents in total). Not available in Turkey, bought from DigiKey / Coilcraft: the ADI ICs, LM74700, the MOSFETs, XAL1510, OS-CON, Rubycon, Phoenix terminals, the shunt, 100 V 0805 X7R (100 nF, 22 nF), C0G 1 nF/100 V and 27 nF, 4.7 Ohm 1%, the 2.2 Ohm pulse resistor and the 0.1% 140k / 11.8k. DAUX1/DCL1 use the Hottech BAT54S (dual, series): diode 1 sits on pins 1/3 exactly like the single BAT54, pin 2 is a no-connect pad on the PCB.

| Part | Replaces | Ozdisan |
|---|---|---|
| BAT54S-HT (DAUX1, DCL1) | BAT54LT1G | [link](https://www.ozdisan.com/p/schottky-diyotlar-385/hottech-bat54s-ht-417220) |
| BAT46WJ,115 (DVIN1) | (same part) | [link](https://www.ozdisan.com/p/schottky-diyotlar-385/nexperia-bat46wj-115-609944) |
| CC0805KKX7R7BB105 (CAUX1, CREF1) | C2012X7R1C105K085AC | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/yageo-cc0805kkx7r7bb105-504015) |
| CC0805KKX7R8BB105 (CBOOT1) | C2012X7R1E105K125AB; | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/yageo-cc0805kkx7r8bb105-576600) |
| CL31B105KCHNNNE (CCATH1) | CC1206KKX7R0BB105; | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/samsung-cl31b105kchnnne-382908) |
| CL21C103JBFNNNE (CCS1, CERR1) | C2012C0G1H103J060AA | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/samsung-cl21c103jbfnnne-353899) |
| CL21A475KAQNNNE (CDRV1) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/samsung-cl21a475kaqnnne-441542) |
| GRM32ER72A225KA35L (CIN1, CIN2, CIN3, CIN4, CIN5, CIN6, CIN7, CIN8, CIN9, CIN10) | CL32B225KCJSNNE | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/murata-grm32er72a225ka35l-1589679) |
| CL21C471JBANNNC (CITHP1) | GRM2165C1H471JA01D; | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/samsung-cl21c471jbannnc-5654) |
| CC0805JRNPO9BN102 (CRUN1, CSENSE1) | GRM2165C1H102JA01D; | [link](https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/yageo-cc0805jrnpo9bn102-749103) |
| TC0525B1000T5G (RCSN1, RCSP1) | RT0805BRD07100RL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-tc0525b1000t5g-700116) |
| RT0603BRD072KL (RCSO1) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/yageo-rt0603brd072kl-625691) |
| 0603SAF2002T5E (RERR1) | RC0603FR-0720KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0603saf2002t5e-353309) |
| TC0525B1002T5G (RFBB1) | RT0805BRD0710KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-tc0525b1002t5g-700129) |
| 0805S8F2432T5E (RFREQ1) | RC0805FR-0724K3L | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f2432t5e-505549) |
| CQ05S8F220KT5E (RGL1) | ERJ-6RQF2R2V | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-cq05s8f220kt5e-587991) |
| RC0805FR-07100KL (RGSH1, RGSL1) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/yageo-rc0805fr-07100kl-460162) |
| 0805S8F1500T5E (RISO1) | RC0805FR-07150RL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f1500t5e-335038) |
| 0805S8F8201T5E (RITH1) | RC0805FR-078K2L | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f8201t5e-31100) |
| 0805S8F1005T5E (RLEAK1) | RC0805FR-0710ML | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f1005t5e-35616) |
| RC0603FR-0717K4L (ROVB1) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/yageo-rc0603fr-0717k4l-618013) |
| 0805S8F8253T5E (ROVT1) | RC0805FR-07825KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f8253t5e-505666) |
| 0805S8F5113T5E (RPG1) | RC0805FR-07511KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f5113t5e-505648) |
| 0805S8F1002T5E (RRUNB1) | RC0805FR-0710KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f1002t5e-30240) |
| 0603SAF1303T5E (RRUNT1) | RC0603FR-07130KL | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0603saf1303t5e-359810) |
| RT0805BRD0712KL (RSETB1) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/yageo-rt0805brd0712kl-814018) |
| 0805S8F3901T5E ((spare)) | (same part) | [link](https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0805s8f3901t5e-35627) |

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

Compensation B parts (3.9 k, 68 nF C0G, 1 nF C0G) are bought for the line/load transient bonus. About 19 USD of the budget is left; useful extra spares: one more of each MOSFET and the LTC3895.

