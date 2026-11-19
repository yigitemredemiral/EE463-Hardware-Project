"""Official Infineon OptiMOS5 80V models (models/infineon/OptiMOS5/OptiMOS5_80V_LTSpice.lib, version 280225, level _L0 (see LEVEL). Replaces the scaled BSC040 VDMOS (Q1), the LTspice-library BSC026 VDMOS (Q2)
and, in the ideal-diode configs, Q3. Drain currents are measured with 0 V sources (VaQ1/VaQ2/VaRP) because LTspice batch
does not write subcircuit pin currents.
Solver: the models do not converge with default settings in this converter (time step too small at the first edges,
node x?:x1:e_eds3); OPT (cshunt 1e-15, reltol 3e-3, abstol 1 nA, vntol 10 uV) + uic cold start works."""
import gen, gen2
LIB = '.lib ../models/infineon/OptiMOS5/OptiMOS5_80V_LTSpice.lib'
# _L1 (temperature-dependent, detailed capacitances) does not run in this converter in practical time: with default options
# it fails at the first edges; with cshunt it crawls (~0.2 ns steps, package L + cshunt). _L0 (same library: level-3 MOS,
# body diode with TT, switched Cgd, package L, TC on Rd/Rs) runs ~as fast as VDMOS -> used for all official-model runs.
LEVEL = '_L0'
OPT = '.options reltol=0.003 abstol=1e-9 vntol=1e-5 itl4=200 cshunt=1e-15'
EXTRA = LIB + '\n' + OPT + '\n.save V(TG) V(BG) V(GHI) V(GLI) V(GH) V(GL)'
def official(q1='BSC040N08NS5'):
    return [(f'MQ1 QD GH SW {q1}', f'VaQ1 QD QDX 0\nXQ1 QDX GH SW {q1}{LEVEL}'),
            ('MQ2 SW GL 0 BSC026N08NS5', f'VaQ2 SW SWX 0\nXQ2 SWX GL 0 BSC026N08NS5{LEVEL}'),
            ('Id(MQ1) Id(MQ2)', 'I(VaQ1) I(VaQ2)')]
def ideal_official(ideal=None):
    r = ideal or gen2.ideal_diode()
    return [(a, b.replace('MRP CABLE GRP UNPROTECTED BSC026N08NS5', f'VaRP CABLE CABX 0\nXRP CABX GRP UNPROTECTED BSC026N08NS5{LEVEL}')
                 .replace('I(MRP)', 'I(VaRP)')) for a, b in r]
