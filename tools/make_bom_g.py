"""RevG BOM -> bom/EE463_Buck_RevG_BOM.xlsx. Stock: DigiKey, checked 2026-11-26 (qty-1 prices, USD)."""
import collections, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

DK = 'https://www.digikey.com/en/products/result?keywords='
# ref -> (value, MPN, maker, package, description, stock, unit price, url, note)
L = [
 ('U1', 'LTC3895', 'LTC3895IFE#PBF', 'Analog Devices', 'TSSOP-38', '150 V synchronous buck controller', 470, 17.69, ''),
 ('U2', 'LT6105', 'LT6105IMS8#PBF', 'Analog Devices', 'MSOP-8', 'Current-sense amplifier (CL loop, optional)', 2163, 4.56, ''),
 ('U3', 'LT1636', 'LT1636IS8#PBF', 'Analog Devices', 'SO-8', 'Op amp, CL integrator (optional)', 443, 7.79, ''),
 ('U4', 'LT6654-1.25', 'LT6654AIS6-1.25#TRMPBF', 'Analog Devices', 'TSOT-23-6', '1.25 V reference (CL loop, optional)', 147, 8.74, 'low stock'),
 ('U5', 'LM74700-Q1', 'LM74700QDBVRQ1', 'Texas Instruments', 'SOT-23-6', 'Ideal-diode controller', 2228, 2.54, ''),
 ('Q1 Q2 Q3', 'IPP040N08NF2S', 'IPP040N08NF2SAKMA1', 'Infineon', 'TO-220', 'N-MOSFET 80 V 4 mOhm (all three the same)', 685, 2.89, ''),
 ('HS1 HS2', 'SK 104 38,1 STC', 'SK 104 38,1 STC', 'Fischer Elektronik', 'TO-220 PCB heatsink', 'Heatsink 11 K/W, solder pins (Q1, Q2) + M3 screw/nut', 865, 1.90, 'DigiKey Marketplace'),
 ('L1', '33 uH', 'XAL1510-333MED', 'Coilcraft', '15x15 mm', 'Power inductor 33 uH, Isat 16.7 A', 'Coilcraft direct (not DigiKey)', 6.50, 'stock: check coilcraft.com'),
 ('RS1', '4 mOhm 2 W', 'PA2512FKF7W0R004E', 'Yageo', '2512', 'Current-sense shunt 1%', 9657, 0.96, ''),
 ('F1', '8 A T', '0154008.DR', 'Littelfuse', 'OMNI-BLOK 154 SMD', 'Input fuse 8 A time-lag 125 V, replaceable Nano2 in holder', 7829, 3.00, 'NEW; spare fuse: 0452008.MRL'),
 ('J1 J2', 'MKDS 2-pos', '1715721', 'Phoenix Contact', '5.08 mm', 'Terminal block (VIN, VOUT)', 0, 1.16, 'backorder, 250 due 30-Nov-2026'),
 ('CINB1 CINB2 CINB3', '100u/100V', '100ZLH100MEFC10X20', 'Rubycon', 'radial 10x20', 'Input electrolytic', 175736, 1.09, ''),
 ('CIN1..CIN10', '2.2u/100V X7R', 'C1210C225K1RACTU', 'KEMET', '1210', 'Input MLCC (no 0805 at 100 V/2.2 uF)', 305587, 1.09, 'replaces GRM32ER72A225KA35L (0 stock)'),
 ('COUT1 COUT2', '330u/25V', '25SVPF330M', 'Panasonic', 'SMD 10x12.6', 'Output OS-CON', 3117, 2.79, ''),
 ('CHF1 CHF2 CHF3 CINT1 CSS1 CVCAP1 C1 C2 C3', '100n/100V X7R', 'C2012X7R2A104K125AA', 'TDK', '0805', 'Hot-loop / bypass', 164626, 0.17, ''),
 ('CCATH1', '1u/100V X7R', '08051C105K4T2A', 'KYOCERA AVX', '0805', 'LM74700 cathode cap', 167494, 0.43, 'was 1206'),
 ('CANODE1', '22n/100V X7R', 'GRM21BR72A223KA01L', 'Murata', '0805', 'LM74700 anode cap', 13494, 0.23, ''),
 ('CAUX1 CREF1', '1u/16V X7R', 'CC0805KKX7R7BB105', 'Yageo', '0805', 'Bypass', 630432, 0.28, ''),
 ('CBOOT1', '1u/25V X7R', 'CC0805KKX7R8BB105', 'Yageo', '0805', 'Bootstrap', 282126, 0.28, ''),
 ('CDRV1', '4.7u/25V X5R', 'CL21A475KAQNNNE', 'Samsung', '0805', 'DRVCC bypass', 611, 0.13, 'low stock'),
 ('CCS1 CERR1', '10n/50V C0G', 'CL21C103JBFNNNE', 'Samsung', '0805', 'CS filter / integrator', 65245, 0.39, ''),
 ('CITH1', '27n/50V C0G', 'GRM2165C1H273JA01D', 'Murata', '0805', 'Compensation', 21837, 0.29, ''),
 ('CITHP1', '470p/50V C0G', 'C0805C471J5GACTU', 'KEMET', '0805', 'Compensation', 82864, 0.26, 'replaces obsolete CL21C471JBANNNC'),
 ('CRUN1 CSENSE1', '1n/50V C0G', 'CC0805JRNPO9BN102', 'Yageo', '0805', 'RUN / sense filter', 212596, 0.64, ''),
 ('CSN1', '1n/100V C0G', 'C2012C0G2A102J060AA', 'TDK', '0805', 'Snubber cap', 39192, 0.13, ''),
 ('RSN1', '2.2 0.5 W', 'ERJ-P06J2R2V', 'Panasonic', '0805', 'Snubber resistor, anti-surge', 26000, 0.14, 'was 1206'),
 ('RGH1', '4.7', 'ERJ-6RQF4R7V', 'Panasonic', '0805', 'Gate resistor', 12180, 0.27, ''),
 ('RGL1', '2.2', 'ERJ-6RQF2R2V', 'Panasonic', '0805', 'Gate resistor', 38055, 0.27, ''),
 ('RGSH1 RGSL1', '100k', 'RC0805FR-07100KL', 'Yageo', '0805', 'Gate pull-down', 61128, 0.10, ''),
 ('RITH1', '8.2k', 'RC0805FR-078K2L', 'Yageo', '0805', 'Compensation', 109867, 0.10, ''),
 ('RFREQ1', '24.3k', 'RC0805FR-0724K3L', 'Yageo', '0805', 'fsw set', 677605, 0.11, ''),
 ('RISO1', '150', 'RC0805FR-07150RL', 'Yageo', '0805', 'CL loop', 373281, 0.10, ''),
 ('RLEAK1', '10M', 'RC0805FR-0710ML', 'Yageo', '0805', 'CL integrator leak', 137755, 0.10, ''),
 ('ROVT1', '825k', 'RC0805FR-07825KL', 'Yageo', '0805', 'OVLO divider', 63684, 0.10, ''),
 ('ROVB1', '17.4k', 'RC0805FR-0717K4L', 'Yageo', '0805', 'OVLO divider', 30184, 0.10, 'was 0603'),
 ('RPG1', '511k', 'ERJ-6ENF5113V', 'Panasonic', '0805', 'PGOOD pull-up', 3341, 0.12, ''),
 ('RRUNB1', '10k', 'RC0805FR-0710KL', 'Yageo', '0805', 'RUN divider', 1373154, 0.10, ''),
 ('RRUNT1', '130k', 'RC0805FR-07130KL', 'Yageo', '0805', 'RUN divider', 19259, 0.10, 'was 0603'),
 ('RERR1', '20k', 'ERJ-6ENF2002V', 'Panasonic', '0805', 'CL integrator', 224114, 0.13, 'was 0603'),
 ('RCSP1 RCSN1', '100 0.1%', 'RT0805BRD07100RL', 'Yageo', '0805', 'CS amp input', 9927, 0.12, ''),
 ('RCSO1', '2k 0.1%', 'RT0805BRD072KL', 'Yageo', '0805', 'CS amp output', 14046, 0.12, 'was 0603'),
 ('RFBB1', '10k 0.1%', 'RT0805BRD0710KL', 'Yageo', '0805', 'FB divider', 124938, 0.12, ''),
 ('RFBT1', '140k 0.1%', 'RT0805BRD07140KL', 'Yageo', '0805', 'FB divider', 1811, 0.12, ''),
 ('RSETB1', '12k 0.1%', 'RT0805BRD0712KL', 'Yageo', '0805', 'Current-limit set', 20673, 0.12, ''),
 ('RSETT1', '11.8k 0.1%', 'RT0805BRD0711K8L', 'Yageo', '0805', 'Current-limit set', 874, 0.12, 'low stock'),
 ('DAUX1 DCL1', 'BAT54', 'BAT54SLT1G', 'onsemi', 'SOT-23', 'Schottky (only diode 1 used)', 'UNVERIFIED', 0.16, 'check stock; alt. Diodes BAT54S-7-F'),
 ('DVIN1', '100 V Schottky', 'BAS100CS-AU_R1_000A1', 'Panjit', 'SOD-323F', 'VIN clamp', 75000, 0.20, 'replaces BAT46WJ (0 stock)'),
 ('DLED1', 'yellow', '150080YS75000', 'Wurth Elektronik', '0805', 'LED: VIN present', 40700, 0.19, 'NEW'),
 ('DLED2', 'green', '150080GS75000', 'Wurth Elektronik', '0805', 'LED: 12 V output', 194166, 0.19, 'NEW'),
 ('DLED3', 'red', '150080RS75000', 'Wurth Elektronik', '0805', 'LED: FAULT (PGOOD low)', 160416, 0.19, 'NEW'),
 ('RLED1', '47k', 'RC0805FR-0747KL', 'Yageo', '0805', 'LED resistor', 204049, 0.10, 'NEW'),
 ('RLED2', '4.7k', 'RC0805FR-074K7L', 'Yageo', '0805', 'LED resistor', 450273, 0.10, 'NEW'),
 ('RLED3', '2.2k', 'RC0805FR-072K2L', 'Yageo', '0805', 'LED resistor', 297227, 0.10, 'NEW'),
 ('SW1', 'ON/OFF', 'OS102011MS2QN1', 'C&K', 'THT slide', 'SPDT slide switch (RUN to GND)', 37139, 0.85, 'NEW'),
 ('JP1', 'CL loop', '61300211121', 'Wurth Elektronik', '2.54 mm', '2-pin header', 370300, 0.13, 'NEW'),
 ('JP1 shunt', 'jumper', '60900213421', 'Wurth Elektronik', '2.54 mm', 'Jumper shunt', 106255, 0.30, 'NEW'),
]


