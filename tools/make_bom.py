"""Build the bills of materials from tools/parts.py and the final PCB.

Outputs (bom/):
  BOM_course_format.csv  - exactly the columns of the course sponsorship sheet (formulas for totals)
  BOM_course_format.tsv  - same, tab separated, to paste into the Google Sheet at cell A1
  BOM_full.csv           - engineering BOM: references, footprints, manufacturer, datasheets, notes
Usage: python tools/make_bom.py <final.kicad_pcb> [group name]"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts import PARTS, SPARES, NOT_BOUGHT, DS, turkey
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bom')
DKS = 'https://www.digikey.com/en/products/result?keywords='
# parts that could not be enlarged to 0805 on the PCB (dense routing at U1/U2/U3): 0603 equivalents
P0603 = {
    '2k / 0.1%': ('RT0603BRD072KL', 'Yageo', 0.12, DS['RT']), '20k': ('0603SAF2002T5E', 'Royal Ohm', 0.00111, 'https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0603saf2002t5e-353309'),
    '140k / 0.1%': ('RT0603BRD07140KL', 'Yageo', 0.12, DS['RT']), '150': ('RC0603FR-07150RL', 'Yageo', 0.10, DS['RC']),
    '17.4k': ('RC0603FR-0717K4L', 'Yageo', 0.10, DS['RC']), '130k': ('0603SAF1303T5E', 'Royal Ohm', 0.00111, 'https://www.ozdisan.com/p/smt-smd-ve-cip-direncler-194/royalohm-0603saf1303t5e-359810'),
    '11.8k / 0.1%': ('RT0603BRD0711K8L', 'Yageo', 0.12, DS['RT']), '8.2k': ('RC0603FR-078K2L', 'Yageo', 0.10, DS['RC']),
    '10M': ('RC0603FR-0710ML', 'Yageo', 0.10, DS['RC']), '825k': ('RC0603FR-07825KL', 'Yageo', 0.10, DS['RC']),
    '511k': ('RC0603FR-07511KL', 'Yageo', 0.10, DS['RC']), '10k': ('RC0603FR-0710KL', 'Yageo', 0.10, DS['RC']),
    '12k / 0.1%': ('RT0603BRD0712KL', 'Yageo', 0.12, DS['RT']), '100 / 0.1%': ('RT0603BRD07100RL', 'Yageo', 0.12, DS['RT']),
    '24.3k': ('RC0603FR-0724K3L', 'Yageo', 0.10, DS['RC']), '100k': ('RC0603FR-07100KL', 'Yageo', 0.10, DS['RC']),
    '4.7': ('RC0603FR-074R7L', 'Yageo', 0.10, DS['RC']), '2.2': ('RC0603FR-072R2L', 'Yageo', 0.10, DS['RC']),
}


def desc0603(d):
    return d.replace('0.125W 0805', '0.1W 0603').replace('0805', '0603')


def pcb_footprints(pcb):
    t = open(pcb, encoding='utf-8').read()
    return {r: f for f, r in re.findall(r'\(footprint "([^"]+)".*?\(property "Reference" "([^"]+)"', t, re.S)}


def natural(ref):
    m = re.match(r'([A-Z#]+)(\d+)', ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def main(pcb, group='Group X'):
    fps = pcb_footprints(pcb)
    lines = {}
    kept0603 = []
    for ref in sorted(fps, key=natural):
        if ref in NOT_BOUGHT or ref.startswith(('TP', 'H', 'MH')):
            continue
        p = dict(PARTS[ref])
        if '0603' in fps[ref]:
            mpn, mfr, price, ds = P0603[p['value']]
            p.update(mpn=mpn, mfr=mfr, price=price, datasheet=ds, dk=DKS + mpn, fp=fps[ref],
                     desc=desc0603(p['desc']), note='0603: no room for 0805 in the routing at the controller', tr='', moq=1)
            for o, n in (('0603SAF2002T5E', 'RC0603FR-0720KL'), ('0603SAF1303T5E', 'RC0603FR-07130KL')):
                if mpn == o:
                    p['mpn'] = n  # let turkey() fill the Royal Ohm data and the Ozdisan link
            p = turkey(p)
            if 'Ozdisan' not in p['note'] and 'in stock' not in p['note']:
                p['note'] = '0603: no room for 0805 in the routing at the controller'
            else:
                p['note'] += '; 0603 (no room for 0805)'
            kept0603.append(ref)
        key = p['mpn']
        if key not in lines:
            lines[key] = dict(p, refs=[], qty=0)
        lines[key]['refs'].append(ref); lines[key]['qty'] += 1
    for s in SPARES:
        key = s['mpn']
        if key in lines:
            lines[key]['qty'] += 1; lines[key]['note'] = (lines[key].get('note', '') + '; +1 spare for compensation B').strip('; ')
        else:
            lines[key] = dict(s, refs=['(spare)'], qty=1, note='spare for compensation B (transient bonus)')
    for l in lines.values():
        need = l['qty']; moq = l.get('moq', 1) or 1
        l['need'] = need; l['qty'] = max(need, math.ceil(need / moq) * moq)
        if l['qty'] > need:
            l['note'] = (l.get('note', '') + f'; {need} used, {l["qty"]} bought (Ozdisan MOQ)').strip('; ')
    def rank(l):
        r = l['refs'][0]
        for i, pre in enumerate(('U', 'Q', 'L', 'RS1', 'RSN', 'J', 'D', 'C', 'R', '(')):
            if r.startswith(pre):
                return (i, natural(r))
        return (99, natural(r))
    order = sorted(lines.values(), key=rank)
    os.makedirs(OUT, exist_ok=True)
    # ---- course format
    rows = [[group, '', '', '', '', '', '', ''],
            ['Part Number', 'Short Description', 'Digikey / Mouser Link', 'Turkish Supplier Link (if available)', 'Quantity',
             'Unit Price (USD)', 'Total Price (USD)', 'Group Total Budget (USD)']]
    first = 3
    for i, l in enumerate(order):
        r = first + i
        desc = f"{l['desc']} [{', '.join(l['refs'])}]"
        rows.append([l['mpn'], desc, l['dk'], l.get('tr', ''), l['qty'], f"{l['price']:.5f}".rstrip('0').rstrip('.'),
                     f'=E{r}*F{r}', f'=SUM(G{first}:G{first + len(order) - 1})' if i == 0 else ''])
    with open(os.path.join(OUT, 'BOM_course_format.csv'), 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)
    with open(os.path.join(OUT, 'BOM_course_format.tsv'), 'w', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t').writerows(rows)
    # ---- full engineering BOM
    with open(os.path.join(OUT, 'BOM_full.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['References', 'Qty', 'Value', 'Manufacturer', 'MPN', 'Description', 'Footprint', 'Datasheet',
                    'DigiKey', 'Unit USD', 'Line USD', 'Notes'])
        for l in order:
            w.writerow([' '.join(l['refs']), l['qty'], l['value'], l['mfr'], l['mpn'], l['desc'], l['fp'], l['datasheet'],
                        l['dk'], l['price'], round(l['qty'] * l['price'], 3), l.get('note', '')])
        for ref, why in NOT_BOUGHT.items():
            w.writerow([ref, 1, '', '', '', why, fps.get(ref, ''), '', '', 0, 0, 'not purchased'])
    total = sum(l['qty'] * l['price'] for l in order)
    print(f'{len(order)} lines, {sum(l["qty"] for l in order)} parts, total {total:.2f} USD; 0603 kept: {kept0603}')
    write_readme(order, total, kept0603, group)
    return total, kept0603, order


def write_readme(order, total, kept0603, group):
    warn = [l for l in order if any(k in l.get('note', '') for k in ('backorder', 'restock', '0 stock', 'not sold by DigiKey'))]
    L = ['# Bill of materials (RevF2)', '',
         f'**{sum(l['need'] for l in order if 'need' in l)} parts used, {sum(l['qty'] for l in order)} pieces bought (MOQ), {len(order)} lines, {total:.2f} USD** for one board '
         '(DigiKey US cut-tape prices, or Ozdisan prices for the lines with a Turkish link, checked on 2026-11-19; shipping, VAT and duty not included). '
         'Course budget: 100 USD per group.', '',
         '| File | Use |', '|---|---|',
         '| `BOM_course_format.csv` / `.tsv` | Same columns as the course sponsorship sheet. Paste the `.tsv` into the copied sheet at cell A1; totals are formulas. |',
         '| `BOM_full.csv` | Engineering BOM: references, values, footprints, manufacturer, datasheet links, notes. |', '',
         '## Course rules applied', '',
         '- **No Israel-made parts.** Vishay parts of RevF1 were replaced: shunt WSL25124L000FEA -> Yageo PA2512FKF7W0R004E '
         '(same 3.05 x 3.68 mm land pattern), snubber resistor CRCW12062R20FKEAHP -> Panasonic ERJ-P08J2R2V (anti-surge, 0.66 W; '
         'snubber dissipation 1 nF x 48 V^2 x 94.3 kHz = 0.22 W), BAT54-E3-08 -> onsemi BAT54LT1G (same SOT-23 pinout). '
         'No Vishay / Vitramon / Dale / Siliconix / Sfernice / BCcomponents part is left. Watch DigiKey substitutions: they often offer Vishay Vitramon capacitors.',
         '- **0805 or larger.** All resistors and capacitors are 0805 or larger except: ' + (', '.join(kept0603) or 'none') +
         '. These sit in the densest routing next to the controller and the op amps; enlarging them would need re-routing. Their 0603 part numbers are standard Yageo values, linked as DigiKey searches (stock not checked one by one) '
         '(course rule: 0603 allowed for a few parts). No 0402.',
         '- **Assembly:** reflow oven + paste dispenser (no stencil). Finest pitch: LTC3895 TSSOP-38, 0.5 mm.', '',
         '## Order early / stock warnings', '']
    for l in warn:
        L.append(f"- `{l['mpn']}` ({', '.join(l['refs'])}): {l['note']}")
    trl = [l for l in order if l.get('tr')]
    L += ['', '## Turkish stock (Ozdisan, checked 2026-11-19)', '',
          f'{len(trl)} of {len(order)} lines are in stock at Ozdisan (link in the "Turkish Supplier Link" column). Where the DigiKey part '
          'was not stocked in Turkey, it was replaced by an equivalent that is (same value, package, tolerance or better, dielectric '
          'class, voltage/power). Prices of these lines are Ozdisan prices (USD, VAT excluded); the quantity is rounded up to the '
          'Ozdisan minimum order (for example 100 pcs for Royal Ohm resistors, a few cents in total). '
          'Not available in Turkey, bought from DigiKey / Coilcraft: the ADI ICs, LM74700, the MOSFETs, XAL1510, OS-CON, Rubycon, '
          'Phoenix terminals, the shunt, 100 V 0805 X7R (100 nF, 22 nF), C0G 1 nF/100 V and 27 nF, 4.7 Ohm 1%, the 2.2 Ohm pulse '
          'resistor and the 0.1% 140k / 11.8k. DAUX1/DCL1 use the Hottech BAT54S (dual, series): diode 1 sits on pins 1/3 exactly like '
          'the single BAT54, pin 2 is a no-connect pad on the PCB.', '',
          '| Part | Replaces | Ozdisan |', '|---|---|---|']
    for l in trl:
        rep = l.get('note', '').split('replaces ')[-1].split(' ')[0] if 'replaces' in l.get('note', '') else '(same part)'
        L.append(f"| {l['mpn']} ({', '.join(l['refs'])}) | {rep} | [link]({l['tr']}) |")
    L += ['', '## Changes against the RevF1 BOM', '',
          '| Ref | RevF1 | RevF2 | Reason |', '|---|---|---|---|',
          '| RS1 | Vishay WSL25124L000FEA | Yageo PA2512FKF7W0R004E | Israel-made rule; same land pattern |',
          '| RSN1 | Vishay CRCW12062R20FKEAHP | Panasonic ERJ-P08J2R2V | Israel-made rule |',
          '| DAUX1, DCL1 | Vishay BAT54-E3-08 | onsemi BAT54LT1G | Israel-made rule |',
          '| 24 of the 30 0603 R/C | 0603 | 0805 (moved 0-0.38 mm on the PCB, DRC clean) | course package rule |',
          '| CIN1-10 | TDK C3225X7R2A225K230AB | Samsung CL32B225KCJSNNE | TDK out of stock (same 2.2 uF / 100 V / 1210 X7R) |',
          '| CINB1-3 | Panasonic EEU-FR2A101 | Rubycon 100ZLH100MEFC10X20 | out of stock (same 100 uF / 100 V, D10, P5) |',
          '| CDRV1, CBOOT1, CREF1/CAUX1, CITH1, CSN1 | Murata/TDK (obsolete or not on DigiKey) | equivalents | availability |',
          '| RGH1, RGL1, RERR1 | Yageo RC0805 | Panasonic ERJ-6 | Yageo value out of stock |',
          '| CCATH1 | - | Yageo CC1206KKX7R0BB105 1 uF / 100 V | LM74700 CATHODE capacitor (hot-plug), see PCB notes |', '',
          '## Spares', '', 'Compensation B parts (3.9 k, 68 nF C0G, 1 nF C0G) are bought for the line/load transient bonus. '
          f'About {100 - total:.0f} USD of the budget is left; useful extra spares: one more of each MOSFET and the LTC3895.', '']
    open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main(*sys.argv[1:3])
