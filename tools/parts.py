"""Single source of truth for the RevF2 part list (schematic fields, PCB fields and the BOM are generated from it).
Prices: DigiKey US, cut tape, checked 2026-11-19 (see bom/README.md). 'dk' is the DigiKey product URL."""

DS = {
    'LTC3895': 'https://www.analog.com/media/en/technical-documentation/data-sheets/3895fa.pdf',
    'LT6105': 'https://www.analog.com/media/en/technical-documentation/data-sheets/6105fa.pdf',
    'LT1636': 'https://www.analog.com/media/en/technical-documentation/data-sheets/1636fc.pdf',
    'LT6654': 'https://www.analog.com/media/en/technical-documentation/data-sheets/lt6654.pdf',
    'LM74700': 'https://www.ti.com/lit/gpn/lm74700-q1',
    'BSC040': 'https://www.infineon.com/part/BSC040N08NS5',
    'BSC026': 'https://www.infineon.com/part/BSC026N08NS5',
    'XAL1510': 'https://www.coilcraft.com/getmedia/cd1cef27-13f0-4568-8894-f7311475209b/xal1510.pdf',
    'WE1510': 'https://www.we-online.com/components/products/datasheet/74439370330.pdf',
    'PA2512': 'https://yageogroup.com/content/datasheet/asset/file/PYU-PA_E_51_ROHS',
    'BAT54': 'https://www.onsemi.com/pub/Collateral/BAT54LT1-D.PDF',
    'BAT46WJ': 'https://assets.nexperia.com/documents/data-sheet/BAT46WJ.pdf',
    'MKDS': 'https://www.phoenixcontact.com/us/products/1715721/pdf',
    'SVPF': 'https://industrial.panasonic.com/ww/products/pt/os-con/models/25SVPF330M',
    'EEUFR': 'https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf',
    'TDK_MV': 'https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/catalog/mlcc_commercial_midvoltage_en.pdf',
    'TDK_GEN': 'https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/catalog/mlcc_commercial_general_en.pdf',
    'MURATA': 'https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8942/490_Chip_Multilayer_CAT2021_MLCC.pdf#',
    'ERJP': 'https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C331.pdf',
    'SAMSUNG': 'https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/41/CL21A475KAQNNNE_Spec.pdf',
    'RC': 'https://yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L',
    'RT': 'https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L',
    'ERJ6R': 'https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf',
}
DK = 'https://www.digikey.com/en/products/result?keywords='
D = 'https://www.digikey.com/en/products/detail/'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'


def p(value, mpn, mfr, desc, fp, price, ds, dk=None, tr='', note=''):
    return dict(value=value, mpn=mpn, mfr=mfr, desc=desc, fp=fp, price=price, datasheet=ds,
                dk=dk or DK + mpn.replace('#', '%23').replace(',', '%2C'), tr=tr, note=note)


RC_ID = {'24K3': 727758, '100K': 727544, '150R': 727613, '8K2': 728147, '10M': 727536, '17K4': 727636, '825K': 728171, '511K': 728019, '10K': 727535, '130K': 727590}
RT_ID = {'100R': 1075540, '2K': 1075799, '10K': 1075550, '140K': 1075599, '11K8': 1075565}


def rc(v, code, note=''):
    m = f'RC0805FR-07{code}L'
    return p(v, m, 'Yageo', f'Resistor {v} 1% 0.125W 0805 thick film', R0805, 0.10, DS['RC'],
             dk=f'{D}yageo/{m}/{RC_ID[code]}' if code in RC_ID else None, note=note)


def rt(v, code, note=''):
    m = f'RT0805BRD07{code}L'
    return p(v + ' / 0.1%', m, 'Yageo', f'Resistor {v} 0.1% 25ppm 0805 thin film', R0805, 0.12, DS['RT'],
             dk=f'{D}yageo/{m}/{RT_ID[code]}' if code in RT_ID else None, note=note)