def qty(refs):
    if '..' in refs:
        a, b = refs.split('..'); return int(b[3:]) - int(a[3:]) + 1
    return len(refs.split())


wb = Workbook(); ws = wb.active; ws.title = 'BOM RevG'
H = ['#', 'Reference', 'Qty', 'Value', 'MPN', 'Manufacturer', 'Package', 'Description', 'DigiKey stock', 'Unit USD', 'Line USD', 'Link', 'Note']
ws.append(['EE463 Buck RevG BOM - Team CMPS - stock checked at DigiKey 2026-11-26']); ws['A1'].font = Font(bold=True, size=13)
ws.append(H)
for c in ws[2]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496')
for i, (r, v, m, mf, pk, d, st, pr, note) in enumerate(L, 1):
    q = qty(r); row = 2 + i
    ws.append([i, r, q, v, m, mf, pk, d, st, pr, f'=C{row}*J{row}', DK + m.replace('#', '%23').replace(' ', '%20').replace(',', '%2C'), note])
    ws.cell(row, 12).hyperlink = ws.cell(row, 12).value; ws.cell(row, 12).font = Font(color='0563C1', underline='single')
    if isinstance(st, int) and st < 1000 or not isinstance(st, int):
        ws.cell(row, 9).fill = PatternFill('solid', fgColor='FFE699')
n = 2 + len(L)
ws.append([]); ws.append(['', 'TOTAL (1 board)', f'=SUM(C3:C{n})', '', '', '', '', '', '', '', f'=SUM(K3:K{n})'])
for c in ws[n + 2]:
    c.font = Font(bold=True)
for i, w in enumerate([4, 30, 5, 14, 24, 18, 16, 42, 14, 9, 10, 60, 36], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = 'A3'
os.makedirs('bom', exist_ok=True)
wb.save('bom/EE463_Buck_RevG_BOM.xlsx'); print('rows', len(L))
