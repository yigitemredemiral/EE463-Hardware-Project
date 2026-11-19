"""Compare the topology of the drawn LTspice schematic (LTspice -netlist output) with a RevF1 simulation netlist.
Net names are ignored: the check is that the same element pins share nodes. Two-terminal R/C/L are unordered.
The reference compensation element C4 (27n Rser=8.2k Cpar=470p) is expanded into RITH1 / CITH1 / CITHP1.
Usage: python tools/cmp_spice.py <drawn.net> <reference.cir>"""
import re, sys

MAP = dict(V1='V1', Rsource='Rsource', MQ3='MRP', Biq='Biq', Bid='Bid', RgLeak='RgLeak', Lcable='Lcable', DVIN1='DvinClamp',
           CINcer='CinCer', CINbulk='CinBulk', Lloop='Lloop', CHF='Chf', MQ1='MQ1', MQ2='MQ2', RGH1='RgH', LgH='LgH',
           RGSH1='RgsH', RGL1='RgL', LgL='LgL', RGSL1='RgsL', RSN1='Rsnub', CSN1='Csnub', CBOOT1='C2', L1='L1',
           Rtrace='Rtrace', RS1='R4', COUT='C1', Rload='Rload', XU1='XU1', RFBT1='R1', RFBB1='R2', CSS1='C5',
           RFREQ1='R3', RRUNT1='RrunTop', RRUNB1='RrunBot', CRUN1='Crun', ROVT1='R6', ROVB1='R7', RPG1='R5',
           CSENSE1='C6', CINT1='C3', CAUX1='Caux', DAUX1='Daux', CDRV1='C7', XU2='XCS', XU3='XEA', XU4='XREF',
           RCSP1='RcsP', RCSN1='RcsN', RCSO1='RcsOut', CCS1='Ccs', RERR1='Rerr', CERR1='Cerr', RLEAK1='RerrLeak',
           RISO1='Riso', DCL1='Dclamp', CREF1='Cref', RSETT1='RsetTop', RSETB1='RsetBot', RITH1='RITH1', CITH1='CITH1',
           CITHP1='CITHP1')
MAP['@LOOP'] = '@LOOP'


def elements(path, expand=False):
    out = {}
    for line in open(path, encoding='latin-1'):
        line = line.split(';')[0].strip()
        if not line or line[0] in '*.+':
            continue
        t = line.split()
        name = ''.join(ch for ch in t[0] if ch.isascii() and (ch.isalnum() or ch in '_@'))
        if name.startswith('XX'):
            name = name[1:]
        c = name[0].upper()
        if c == 'X':
            nodes = t[1:-1]
        elif c == 'M':
            nodes = t[1:4]
        elif c in 'RCLDVB@':
            nodes = t[1:3]
        else:
            continue
        if expand and name == 'C4':
            out['RITH1'] = (nodes[0], 'COMP_X'); out['CITH1'] = ('COMP_X', nodes[1]); out['CITHP1'] = (nodes[0], nodes[1])
            continue
        out[name] = tuple(nodes)
    return out


def partition(el):
    nets = {}
    for name, nodes in el.items():
        two = name[0].upper() in 'RCL' and len(nodes) == 2
        for i, n in enumerate(nodes):
            key = name if two else f'{name}.{i + 1}'
            nets.setdefault('0' if n == '0' else n, set()).add(key)
    # single-pin nets (unconnected pins, MP_xx / NC_xx) carry no topology
    return {k: frozenset(v) for k, v in nets.items() if len(v) > 1 or k == '0'}


if __name__ == '__main__':
    new = elements(sys.argv[1]); ref = elements(sys.argv[2], expand=True)
    new = {MAP.get(k, k): v for k, v in new.items()}
    miss = set(ref) ^ set(new)
    print('elements only in one file:', sorted(miss) or 'none')
    a, b = partition(new), partition(ref)
    A, B = set(a.values()), set(b.values())
    for x in sorted(A - B, key=sorted):
        print('  drawn only:', sorted(x))
    for x in sorted(B - A, key=sorted):
        print('  reference only:', sorted(x))
    print('ground net equal:', a.get('0') == b.get('0'))
    print('TOPOLOGY IDENTICAL' if A == B and not miss else 'TOPOLOGY DIFFERENT')