def mur(v, mpn, desc, price, note='', dk=None):
    return p(v, mpn, 'Murata', desc, C0805, price, DS['MURATA'].rstrip('#'), dk=dk, note=note)


PARTS = {
    # --- controller and analog ICs
    'U1': p('LTC3895IFE#PBF', 'LTC3895IFE#PBF', 'Analog Devices', '150 V synchronous buck controller, TSSOP-38 (FE) + EP',
            'EE463Footprints:LTC3895_FE38_31_EP39_P0p5', 17.69, DS['LTC3895'], dk=D + 'analog-devices-inc/LTC3895IFE-PBF/6025900'),
    'U2': p('LT6105IMS8#PBF', 'LT6105IMS8#PBF', 'Analog Devices', 'Current-sense amplifier, -0.3..44 V input, MSOP-8',
            'Package_SO:MSOP-8_3x3mm_P0.65mm', 4.56, DS['LT6105'], dk=D + 'analog-devices-inc/LT6105IMS8-PBF/1785494'),
    'U3': p('LT1636IS8#PBF', 'LT1636IS8#PBF', 'Analog Devices', 'Over-the-Top rail-to-rail op amp, SO-8 (CC loop integrator)',
            'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 7.79, DS['LT1636'], dk=D + 'analog-devices-inc/LT1636IS8-PBF/889250'),
    'U4': p('LT6654AIS6-1.25', 'LT6654AIS6-1.25#TRMPBF', 'Analog Devices', '1.25 V precision reference 0.05%, TSOT-23-6',
            'Package_TO_SOT_SMD:TSOT-23-6', 8.74, DS['LT6654'], dk=D + 'analog-devices-inc/LT6654AIS6-1-25-TRMPBF/7322677', note='cut tape'),
    'U5': p('LM74700-Q1', 'LM74700QDBVRQ1', 'Texas Instruments', 'Ideal-diode controller (reverse polarity), SOT-23-6',
            'Package_TO_SOT_SMD:SOT-23-6', 2.54, DS['LM74700'], dk=D + 'texas-instruments/LM74700QDBVRQ1/10434692', note='pin-compatible 2nd source: Diodes AP74700QW6-7'),
    # --- power stage
    'Q1': p('BSC040N08NS5', 'BSC040N08NS5ATMA1', 'Infineon', 'N-MOSFET 80 V 4.0 mOhm, PG-TDSON-8 (high side)',
            'Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm', 2.66, DS['BSC040'], dk=D + 'infineon-technologies/BSC040N08NS5ATMA1/5959902'),
    'Q2': p('BSC026N08NS5', 'BSC026N08NS5ATMA1', 'Infineon', 'N-MOSFET 80 V 2.6 mOhm, PG-TDSON-8 (low side / ideal diode)',
            'Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm', 3.57, DS['BSC026'], dk=D + 'infineon-technologies/BSC026N08NS5ATMA1/5959896'),
    'L1': p('33u', 'XAL1510-333MED', 'Coilcraft', 'Power inductor 33 uH 20%, Isat 16.7 A, DCR 18.7 mOhm, 15x15 mm',
            'EE463Footprints:L_XAL1510_WE-XHMI1510_Dual', 7.00, DS['XAL1510'],
            dk='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal1510/xal1510-333/',
            note='Coilcraft direct: 6.37 EUR at qty 1, in stock (2026-11-19); not sold by DigiKey. 2nd source on the same dual footprint: Wurth 74439370330 (DigiKey 7.27 USD, restock Jan-2027)'),
    'RS1': p('4m / 1% / 2W', 'PA2512FKF7W0R004E', 'Yageo', 'Current-sense resistor 4 mOhm 1% 2 W, 2512',
             'EE463Footprints:R_2512_Shunt_Kelvin_3.05x3.68mm', 0.96, DS['PA2512'], dk=D + 'yageo/PA2512FKF7W0R004E/5138663',
             note='Yageo land pattern (3.05 x 3.68 mm, 1.27 mm gap) equals the PCB pads'),
    'RSN1': p('2.2 / 0.66W pulse', 'ERJ-P08J2R2V', 'Panasonic', 'Snubber resistor 2.2 Ohm 5% 0.66 W anti-surge, 1206',
              'Resistor_SMD:R_1206_3216Metric', 0.18, DS['ERJP'], dk=D + 'panasonic-industry/ERJ-P08J2R2V/9813197'),
    'CSN1': p('1n / 100V C0G', 'C2012C0G2A102J060AA', 'TDK', 'Snubber capacitor 1 nF 100 V C0G, 0805', C0805, 0.13, DS['TDK_MV'], dk=D + 'tdk-corporation/C2012C0G2A102J060AA/789714'),
    'CHF1': p('100n / 100V', 'C2012X7R2A104K125AA', 'TDK', 'Capacitor 100 nF 100 V X7R, 0805 (hot loop, INTVCC, soft start, VCAP)', C0805, 0.17, DS['TDK_MV'], dk=D + 'tdk-corporation/C2012X7R2A104K125AA/569044'),
    # --- input / output filter
    'CIN1': p('2.2u / 100V', 'CL32B225KCJSNNE', 'Samsung Electro-Mechanics', 'Input capacitor 2.2 uF 100 V X7R, 1210', 'Capacitor_SMD:C_1210_3225Metric', 0.365, 'https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/41/CL32B225KCJSNNE_Spec.pdf', dk=D + 'samsung-electro-mechanics/CL32B225KCJSNNE/3889020', note='qty-10 price; TDK C3225X7R2A225K230AB out of stock'),
    'CINB1': p('100u / 100V', '100ZLH100MEFC10X20', 'Rubycon', 'Input bulk electrolytic 100 uF 100 V low ESR, D10 x 20 mm, P5 mm',
               'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', 1.09, 'https://www.rubycon.co.jp/wp-content/uploads/catalog-aluminum/ZLH.pdf', dk=D + 'rubycon/100ZLH100MEFC10X20/3563824', note='Panasonic EEU-FR2A101 out of stock'),
    'COUT1': p('330u / 25V', '25SVPF330M', 'Panasonic', 'Output polymer capacitor 330 uF 25 V OS-CON, 10x12.6 mm',
               'Capacitor_SMD:CP_Elec_10x12.6', 2.79, DS['SVPF'], dk=D + 'panasonic-industry/25SVPF330M/4204844'),
    'CCATH1': p('1u / 100V', 'CC1206KKX7R0BB105', 'Yageo', 'LM74700 CATHODE / Q3 drain capacitor 1 uF 100 V X7R, 1206',
                'Capacitor_SMD:C_1206_3216Metric', 0.71, 'https://yageogroup.com/content/datasheet/asset/file/UPY-GPHC_X7R_6_3V-TO-250V', dk=D + 'yageo/CC1206KKX7R0BB105/5195354'),
    # --- protection / aux
    'DAUX1': p('BAT54', 'BAT54LT1G', 'onsemi', 'Schottky 30 V 200 mA, SOT-23 (1=A, 3=K)',
               'Package_TO_SOT_SMD:SOT-23', 0.14, DS['BAT54'], dk=D + 'onsemi/BAT54LT1G/918316'),
    'DVIN1': p('BAT46WJ', 'BAT46WJ,115', 'Nexperia', 'Schottky 100 V 250 mA, SOD-323F (VIN negative clamp)',
               'Diode_SMD:D_SOD-323F', 0.32, DS['BAT46WJ'], dk=D + 'nexperia-usa-inc/BAT46WJ-115/2405998', note='backordered at DigiKey: order early or check Mouser/Farnell'),
    'J1': p('20-48 V IN', '1715721', 'Phoenix Contact', 'Terminal block 2-pos 5.08 mm, MKDS 1,5/2-5,08',
            'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', 1.16, DS['MKDS'], dk=D + 'phoenix-contact/1715721/260631', note='DigiKey restock 03-Dec-2026'),
    'CANODE1': mur('22n / 100V X7R', 'GRM21BR72A223KA01L', 'LM74700 ANODE capacitor 22 nF 100 V X7R, 0805', 0.23, dk=D + 'murata-electronics/GRM21BR72A223KA01L/586672'),
    'CVCAP1': p('100n / 100V X7R', 'C2012X7R2A104K125AA', 'TDK', 'LM74700 VCAP capacitor 100 nF X7R, 0805', C0805, 0.17, DS['TDK_MV'], dk=D + 'tdk-corporation/C2012X7R2A104K125AA/569044'),
    # --- controller support
    'CDRV1': p('4.7u / 25V', 'CL21A475KAQNNNE', 'Samsung Electro-Mechanics', 'DRVCC bypass 4.7 uF 25 V X5R, 0805', C0805, 0.13, DS['SAMSUNG'], dk=D + 'samsung-electro-mechanics/CL21A475KAQNNNE/3886902'),
    'CINT1': p('100n / 100V', 'C2012X7R2A104K125AA', 'TDK', 'INTVCC bypass 100 nF X7R, 0805', C0805, 0.17, DS['TDK_MV'], dk=D + 'tdk-corporation/C2012X7R2A104K125AA/569044'),
    'CSS1': p('100n / 100V', 'C2012X7R2A104K125AA', 'TDK', 'Soft-start 100 nF X7R, 0805', C0805, 0.17, DS['TDK_MV'], dk=D + 'tdk-corporation/C2012X7R2A104K125AA/569044'),
    'CREF1': p('1u / 16V', 'C2012X7R1C105K085AC', 'TDK', 'Reference / aux bypass 1 uF 16 V X7R, 0805', C0805, 0.17, DS['TDK_GEN'], dk=D + 'tdk-corporation/C2012X7R1C105K085AC/2733011'),
    'CBOOT1': p('1u / 25V', 'C2012X7R1E105K125AB', 'TDK', 'Bootstrap capacitor 1 uF 25 V X7R, 0805', C0805, 0.23, DS['TDK_GEN'], dk=D + 'tdk-corporation/C2012X7R1E105K125AB/513887'),
    'CITH1': mur('27n / C0G', 'GRM2165C1H273JA01D', 'Compensation CITH 27 nF 50 V C0G, 0805', 0.29, dk=D + 'murata-electronics/GRM2165C1H273JA01D/13688529'),
    'CITHP1': mur('470p / C0G', 'GRM2165C1H471JA01D', 'Compensation CITHP 470 pF 50 V C0G, 0805', 0.24, dk=D + 'murata-electronics/GRM2165C1H471JA01D/586802'),
    'CCS1': p('10n / C0G', 'C2012C0G1H103J060AA', 'TDK', 'CS filter / integrator 10 nF 50 V C0G, 0805', C0805, 0.28, DS['TDK_GEN'], dk=D + 'tdk-corporation/C2012C0G1H103J060AA/2732954'),
    'CRUN1': mur('1n / 50V C0G', 'GRM2165C1H102JA01D', 'Capacitor 1 nF 50 V C0G, 0805 (RUN filter, sense filter)', 0.17, dk=D + 'murata-electronics/GRM2165C1H102JA01D/586809'),
    'RITH1': rc('8.2k', '8K2'), 'RFREQ1': rc('24.3k', '24K3'),
    'RGH1': p('4.7', 'ERJ-6RQF4R7V', 'Panasonic', 'Gate resistor 4.7 Ohm 1% 0805', R0805, 0.27, DS['ERJ6R'], dk=D + 'panasonic-industry/ERJ-6RQF4R7V/250180', note='Yageo RC0805FR-074R7L out of stock'),
    'RGL1': p('2.2', 'ERJ-6RQF2R2V', 'Panasonic', 'Gate resistor 2.2 Ohm 1% 0805', R0805, 0.27, DS['ERJ6R'], dk=D + 'panasonic-industry/ERJ-6RQF2R2V/250176', note='Yageo RC0805FR-072R2L out of stock'),
    'RGSH1': rc('100k', '100K'), 'RISO1': rc('150', '150R'), 'RLEAK1': rc('10M', '10M'), 'ROVB1': rc('17.4k', '17K4'),
    'ROVT1': rc('825k', '825K'), 'RPG1': rc('511k', '511K'), 'RRUNB1': rc('10k', '10K'), 'RRUNT1': rc('130k', '130K'),
    'RERR1': p('20k', 'ERJ-6ENF2002V', 'Panasonic', 'Resistor 20 kOhm 1% 0805 (CC integrator)', R0805, 0.13, DS['ERJ6R'], dk=D + 'panasonic-industry/ERJ-6ENF2002V/111532', note='Yageo RC0805FR-0720KL out of stock'),
    'RCSP1': rt('100', '100R', note='DigiKey 0 stock: order early; alt. Panasonic ERA-6AEB101V (0.1% 0805, not checked)'), 'RCSO1': rt('2k', '2K'), 'RFBB1': rt('10k', '10K'), 'RFBT1': rt('140k', '140K'),
    'RSETB1': rt('12k', '12K'), 'RSETT1': rt('11.8k', '11K8', note='current-limit trim: see calculations'),
}
# parts that share a line with another reference
SAME = {'Q3': 'Q2', 'CHF2': 'CHF1', 'CHF3': 'CHF1', 'J2': 'J1', 'COUT2': 'COUT1', 'CINB2': 'CINB1', 'CINB3': 'CINB1',
        'DCL1': 'DAUX1', 'CAUX1': 'CREF1', 'CERR1': 'CCS1', 'CSENSE1': 'CRUN1', 'RGSL1': 'RGSH1', 'RCSN1': 'RCSP1'}
SAME.update({f'CIN{i}': 'CIN1' for i in range(2, 11)})
for a, b in SAME.items():
    PARTS[a] = PARTS[b]
PARTS['J2'] = dict(PARTS['J1'], value='12 V OUT')
NOT_BOUGHT = {'J3': 'Fan connector, DNP', **{f'TP{i}': 'PCB copper test pad' for i in range(1, 17)}}
# spares bought for the line/load transient bonus (compensation B: RITH 3.9k, CITH 68n, CITHP 1n)
SPARES = [
    p('3.9k', 'RC0805FR-073K9L', 'Yageo', 'Compensation B: RITH 3.9 kOhm 1% 0805 (spare, hand-fitted for the A/B test)', R0805, 0.10, DS['RC'], dk=D + 'yageo/RC0805FR-073K9L/727838'),
    p('68n / C0G', 'C3216C0G1H683J160AA', 'TDK', 'Compensation B: CITH 68 nF 50 V C0G 1206 (spare; fits across the 0805 pads)', 'Capacitor_SMD:C_1206_3216Metric', 0.62, DS['TDK_GEN'], dk=D + 'tdk-corporation/C3216C0G1H683J160AA/2733128'),
    mur('1n / 50V C0G', 'GRM2165C1H102JA01D', 'Compensation B: CITHP 1 nF 50 V C0G 0805 (spare)', 0.17, dk=D + 'murata-electronics/GRM2165C1H102JA01D/586809'),
]


# ---------------------------------------------------------------------------------------------------------------
# Turkish stock (Ozdisan, checked 2026-11-19). Parts not stocked in Turkey are replaced by an equivalent that is
# (same value, same package, same or tighter tolerance, same dielectric class, same or higher voltage/power).
# Prices: Ozdisan unit price in USD (VAT excluded); the bought quantity is rounded up to the Ozdisan MOQ.
# Parts with no Turkish stock (ADI ICs, LM74700, MOSFETs, XAL1510, OS-CON, Rubycon, Phoenix, shunt, 100 V 0805 X7R,
# C0G 1 nF/100 V, 27 nF C0G, 4.7 Ohm 1%, 2.2 Ohm pulse, 0.1% 140k/11.8k) stay on DigiKey.
OZ = 'https://www.ozdisan.com/p/'
OZR = OZ + 'smt-smd-ve-cip-direncler-194/'
OZC = OZ + 'smt-smd-ve-mlcc-kapasitorler-184/'
DS_TC = 'https://www.mouser.lt/pdfDocs/highprecisionthinfilmtcseries_ro-1.pdf'
DS_HOT = 'https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/1812051032_Guangdong-Hottech-BAT54S_C181201.pdf'
DS_YX7R = 'https://yageogroup.com/content/datasheet/asset/file/UPY-GPHC_X7R_6_3V-TO-250V'
DS_YNP0 = 'https://yageogroup.com/content/datasheet/asset/file/UPY-GPHC_NP0_16V-TO-50V'


def roy(v, mpn, oid, price, moq, tol='1%', kind='0.125W 0805 thick film', ds=None):
    url = f'{OZR}royalohm-{mpn.lower()}-{oid}'
    return dict(mpn=mpn, mfr='Royal Ohm', desc=f'Resistor {v} {tol} {kind}', price=price, moq=moq, tr=url,
                datasheet=ds or url)


def cap(mpn, mfr, desc, price, moq, slug, ds=None):
    url = OZC + slug
    return dict(mpn=mpn, mfr=mfr, desc=desc, price=price, moq=moq, tr=url, datasheet=ds or url, dk=DK + mpn)


# old MPN -> Turkish-stock replacement. When the new maker is not on DigiKey (Royal Ohm, Hottech) the DigiKey column
# keeps the link of the original, equivalent part.
REPLACE = {
    'RC0805FR-078K2L': roy('8.2k', '0805S8F8201T5E', 31100, 0.00182, 100),
    'RC0805FR-0724K3L': roy('24.3k', '0805S8F2432T5E', 505549, 0.00182, 100),
    'RC0805FR-07150RL': roy('150', '0805S8F1500T5E', 335038, 0.00182, 100),
    'RC0805FR-0710ML': roy('10M', '0805S8F1005T5E', 35616, 0.00337, 50),
    'RC0805FR-07825KL': roy('825k', '0805S8F8253T5E', 505666, 0.00182, 100),
    'RC0805FR-07511KL': roy('511k', '0805S8F5113T5E', 505648, 0.00182, 100),
    'RC0805FR-0710KL': roy('10k', '0805S8F1002T5E', 30240, 0.00182, 100),
    'RC0805FR-073K9L': roy('3.9k', '0805S8F3901T5E', 35627, 0.00182, 100),
    'ERJ-6RQF2R2V': roy('2.2 Ohm', 'CQ05S8F220KT5E', 587991, 0.00505, 20, kind='0.125W 0805 AEC-Q200 (gate)'),
    'RT0805BRD07100RL': roy('100 Ohm', 'TC0525B1000T5G', 700116, 0.03564, 5, '0.1% 25ppm', '0805 thin film', DS_TC),
    'RT0805BRD0710KL': roy('10k', 'TC0525B1002T5G', 700129, 0.03564, 5, '0.1% 25ppm', '0805 thin film', DS_TC),
    'RC0603FR-0720KL': roy('20k', '0603SAF2002T5E', 353309, 0.00111, 100, kind='0.1W 0603 thick film'),
    'RC0603FR-07130KL': roy('130k', '0603SAF1303T5E', 359810, 0.00111, 100, kind='0.1W 0603 thick film'),
    'CL32B225KCJSNNE': cap('GRM32ER72A225KA35L', 'Murata', 'Input capacitor 2.2 uF 100 V X7R, 1210', 0.32651, 1,
                           'murata-grm32er72a225ka35l-1589679', DS['MURATA'].rstrip('#')),
    'C2012X7R1C105K085AC': cap('CC0805KKX7R7BB105', 'Yageo', 'Reference / aux bypass 1 uF 16 V X7R, 0805', 0.05307, 2,
                               'yageo-cc0805kkx7r7bb105-504015', DS_YX7R),
    'C2012X7R1E105K125AB': cap('CC0805KKX7R8BB105', 'Yageo', 'Bootstrap capacitor 1 uF 25 V X7R, 0805', 0.06369, 5,
                               'yageo-cc0805kkx7r8bb105-576600', DS_YX7R),
    'GRM2165C1H471JA01D': cap('CL21C471JBANNNC', 'Samsung Electro-Mechanics', 'Compensation CITHP 470 pF 50 V C0G 5%, 0805',
                              0.020, 10, 'samsung-cl21c471jbannnc-5654'),
    'C2012C0G1H103J060AA': cap('CL21C103JBFNNNE', 'Samsung Electro-Mechanics', 'CS filter / integrator 10 nF 50 V C0G 5%, 0805',
                               0.10478, 1, 'samsung-cl21c103jbfnnne-353899'),
    'GRM2165C1H102JA01D': cap('CC0805JRNPO9BN102', 'Yageo', 'Capacitor 1 nF 50 V C0G 5%, 0805 (RUN filter, sense filter, comp. B CITHP)',
                              0.02694, 5, 'yageo-cc0805jrnpo9bn102-749103', DS_YNP0),
    'CC1206KKX7R0BB105': cap('CL31B105KCHNNNE', 'Samsung Electro-Mechanics', 'LM74700 CATHODE / Q3 drain capacitor 1 uF 100 V X7R, 1206',
                             0.06529, 2, 'samsung-cl31b105kchnnne-382908'),
    'BAT54LT1G': dict(mpn='BAT54S-HT', mfr='Hottech', value='BAT54S', price=0.01054, moq=10, datasheet=DS_HOT,
                      desc='Schottky 30 V 200 mA dual series, SOT-23; only diode 1 used (1=A, 3=K, same as BAT54), pin 2 is a no-connect pad',
                      tr=OZ + 'schottky-diyotlar-385/hottech-bat54s-ht-417220'),
}
# kept parts that are also in stock in Turkey
TR_ONLY = {
    'BAT46WJ,115': dict(tr=OZ + 'schottky-diyotlar-385/nexperia-bat46wj-115-609944', price=0.12133, moq=1,
                        note='Ozdisan: 6562 in stock (DigiKey backordered)'),
    'CL21A475KAQNNNE': dict(tr=OZC + 'samsung-cl21a475kaqnnne-441542', price=0.028, moq=5),
    'RC0805FR-07100KL': dict(tr=OZR + 'yageo-rc0805fr-07100kl-460162', price=0.00429, moq=50),
    'RT0805BRD0712KL': dict(tr=OZR + 'yageo-rt0805brd0712kl-814018', price=0.04871, moq=5),
    'RT0603BRD072KL': dict(tr=OZR + 'yageo-rt0603brd072kl-625691', price=0.04921, moq=5),
    'RC0603FR-0717K4L': dict(tr=OZR + 'yageo-rc0603fr-0717k4l-618013', price=0.00252, moq=50),
}


def turkey(p):
    """Return the part with the Turkish-stock replacement or link applied (idempotent)."""
    old = p['mpn']
    if old in REPLACE:
        r = REPLACE[old]
        q = dict(p, **r)
        q['note'] = f'Turkish stock (Ozdisan); replaces {old}'
        if 'dk' not in r:
            q['note'] += ' (DigiKey link = that original part)'
        return q
    if old in TR_ONLY:
        t = TR_ONLY[old]
        q = dict(p, **{k: v for k, v in t.items() if k != 'note'})
        q['note'] = t.get('note', 'in stock at Ozdisan')
        return q
    return p


for _r in list(PARTS):
    PARTS[_r] = turkey(PARTS[_r])
PARTS['J2'] = dict(PARTS['J1'], value='12 V OUT')
SPARES = [turkey(s) for s in SPARES]
