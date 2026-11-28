"""rip-up and retry: nets that failed go to the front of the order. python tools/revg_iter.py"""
import os, subprocess, shutil, re
PY = r'C:/Program Files/KiCad/10.0/bin/python.exe'
first = ['/SW', '/BOOST', '/TG', '/BG', '/SS', '/VOUT', '/ITH']
best = None
for it in range(20):
    shutil.copy('build/g_placed.kicad_pcb', 'build/g_r.kicad_pcb')
    env = dict(os.environ, FIRST=','.join(first))
    out = subprocess.run([PY, '-u', 'tools/revg_route.py', 'build/g_r.kicad_pcb'], env=env, capture_output=True, text=True).stdout
    fails = re.findall(r'FAIL \S+ \S+ (\S+)', out)
    nf = len(set(fails)); print(it, nf, sorted(set(fails)), flush=True)
    if best is None or nf < best:
        best = nf; shutil.copy('build/g_r.kicad_pcb', 'build/g_best.kicad_pcb')
    if nf == 0:
        break
    for n in fails:
        if n in first:
            first.remove(n)
    first = list(dict.fromkeys([n for n in fails if n.startswith('/')] + first))
print('best', best)
