"""Hot plug re-run with the board inductance between Q3 and the input caps corrected (base netlist Lcable 200 nH sits after
the reverse-polarity element and double counts the cable once Lcab is modelled; RevF1 layout: Q3 drain -> VIN pour ->
33 vias -> In2 plane, ~20 nH). Options: with / without a 1 uF 100 V X7R cathode cap at the Q3 drain (LM74700 COUT >= 0.1 uF)."""
import sys; sys.argv = [sys.argv[0], "lib"]
import gen10, gen
names = []
for cab, (L, R) in {'1u': ('1u', '50m'), '0p5u': ('0.5u', '20m')}.items():
    for cc in (False, True):
        n = f'RevF1_G_hotplug48_cable{cab}_lb20n' + ('_ccath1u' if cc else '')
        gen10.mk(n, vin=48, tstop='3m', state='none', extra=('\nCcath CABLE 0 1u Rser=5m Lser=1n' if cc else ''), overrides={'gear': 1, 'replace': [
            ('V1 SOURCE 0 {VIN}\n', 'V1 SOURCE 0 PWL(0 0 1u 0 1.001u 48)\n'),
            ('Rsource SOURCE UNPROTECTED 50m', f'Rsource SOURCE NCAB {R}\nLcab NCAB UNPROTECTED {L}\nCanode UNPROTECTED 0 22n'),
            ('Lcable CABLE IN 200n', 'Lcable CABLE IN 20n')]})
        names.append(n)
print(' '.join(names))
