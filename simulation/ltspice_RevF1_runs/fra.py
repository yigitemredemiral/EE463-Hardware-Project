"""Parse LTspice .fra complex raw and report crossover, phase margin, gain margin."""
import sys, re, numpy as np
def read_complex_raw(path):
    b = open(path, 'rb').read(); key = 'Binary:\n'.encode('utf-16-le'); i = b.index(key)
    hdr = b[:i].decode('utf-16-le'); body = b[i + len(key):]
    nv = int(re.search(r'No\. Variables:\s*(\d+)', hdr).group(1)); npt = int(re.search(r'No\. Points:\s*(\d+)', hdr).group(1))
    names = re.findall(r'^\t\d+\t(\S+)\t', hdr, re.M)
    a = np.frombuffer(body, dtype='<c16', count=nv * npt).reshape(npt, nv)
    return hdr, {n: a[:, k] for k, n in enumerate(names)}
def analyse(path):
    hdr, d = read_complex_raw(path)
    f = np.abs(d['frequency'].real) if 'frequency' in d else np.abs(list(d.values())[0].real)
    keys = [k for k in d if k.lower() != 'frequency']
    out = {'vars': keys}
    T = d[keys[0]]
    mag = 20 * np.log10(np.abs(T)); ph = np.degrees(np.unwrap(np.angle(T)))
    out['table'] = [(float(a), float(b), float(c)) for a, b, c in zip(f, mag, ph)]
    # LTspice .fra displays phase as 180 deg + angle(T) (verified: ~45 deg at 500 Hz for an integrator+output-pole loop),
    # so the displayed phase at the 0 dB crossing IS the phase margin; gain margin where the displayed phase crosses 0.
    phw = ((ph + 180) % 360) - 180
    i = np.flatnonzero((mag[:-1] > 0) & (mag[1:] <= 0))
    if len(i):
        k = i[0]; x = (0 - mag[k]) / (mag[k + 1] - mag[k])
        out['fc_Hz'] = float(10 ** (np.log10(f[k]) + x * (np.log10(f[k + 1]) - np.log10(f[k]))))
        out['PM_deg'] = float(phw[k] + x * (phw[k + 1] - phw[k]))
        j = [m for m in range(k, len(f) - 1) if phw[m] > 0 >= phw[m + 1]]
        if j:
            m = j[0]; y = phw[m] / (phw[m] - phw[m + 1])
            out['GM_dB'] = float(-(mag[m] + y * (mag[m + 1] - mag[m]))); out['GM_freq'] = float(f[m] * (f[m + 1] / f[m]) ** y)
        else:
            out['GM_dB'] = None; out['GM_lower_bound_dB'] = float(-mag[-1]); out['f_max'] = float(f[-1])
    return out
if __name__ == '__main__':
    import json
    for p in sys.argv[1:]:
        o = analyse(p); print(p, json.dumps({k: v for k, v in o.items() if k != 'table'}))
        for row in o['table']: print('   %9.1f Hz %7.2f dB %8.1f deg' % row)
