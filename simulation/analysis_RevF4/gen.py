"""Generate LTspice netlist variants from base.net and run them in parallel (LTspice -b)."""
import re, subprocess, sys, os
base = open('base.net', encoding='latin-1').read()
SAVE = ('.save V(OUT) V(SW) V(IN) V(SOURCE) V(QD) V(CABLE) V(UNPROTECTED) V(LOUT) V(SENSEP) V(ITH) V(GH) V(GL) '
        'V(INTVCC) V(SS) V(RUN) V(PGOOD) I(L1) I(V1) I(Rload) Id(MQ1) Id(MQ2) Id(MQ3) I(CINcer) I(CINbulk) I(COUT) I(RS1) I(Rsource)')
RUNS = {
    # name: (VIN, RL, tstop, tsave, extra)
    's20': (20, 2.4, '14m', '10m', None), 's24': (24, 2.4, '14m', '10m', None),
    's36': (36, 2.4, '14m', '10m', None), 's48': (48, 2.4, '14m', '10m', None),
    'h24': (24, 1.6, '14m', '10m', None), 'h48': (48, 1.6, '14m', '10m', None),
    'l24_30': (24, 4.8, '14m', '10m', None), 'l24_15': (24, 9.6, '14m', '10m', None), 'l24_6': (24, 24, '14m', '10m', None),
    'l48_30': (48, 4.8, '14m', '10m', None), 'l48_15': (48, 9.6, '14m', '10m', None), 'l48_6': (48, 24, '14m', '10m', None),
    'step24': (24, 2.4, '15m', '7m', 'step'), 'line': (24, 2.4, '15m', '7m', 'line'),
    'fault': (24, 2.4, '14m', '5m', 'fault'), 'start48': (48, 2.4, '14m', '0', None), 'start24': (24, 2.4, '14m', '0', None),
    'fra20': (20, 2.4, '40m', '2m', 'fra'), 'fra24': (24, 2.4, '40m', '2m', 'fra'), 'fra36': (36, 2.4, '40m', '2m', 'fra'), 'fra48': (48, 2.4, '40m', '2m', 'fra'),
}
procs = []
for n, (vin, rl, ts, t0, ex) in RUNS.items():
    if len(sys.argv) > 1 and n not in sys.argv[1:]: continue
    s = base.replace('.param VIN=24 RL=2.4 TEST=0', f'.param VIN={vin} RL={rl} TEST={1 if ex == "fault" else 0}')
    s = re.sub(r'\.tran .*', f'.tran 0 {ts} {t0} 100n', s)
    s = re.sub(r'\.save .*', SAVE, s)
    if ex == 'step':
        s = re.sub(r'Rload OUT 0 R=.*', 'Rload OUT 0 R={table(time,0,RL,9m,RL,9.002m,2*RL,12m,2*RL,12.002m,RL)}', s)
    if ex == 'line':
        s = s.replace('V1 SOURCE 0 {VIN}', 'V1 SOURCE 0 PWL(0 24 9m 24 9.1m 36 12m 36 12.1m 24)')
    if ex == 'fra':
        s = re.sub(r'@LOOP .*', '@LOOP OUT FBOUT fstart=500 fend=50000 oct=2 delay=3m pp0=40m pp1=15m f0=2k f1=10k tsettle=1m tavgmin=1m nmax=1', s)
    else:
        s = re.sub(r'@LOOP OUT FBOUT .*', 'Vloop OUT FBOUT 0', s)
    open(n + '.net', 'w', encoding='latin-1').write(s)
    procs.append((n, subprocess.Popen([r'C:\Program Files\ADI\LTspice\LTspice.exe', '-b', n + '.net'])))
for n, p in procs: p.wait(); print(n, 'done', p.returncode, flush=True)
