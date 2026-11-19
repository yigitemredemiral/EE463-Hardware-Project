"""Parallel LTspice batch runner with one retry (alternate integration method) on failure."""
import os, sys, subprocess, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
LT = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'ADI', 'LTspice', 'LTspice.exe')

def ok(name):
    p = os.path.join(HERE, name + '.log')
    if not os.path.exists(p): return False
    t = open(p, 'rb').read().decode('latin-1', 'ignore')
    return 'Total elapsed time' in t and 'aborted' not in t.lower() and 'simulation failed' not in t.lower()

def run1(name):
    t0 = time.time()
    subprocess.run([LT, '-b', name + '.cir'], cwd=HERE)
    if ok(name):
        return name, 'ok', time.time() - t0
    # retry once with alternate method
    p = os.path.join(HERE, name + '.cir')
    s = open(p, encoding='latin-1').read()
    if '.options method=gear' in s:
        s = s.replace('.options method=gear', '.options method=trap reltol=2m')
    else:
        s = s.replace('.tran', '.options method=gear\n.tran', 1)
    open(p, 'w', encoding='latin-1', newline='\r\n').write(s)
    subprocess.run([LT, '-b', name + '.cir'], cwd=HERE)
    return name, ('ok-retry' if ok(name) else 'FAILED'), time.time() - t0

def run(names, n=8):
    with ThreadPoolExecutor(n) as ex:
        res = list(ex.map(run1, names))
    for r in res: print(f'{r[0]:40s} {r[1]:9s} {r[2]:6.0f}s', flush=True)
    return res

if __name__ == '__main__':
    run(sys.argv[1:])
