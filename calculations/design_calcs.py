"""EE463 RevF2 synchronous buck: analytical design calculations (pre-report section 3).

Run: python calculations/design_calcs.py  -> prints the tables used in reports/PreReport.md and writes
calculations/design_calcs.json. All values are hand calculations from datasheet numbers (no simulation)."""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
# ---- specification
VIN = [20, 24, 36, 48]
VOUT = 12.0
POUT = {'60W': 60.0, '90W': 90.0}
# ---- design values
FSW = 94.3e3                    # RFREQ 24.3k (LTC3895 FREQ resistor), confirmed in simulation
L = 33e-6                       # Coilcraft XAL1510-333 (+-20 %)
DCR = 18.7e-3                   # typ, 20.0 max
COUT = 2 * 330e-6               # 2 x Panasonic 25SVPF330M
ESR_OUT = 16e-3 / 2             # 25SVPF330M ESR 16 mOhm each (datasheet max)
CIN_CER = 10 * 2.2e-6 * 0.45    # 10 x 2.2 uF X7R, about 45 % left at 48 V DC bias
RS = 4e-3                       # current-sense shunt
RDS_Q1, RDS_Q2 = 4.0e-3, 2.6e-3  # BSC040N08NS5 / BSC026N08NS5, max at 25 C, VGS = 10 V
TC = 1.5                        # Rds(on) factor at Tj ~ 100 C
QG_Q1, QG_Q2 = 43e-9, 74e-9     # total gate charge at 10 V
QGD_Q1, QGS2_Q1 = 6e-9, 5e-9    # BSC040N08NS5 Qgd, Qgs2 (approx. datasheet typ)
VDRV, RDRV_UP, RDRV_DN = 10.0, 2.2 + 4.7 + 1.1, 1.0 + 4.7 + 1.1   # driver + RGH + internal Rg (Ohm)
VPL = 4.8                       # Miller plateau of BSC040N08NS5 at ~6 A
QRR = 40e-9                     # Q2 body-diode reverse recovery charge (dead time conduction), datasheet typ
TDEAD = 2 * 30e-9               # two dead times per cycle
VF_BODY = 0.8


def point(vin, pout):
    io = pout / VOUT
    d = VOUT / vin
    dil = VOUT * (1 - d) / (L * FSW)
    ipk = io + dil / 2
    irms_l = math.sqrt(io ** 2 + dil ** 2 / 12)
    irms_q1 = irms_l * math.sqrt(d)
    irms_q2 = irms_l * math.sqrt(1 - d)
    icin_rms = io * math.sqrt(d * (1 - d))
    dv_c = dil / (8 * FSW * COUT)
    dv_esr = dil * ESR_OUT
    # losses
    p_q1_cond = irms_q1 ** 2 * RDS_Q1 * TC
    i_on, i_off = io - dil / 2, io + dil / 2
    t_rise = (QGD_Q1 + QGS2_Q1) * RDRV_UP / (VDRV - VPL)
    t_fall = (QGD_Q1 + QGS2_Q1) * RDRV_DN / VPL
    p_q1_sw = 0.5 * vin * (i_on * t_rise + i_off * t_fall) * FSW
    p_q2_cond = irms_q2 ** 2 * RDS_Q2 * TC
    p_dead = VF_BODY * io * TDEAD * FSW
    p_qrr = QRR * vin * FSW
    p_gate = (QG_Q1 + QG_Q2) * VDRV * FSW * (VDRV / VOUT)     # DRVCC from EXTVCC = 12 V (LDO)
    p_l = irms_l ** 2 * DCR
    p_rs = io ** 2 * RS
    p_cout = (dil / math.sqrt(12)) ** 2 * ESR_OUT
    p_q3 = (pout / vin) ** 2 * 2.6e-3 * TC
    p_ctrl = 12 * 3e-3 + 5 * 2e-3               # controller + analog aux (EXTVCC 12 V)
    loss = dict(q1_cond=p_q1_cond, q1_sw=p_q1_sw, q2_cond=p_q2_cond, deadtime=p_dead, qrr=p_qrr, gate=p_gate,
                inductor_dcr=p_l, shunt=p_rs, cout_esr=p_cout, ideal_diode=p_q3, controller_aux=p_ctrl)
    ptot = sum(loss.values())
    return dict(vin=vin, pout=pout, io=io, duty=d, dil_app=dil, il_peak=ipk, il_rms=irms_l, irms_q1=irms_q1,
                irms_q2=irms_q2, icin_rms=icin_rms, ripple_mvpp=(dv_c + dv_esr) * 1e3, t_rise_ns=t_rise * 1e9,
                t_fall_ns=t_fall * 1e9, losses=loss, p_loss=ptot, eff=pout / (pout + ptot))


def main():
    res = {}
    print(f'fsw = {FSW / 1e3:.1f} kHz, L = {L * 1e6:.0f} uH, Cout = {COUT * 1e6:.0f} uF (ESR {ESR_OUT * 1e3:.0f} mOhm)\n')
    hdr = 'Vin   P    D     dIL(A) IL,pk  IQ1rms IQ2rms ICin,rms  ripple(mVpp)  Ploss(W)  eff(%)'
    print(hdr)
    for pk, p in POUT.items():
        for v in VIN:
            r = point(v, p); res[f'{v}V_{pk}'] = r
            print(f'{v:3d} {p:4.0f}  {r["duty"]:.3f}  {r["dil_app"]:5.2f}  {r["il_peak"]:5.2f}  {r["irms_q1"]:5.2f}  '
                  f'{r["irms_q2"]:5.2f}  {r["icin_rms"]:6.2f}   {r["ripple_mvpp"]:8.1f}      {r["p_loss"]:5.2f}   {100 * r["eff"]:6.2f}')
    print('\nloss breakdown (W) at 48 V / 60 W:')
    for k, v in res['48V_60W']['losses'].items():
        print(f'  {k:15s} {v:6.3f}')
    eff_avg = sum(res[f'{v}V_60W']['eff'] for v in VIN) / 4
    print(f'\nhand-calculated 4-point average efficiency at 60 W: {100 * eff_avg:.2f} %  '
          f'(bonus B = {100 * (eff_avg - 0.8):.1f} points if measured like this)')
    # component stresses
    print('\nstresses: VDS(Q1,Q2) = Vin,max = 48 V + ringing (sim 49.6 V) vs 80 V rating -> 60 % derating OK')
    print(f'  L1 peak current at 48 V / 90 W: {res["48V_90W"]["il_peak"]:.2f} A vs Isat 16.7 A, Irms 8.6 A (20 C rise)')
    print(f'  CIN RMS current max: {max(r["icin_rms"] for r in res.values()):.2f} A shared by 10 x 1210 + 3 electrolytics')
    # compensation / loop
    gm, hdiv, gi = 2e-3, 10 / 150, 12.4
    for name, rith in (('A', 8.2e3), ('B', 3.9e3)):
        fc = hdiv * gm * rith * gi / (2 * math.pi * COUT)
        print(f'  compensation {name}: fc ~ {fc:.0f} Hz')
    # thermal
    rth = 38.0
    p = res['48V_90W']['losses']['q1_cond'] + res['48V_90W']['losses']['q1_sw'] + res['48V_90W']['losses']['qrr']
    print(f'\nQ1 at 48 V / 90 W: {p:.2f} W -> Tj = 40 C + {rth:.0f} K/W x P = {40 + rth * p:.0f} C (copper + 12 vias, no heatsink)')
    json.dump(res, open(os.path.join(HERE, 'design_calcs.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
