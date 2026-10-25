"""
resolve_continuous_threshold_modulation.py

Rigorous, non-aliased analysis of gate-dependent threshold modulation under dynamic load (R_L = 50 kOhm).

SCIENTIFIC AUDIT CORRECTIONS:
1. Evaluates BOTH milestone criteria separately and explicitly:
   - Criterion A: Percolation Threshold (fm = 1/3 ~ 0.333333)
   - Criterion B: Transition Midpoint   (fm = 0.500000)
2. Uses IDENTICAL criteria for continuous and sampled comparisons.
3. Dynamically extracts discrete 0.5 ns sampled thresholds (no hardcoding).
4. Demonstrates continuous event detection vs discrete 80 mV binning across gate voltages.
5. Performs fine-grid discrete ramp integration (dt = 0.01 ns -> 1.6 mV/step) across the transition window.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from giv_pts_model import (
    get_config,
    ramp_waveform,
    solve_device_state,
    create_ode_system,
    initial_metallic_fraction,
)

def make_event(crit):
    def switch_event(t, y):
        return y[0] - crit
    switch_event.direction = 1  # positive crossing
    switch_event.terminal = True
    return switch_event

def main():
    print("=" * 80)
    print("AUTHORITATIVE DYNAMIC THRESHOLD MODULATION AUDIT")
    print("Identical Criteria for Continuous vs Sampled Comparisons")
    print("=" * 80)

    cfg = get_config()
    vg_values = [0.0, 0.5, 1.0, 1.5, 2.0]
    ramp_duration = 100.0e-9  # 100 ns ramp duration
    
    # 0.5 ns sampling grid (201 points over 100 ns, 101 points over 50 ns rise)
    t_grid_0p5ns = np.linspace(0.0, ramp_duration, 201)
    t_grid_rise = t_grid_0p5ns[t_grid_0p5ns <= 50.0e-9]

    criteria = [
        ("Percolation (fm = 1/3)", 1.0 / 3.0),
        ("Midpoint (fm = 0.50)", 0.50)
    ]

    all_records = []

    for crit_name, crit_val in criteria:
        print(f"\n>>> Evaluating Milestone: {crit_name} (fm_threshold = {crit_val:.4f})")
        crit_records = []

        for vg in vg_values:
            fm_init = initial_metallic_fraction(vg, cfg=cfg, is_graphene=True)
            ode_func = create_ode_system(
                vg,
                lambda t: ramp_waveform(t, max_voltage=8.0, ramp_period=ramp_duration),
                cfg=cfg,
                is_graphene=True
            )

            # 1. Continuous Event Detection via Radau stiff ODE solver
            sol_cont = solve_ivp(
                ode_func,
                (0.0, 50.0e-9),
                [fm_init, cfg.T_amb],
                events=make_event(crit_val),
                rtol=1e-10,
                atol=1e-12,
                method='Radau'
            )

            if len(sol_cont.t_events[0]) > 0:
                t_cont = sol_cont.t_events[0][0]
                fm_cont = sol_cont.y_events[0][0][0]
                T_cont = sol_cont.y_events[0][0][1]
                v_app_cont = ramp_waveform(t_cont, max_voltage=8.0, ramp_period=ramp_duration)
                vd_cont, id_cont, _, _, _, _ = solve_device_state(v_app_cont, fm_cont, T_cont, cfg=cfg)
            else:
                t_cont = np.nan
                v_app_cont = np.nan
                vd_cont = np.nan
                id_cont = np.nan
                T_cont = np.nan

            # 2. Discrete 0.5 ns Sampled Detection (Identical Simulation evaluated on 0.5 ns grid)
            sol_disc = solve_ivp(
                ode_func,
                (0.0, 50.0e-9),
                [fm_init, cfg.T_amb],
                t_eval=t_grid_rise,
                rtol=1e-8,
                atol=1e-10,
                method='Radau'
            )

            idx_cross = np.where(sol_disc.y[0] >= crit_val)[0]
            if len(idx_cross) > 0:
                idx_first = idx_cross[0]
                t_disc = sol_disc.t[idx_first]
                fm_disc = sol_disc.y[0][idx_first]
                T_disc = sol_disc.y[1][idx_first]
                v_app_disc = ramp_waveform(t_disc, max_voltage=8.0, ramp_period=ramp_duration)
                vd_disc, id_disc, _, _, _, _ = solve_device_state(v_app_disc, fm_disc, T_disc, cfg=cfg)
            else:
                t_disc = np.nan
                v_app_disc = np.nan
                fm_disc = np.nan
                vd_disc = np.nan
                id_disc = np.nan
                T_disc = np.nan

            rec = {
                "Criterion": crit_name,
                "fm_threshold": crit_val,
                "V_G_V": vg,
                # Continuous quantities
                "Continuous_t_switch_ns": t_cont * 1e9,
                "Continuous_V_app_SET_V": v_app_cont,
                "Continuous_V_D_SET_V": vd_cont,
                "Continuous_I_D_SET_uA": id_cont * 1e6 if not np.isnan(id_cont) else np.nan,
                "Continuous_T_avg_SET_K": T_cont,
                # Sampled quantities (0.5 ns grid, 80 mV step)
                "Sampled_0p5ns_t_switch_ns": t_disc * 1e9,
                "Sampled_0p5ns_V_app_SET_V": v_app_disc,
                "Sampled_0p5ns_fm_at_sample": fm_disc,
                "Sampled_0p5ns_V_D_SET_V": vd_disc,
                "Sampled_0p5ns_I_D_SET_uA": id_disc * 1e6 if not np.isnan(id_disc) else np.nan,
                "Sampled_0p5ns_T_avg_SET_K": T_disc,
            }
            crit_records.append(rec)
            all_records.append(rec)

            print(f"  V_G = {vg:.1f} V | "
                  f"Continuous: t = {t_cont*1e9:.4f} ns, V_app = {v_app_cont:.4f} V, V_D = {vd_cont:.4f} V | "
                  f"Sampled (0.5 ns): t = {t_disc*1e9:.1f} ns, V_app = {v_app_disc:.2f} V (fm = {fm_disc:.3f})")

        # Calculate shifts relative to VG = 0 V
        df_c = pd.DataFrame(crit_records)
        v_app_cont_vg0 = df_c.loc[df_c['V_G_V'] == 0.0, 'Continuous_V_app_SET_V'].values[0]
        v_app_disc_vg0 = df_c.loc[df_c['V_G_V'] == 0.0, 'Sampled_0p5ns_V_app_SET_V'].values[0]

        delta_cont_2V = (v_app_cont_vg0 - df_c.loc[df_c['V_G_V'] == 2.0, 'Continuous_V_app_SET_V'].values[0]) * 1000.0
        delta_disc_2V = (v_app_disc_vg0 - df_c.loc[df_c['V_G_V'] == 2.0, 'Sampled_0p5ns_V_app_SET_V'].values[0]) * 1000.0

        print(f"  --> Total Continuous Shift (0 to 2 V): {delta_cont_2V:.2f} mV")
        print(f"  --> Total Sampled Shift    (0 to 2 V): {delta_disc_2V:.2f} mV (Resolution limit: 80 mV)")

    df_all = pd.DataFrame(all_records)
    out_csv = os.path.join(script_dir, "..", "hysteresis", "continuous_threshold_modulation.csv")
    df_all.to_csv(out_csv, index=False)
    print(f"\n[INFO] Saved complete threshold comparison table to: {out_csv}")

    # -------------------------------------------------------------
    # Fine-Grid Discrete Sampling across transition window
    # -------------------------------------------------------------
    print("\n[PART 2] Fine-Grid Integration (dt = 0.01 ns -> 1.6 mV/step)...")
    t_eval_fine_s = np.linspace(33.0e-9, 42.0e-9, 901)
    fine_traces = []

    for vg in [0.0, 1.0, 2.0]:
        fm_init = initial_metallic_fraction(vg, cfg=cfg, is_graphene=True)
        ode_func = create_ode_system(
            vg,
            lambda t: ramp_waveform(t, max_voltage=8.0, ramp_period=ramp_duration),
            cfg=cfg,
            is_graphene=True
        )

        sol_fine = solve_ivp(
            ode_func,
            (0.0, 42.0e-9),
            [fm_init, cfg.T_amb],
            t_eval=t_eval_fine_s,
            rtol=1e-8,
            atol=1e-10,
            method='Radau'
        )

        for i, t in enumerate(sol_fine.t):
            fm = sol_fine.y[0][i]
            T = sol_fine.y[1][i]
            v_app = ramp_waveform(t, max_voltage=8.0, ramp_period=ramp_duration)
            vd, id_, _, _, _, _ = solve_device_state(v_app, fm, T, cfg=cfg)
            fine_traces.append({
                "time_ns": t * 1e9,
                "V_G_V": vg,
                "V_app_V": v_app,
                "V_D_V": vd,
                "I_D_uA": id_ * 1e6,
                "T_avg_K": T,
                "fm_avg": fm
            })

    df_fine = pd.DataFrame(fine_traces)
    out_fine = os.path.join(script_dir, "..", "hysteresis", "fine_ramp_threshold_resolution.csv")
    df_fine.to_csv(out_fine, index=False)
    print(f"[INFO] Saved fine-grid threshold resolution to: {out_fine}")
    print("=" * 80)

if __name__ == "__main__":
    main()
