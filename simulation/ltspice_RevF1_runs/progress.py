"""Simulated time reached by running LTspice batch jobs (reads the partially written binary .raw)."""
import sys, re, os, struct
for n in sys.argv[1:]:
    p = n + '.raw'
    if not os.path.exists(p): print(n, 'no raw'); continue
    b = open(p, 'rb').read(); key = 'Binary:\n'.encode('utf-16-le'); i = b.find(key)
    if i < 0: print(n, 'no header yet'); continue
    hdr = b[:i].decode('utf-16-le'); nv = int(re.search(r'No\. Variables:\s*(\d+)', hdr).group(1))
    row = 8 + 4 * (nv - 1); body = len(b) - i - len(key); k = body // row
    t = struct.unpack('<d', b[i + len(key) + (k - 1) * row: i + len(key) + (k - 1) * row + 8])[0] if k else 0
    print(f'{n:40s} t = {abs(t)*1e3:7.3f} ms  ({k} points)')
