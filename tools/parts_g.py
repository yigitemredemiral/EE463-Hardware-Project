"""RevG part list = RevF2/F4 list (parts.py) + presentation feedback (2026-11-25):
 - all three MOSFETs the same TO-220 part, each on its own PCB heatsink (no fan, J3 removed)
 - every R/C 0805 except the 2512 shunt, the 1210 100 V input MLCCs and the electrolytic / polymer capacitors
 - status LEDs (VIN, 12 V OUT, FAULT), RUN on/off slide switch, jumper that disconnects the average current-limit loop"""
from parts import PARTS as _P, DS, D, DK, p, R0805, C0805

PARTS = {k: dict(v) for k, v in _P.items() if k != 'J3'}
DS.update({
    'IPP040': 'https://www.infineon.com/part/IPP040N08NF2S',
    'SK104': 'https://www.fischerelektronik.de/web_fischer/en_GB/heatsinks/C01/PCB%20heatsinks/PR/SK104_/index.xhtml',
    'OS102': 'https://www.ckswitches.com/media/1428/os.pdf',
    'WLED': 'https://www.we-online.com/components/products/datasheet/150080GS75000.pdf',
    'WHDR': 'https://www.we-online.com/components/products/datasheet/61300211121.pdf',
})
FET = p('IPP040N08NF2S', 'IPP040N08NF2SAKMA1', 'Infineon', 'N-MOSFET 80 V 4.0 mOhm, TO-220 (vertical, on PCB heatsink)',
        'Package_TO_SOT_THT:TO-220-3_Vertical', 2.20, DS['IPP040'], dk=D + 'infineon-technologies/IPP040N08NF2SAKMA1/13996705')
for q in ('Q1', 'Q2', 'Q3'):
    PARTS[q] = dict(FET)
HS = p('SK 104 38,1 STC', 'SK 104 38,1 STC', 'Fischer Elektronik', 'TO-220 PCB heatsink 38.1 mm, solder pins, M3 screw',
       'Heatsink:Heatsink_Fischer_SK104-STC-STIC_35x13mm_2xDrill2.5mm', 1.60, DS['SK104'])
for h in ('HS1', 'HS2'):
    PARTS[h] = dict(HS)


def rc(v, code, desc):
    m = f'RC0805FR-07{code}L'
    return p(v, m, 'Yageo', f'Resistor {v} 1% 0.125W 0805 ({desc})', R0805, 0.10, DS['RC'])


def led(color, code, desc):
    m = f'150080{code}75000'
    return p(color, m, 'Wurth Elektronik', f'LED {color} 0805 ({desc})', 'LED_SMD:LED_0805_2012Metric', 0.20,
             DS['WLED'].replace('GS', code))


PARTS.update({
    'F1': p('8A', '0154008.DR', 'Littelfuse', 'Input fuse 8 A time-lag, 125 V, OMNI-BLOK 154 (Nano2 fuse in SMD holder, replaceable)',
             'Fuse:Fuseholder_Littelfuse_Nano2_154x', 1.50, 'https://www.littelfuse.com/products/fuses/surface-mount-fuses/nano2-fuses/154'),
    'DLED1': led('yellow', 'YS', 'VIN present'), 'RLED1': rc('47k', '47K', 'VIN LED, 1 mA at 48 V, 46 mW'),
    'DLED2': led('green', 'GS', '12 V output on'), 'RLED2': rc('4.7k', '4K7', 'VOUT LED, 2.1 mA'),
    'DLED3': led('red', 'RS', 'FAULT = PGOOD low'), 'RLED3': rc('2.2k', '2K2', 'FAULT LED from INTVCC, 1.4 mA'),
    'SW1': p('ON/OFF', 'OS102011MS2QN1', 'C&K', 'Slide switch SPDT, THT straight (RUN to GND = converter off)',
             'Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q', 0.55, DS['OS102']),
    'JP1': p('CL loop', '61300211121', 'Wurth Elektronik', '2-pin header 2.54 mm + jumper shunt 60900213421 (closed = average current-limit loop active)',
             'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', 0.30, DS['WHDR']),
    'RSN1': p('2.2 / 0.5W pulse', 'ERJ-P06J2R2V', 'Panasonic', 'Snubber resistor 2.2 Ohm 5% 0.5 W anti-surge, 0805', R0805, 0.20,
              DS['ERJP']),
    'CCATH1': p('1u / 100V', 'C2012X7S2A105K125AB', 'TDK', 'LM74700 CATHODE / Q3 drain capacitor 1 uF 100 V X7S, 0805', C0805, 0.35,
                DS['TDK_MV']),
})
# 0603 parts of RevF2 -> 0805 (parts.py REPLACE used 0603 Royal Ohm parts for these)
PARTS['RERR1'] = rc('20k', '20K', 'CC integrator')
PARTS['RRUNT1'] = rc('130k', '130K', 'RUN divider top')
PARTS['ROVB1'] = rc('17.4k', '17K4', 'OVLO divider bottom')
PARTS['RCSO1'] = p('2k / 0.1%', 'RT0805BRD072KL', 'Yageo', 'Resistor 2k 0.1% 25ppm 0805 thin film', R0805, 0.12, DS['RT'])
for k in ('C1', 'C2', 'C3'):
    PARTS[k] = dict(PARTS['CHF1'], desc='Supply decoupling 100 nF 100 V X7R, 0805 (U2/U3/U4 INTVCC pin)')
PARTS['J2'] = dict(PARTS['J1'], value='12 V OUT')
for k, v in PARTS.items():
    assert '0603' not in v['fp'], k
