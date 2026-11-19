"""Write the small LTspice symbols used by EE463_Buck_RevF2.asc (pin order = ADI subcircuit node order)."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'simulation', 'ltspice_RevF2')
SYMS = {
    'LT6105': ('LT6105', 'Current sense amplifier (ADI model models/LT6105.lib)',
               [(6, '+IN', -96, -32), (1, '-IN', -96, 32), (4, 'OUT', 96, 0), (5, 'NC', 96, 32), (2, 'V+', 0, -96), (3, 'V-', 0, 96)]),
    'LT1636': ('LT1636', 'Over-the-Top op amp (ADI model models/LT1636.lib)',
               [(1, '+IN', -96, -32), (2, '-IN', -96, 32), (5, 'OUT', 96, 0), (3, 'V+', 0, -96), (4, 'V-', -32, 96), (6, 'SHDN', 32, 96)]),
    'LT6654': ('LT6654-1.25', '1.25 V reference (ADI model models/LT6654-1.25.sub)',
               [(2, 'IN', -96, 0), (3, 'OUT', 96, 0), (1, 'GND', 0, 96)]),
}
for name, (value, desc, pins) in SYMS.items():
    L = ['Version 4', 'SymbolType CELL', 'RECTANGLE Normal -64 -64 64 64',
         'WINDOW 0 0 -72 Bottom 2', 'WINDOW 3 0 72 Top 2',
         f'SYMATTR Value {value}', 'SYMATTR Prefix X', f'SYMATTR Description {desc}']
    for order, pn, x, y in sorted(pins):
        if abs(x) == 96:
            L.append(f'LINE Normal {x} {y} {64 if x > 0 else -64} {y}')
            just = 'RIGHT' if x > 0 else 'LEFT'
        else:
            L.append(f'LINE Normal {x} {y} {x} {64 if y > 0 else -64}')
            just = 'BOTTOM' if y > 0 else 'TOP'
        L += [f'PIN {x} {y} {just} 8', f'PINATTR PinName {pn}', f'PINATTR SpiceOrder {order}']
    open(os.path.join(OUT, name + '.asy'), 'w', encoding='latin-1', newline='\n').write('\n'.join(L) + '\n')
print('ok')
