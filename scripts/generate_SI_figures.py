"""generate_SI_figures.py

Generates all Supplementary Information figures strictly synchronized with the authoritative,
reconciled device-physics model, physical sheet parameters, and FEA calibrations:
- Fig S1: Quantum Capacitance Partition & Transferred Sheet Density
- Fig S2: Gate-Dependent Equilibrium Phase Curves (Five Gate Biases)
- Fig S3: Native Equilibrium Initialization & 3.175 V Half-Pulse Trajectory (6.35 V Protocol)
- Fig S4: Paired Gate-Coupling & Thermal Sensitivity Analysis
- Fig S5: Dynamic Threshold Modulation: First fm = 1/3 and fm = 0.50 Crossings
- Fig S6: Event Convergence & Time-Step Stability (fs-Scale Invariance)
- Fig S7: Ramp Sampling Limitations & Discrete Binning vs. Continuous Thresholds
- Fig S8: Prescribed-Heating Thermal Calibration (Gr ON k=201 W/mK vs Gr OFF)
- Fig S9: Quantitative TBR Penalties from 3D FEA (Table S4 Alignment)
- Fig S10: Principal-ROM Circuit Quantities & 50 kOhm Load-Line Compliance
- Fig S11: Thickness-Dependent 2D Spatial Thermal Maps (Fixed Total Power P = 1 uW)
- Fig S12: Four Dynamic Quantities Across Five Gate Biases (Authoritative Traces)
- Fig S13: ROM Energy Accounting (ODE-Integrated Reference vs Coarse-Quadrature Sample)
- Fig S14: Fine Forward-Ramp Dynamic Trajectories & Load-Line Throttling
- Fig S15: Spatial Switching Milestone Visualization (Illustrative Continuum Profiles)
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter

# Dynamically locate project root by walking upward until authoritative_model_config.json is found
import os
import sys

_cand = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = None
while _cand and _cand != os.path.dirname(_cand):
    if os.path.exists(os.path.join(_cand, "authoritative_model_config.json")):
        ROOT_DIR = _cand
        break
    _cand = os.path.dirname(_cand)
if ROOT_DIR is None:
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

for _p in [ROOT_DIR, os.path.join(ROOT_DIR, "scripts")]:
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import giv_pts_model as gm

# Output directory
out_dirs = [
    os.path.join(ROOT_DIR, 'figures'),
    os.path.join(ROOT_DIR, 'manuscript_figures'),
    os.path.join(ROOT_DIR, 'manuscript', 'figures'),
    os.path.join(ROOT_DIR, 'supplementary', 'figures')
]
out_dir = out_dirs[0]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

# Formatting settings - Large and Bold for Supplementary Figures
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 16,
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'figure.titleweight': 'bold',
    'axes.linewidth': 2.0,
    'lines.linewidth': 2.8,
    'figure.titlesize': 20,
    'axes.titlesize': 18.0,
    'axes.labelsize': 17.0,
    'xtick.labelsize': 15.0,
    'ytick.labelsize': 15.0,
    'legend.fontsize': 13.5,
    'legend.title_fontsize': 14.5,
    'xtick.major.width': 1.8,
    'ytick.major.width': 1.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'mathtext.fontset': 'dejavusans'
})

def save_fig(fig, name, alias=None):
    for ax in fig.get_axes():
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
    if not fig.get_constrained_layout():
        try:
            fig.tight_layout()
        except Exception:
            pass
    for d in out_dirs:
        png_path = os.path.join(d, f'{name}.png')
        pdf_path = os.path.join(d, f'{name}.pdf')
        fig.savefig(png_path, dpi=300, bbox_inches='tight')
        fig.savefig(pdf_path, bbox_inches='tight')
    print(f"  [SAVED] {name}.png and .pdf")
    if alias:
        for d in out_dirs:
            a_png = os.path.join(d, f'{alias}.png')
            a_pdf = os.path.join(d, f'{alias}.pdf')
            fig.savefig(a_png, dpi=300, bbox_inches='tight')
            fig.savefig(a_pdf, bbox_inches='tight')
        print(f"  [SAVED ALIAS] {alias}.png and .pdf")
    plt.close(fig)


# -------------------------------------------------------------------------
# Fig S1: Quantum Capacitance Partition & Transferred Sheet Density
# -------------------------------------------------------------------------
def figS1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    cfg = gm.get_config()
    vg_vals = np.linspace(0.0, 2.0, 100)
    
    a = gm.E_Q / cfg.C_top
    b = gm.HBAR * gm.V_F * np.sqrt(np.pi) / gm.E_Q
    
    vox_list = []
    vmu_list = []
    n2d_list = []
    nvo2_list = []
    
    for vg in vg_vals:
        if vg <= 1e-9:
            vox_list.append(0.0)
            vmu_list.append(0.0)
            n2d_list.append(0.0)
            nvo2_list.append(0.0)
        else:
            disc = b**2 + 4.0 * a * vg
            sqrt_n = (-b + np.sqrt(disc)) / (2.0 * a)
            n2d = sqrt_n**2
            vox_list.append(a * n2d)
            vmu_list.append(b * sqrt_n)
            n2d_list.append(n2d * 1e-16)
            nvo2_list.append(cfg.eta_CT * n2d * 1e-16)
            
    # Panel A: Quantum Capacitance Partition
    ax1.plot(vg_vals, vox_list, label=r'Dielectric Drop $V_{\rm ox}$', color='#3498db', lw=2.8)
    ax1.plot(vg_vals, vmu_list, label=r'Quantum Drop $V_{\mu}$', color='#e74c3c', lw=2.8)
    ax1.plot(vg_vals, vg_vals, 'k--', label=r'Applied $V_G = V_{\rm ox} + V_{\mu}$', lw=2.0, alpha=0.7)
    ax1.set_xlabel('Applied Gate Voltage $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel('Potential Drop (V)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(0, 2.25)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Transferred Sheet Density & Closure Comparison
    ax2.plot(vg_vals, n2d_list, label=r'Graphene Density $N_{\rm 2D}$ ($V_D = 0$ V)', color='#2c3e50', lw=2.8)
    ax2.plot(vg_vals, nvo2_list, label=r'Transferred $N_{\mathrm{VO_2}}$ ($V_D = 0$ V)', color='#e74c3c', lw=2.8)
    
    # Non-zero drain comparison (V_D = 2.0 V): Spatially averaged vs Midpoint
    nvo2_sp_2v = [gm.calc_N2D(vg, 2.0, cfg, closure_mode='spatially_averaged') * 1e-16 for vg in vg_vals]
    nvo2_mp_2v = [gm.calc_N2D(vg, 2.0, cfg, closure_mode='midpoint') * 1e-16 for vg in vg_vals]
    ax2.plot(vg_vals, nvo2_sp_2v, label=r'Spatially Averaged ($V_D = 2$ V)', color='#27ae60', lw=2.6, linestyle='--')
    ax2.plot(vg_vals, nvo2_mp_2v, label=r'Midpoint Closure ($V_D = 2$ V)', color='#8e44ad', lw=2.6, linestyle=':')
    
    ax2.set_xlabel('Applied Gate Voltage $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Carrier Sheet Density ($10^{16}\ \mathrm{m}^{-2}$)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_xlim(0, 2.0)
    ax2.set_ylim(-0.5, 45.0)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    save_fig(fig, 'FigS1_Electrostatic_Closure')


# -------------------------------------------------------------------------
# Fig S2: Gate-Dependent Equilibrium Phase Curves (Five Gate Biases)
# -------------------------------------------------------------------------
def figS2():
    cfg = gm.get_config()
    fig, ax = plt.subplots(figsize=(9.2, 6.2), dpi=300)
    T_vals = np.linspace(300.0, 360.0, 120)
    vg_list = [0.0, 0.5, 1.0, 1.5, 2.0]
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#d62728']
    
    for vg, col in zip(vg_list, colors):
        n2d_0 = gm.calc_N2D(vg, 0.0, cfg)
        dXg = cfg.beta_X * n2d_0
        fm_list = []
        for T in T_vals:
            A_IMT = cfg.DG0 - cfg.alpha_th * (T - cfg.T0) - cfg.alpha_IMTg * dXg
            A_MIT = cfg.DG0 + cfg.alpha_th * (T - cfg.T0) + cfg.alpha_MITg * dXg
            dG_IMT = 0.5 * (A_IMT + np.sqrt(A_IMT**2 + 2.5e-5))
            dG_MIT = 0.5 * (A_MIT + np.sqrt(A_MIT**2 + 2.5e-5))
            fm = 1.0 / (1.0 + np.exp((dG_IMT - dG_MIT) / (gm.K_B_EV * T)))
            fm_list.append(fm)
        ax.plot(T_vals, fm_list, color=col, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
        
    ax.axhline(1/3.0, color='gray', linestyle=':', lw=1.8, label=r'Percolation ($f_c = 1/3$)')
    ax.set_xlabel('Temperature $T$ (K)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Equilibrium Metallic Fraction $f_{m,\rm eq}$', fontsize=16.5, fontweight='bold')
    ax.set_xlim(300.0, 360.0)
    ax.set_ylim(-0.02, 1.25)
    ax.grid(True, alpha=0.3)
    # Headroom y in [1.00, 1.25] is 100% vacant above saturation fm=1.0, ensuring zero curve overlap
    ax.legend(loc='upper center', ncol=3, framealpha=0.9, fontsize=12.5, borderpad=0.4, columnspacing=0.8)
    save_fig(fig, 'FigS2_Phase_Equilibrium')


# -------------------------------------------------------------------------
# Fig S3: Native Equilibrium Initialization & 3.175 V Half-Pulse Trajectory
# -------------------------------------------------------------------------
def figS3():
    cfg = gm.get_config()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    vg_list = [0.0, 0.5, 1.0, 1.5, 2.0]
    fm_init = []
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#d62728']
    
    for vg, col in zip(vg_list, colors):
        fpath = os.path.join(ROOT_DIR, 'transients', f'Transient_VG_{vg:.1f}.csv')
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            fm_0 = df.iloc[0]['fm_avg']
            fm_init.append(fm_0)
            
            sub = df[df['time_ns'] <= 0.52]
            ax2.plot(sub['time_ns'], sub['fm_avg'], color=col, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
            
    # Panel A: Initial fraction versus gate bias
    ax1.plot(vg_list, fm_init, 'o-', color='#1b4f72', lw=2.8, markersize=9, label='Gate-Prepared $f_m(0)$')
    ax1.axhline(fm_init[0], color='gray', linestyle='--', lw=2.0, label=f'Ungated Baseline ({fm_init[0]:.2e})')
    ax1.set_yscale('log')
    ax1.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Initial Metallic Fraction $f_m(t=0)$', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, which='both')
    ax1.set_ylim(1e-5, 0.15)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    for vg, fm in zip(vg_list, fm_init):
        ax1.annotate(f'{fm:.2e}', (vg, fm), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=12.0, fontweight='bold')
    
    # Panel B: Traces up to rising-edge midpoint at 0.5 ns
    ax2.set_yscale('log')
    ax2.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Metallic Volume Fraction $f_m$', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.axvline(0.5, color='gray', linestyle=':', lw=2.0, label='Pulse Start ($0.50$ ns)')
    
    # Controlled common initialization for VG = 2.0 V (gate engages at pulse arrival 0.50 ns)
    t_sub_ev = np.linspace(0, 0.52e-9, 105)
    sol_comm2 = gm.solve_transient(2.0, gm.pulse_waveform, t_span=(0, 0.52e-9), cfg=cfg, init_mode='controlled_common', t_gate_start=0.5e-9, t_eval=t_sub_ev)
    ax2.plot(sol_comm2.t * 1e9, sol_comm2.y[0], color='#d62728', linestyle='--', lw=2.8, label=r'Common-Start $V_G = 2.0$ V')
    
    ax2.set_xlim(0.0, 0.52)
    ax2.set_ylim(1e-5, 0.25)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend(loc='upper left', ncol=2, fontsize=12.0, framealpha=0.9, borderpad=0.4, columnspacing=0.8)
    
    save_fig(fig, 'FigS3_Equilibrium_Initialization', alias='FigS3_Gate_Return_Test')


# -------------------------------------------------------------------------
# Fig S4: Paired Gate-Coupling and Thermal-Capacitance Sensitivity
# -------------------------------------------------------------------------
def figS4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df_c = pd.read_csv(os.path.join(ROOT_DIR, 'transients/paired_sensitivity_25grid.csv'))
    c_th_factors = sorted(df_c['C_fac'].unique())
    
    # Panel A: Baseline Latency vs Imposed Thermal Capacitance Variation
    lat_0v = [df_c[df_c['C_fac'] == c]['lat0_ps'].iloc[0] for c in c_th_factors]
    pct_c_th = [(c - 1.0) * 100 for c in c_th_factors]
    
    ax1.plot(pct_c_th, lat_0v, 'o-', color='#2c3e50', markersize=9, lw=2.8, label=r'Baseline $t_{\rm lat}(V_G=0\,{\rm V})$')
    ax1.axvline(0, color='gray', linestyle=':', lw=2.0, label=r'Nominal ($C_{\rm th,on} = 7.80\times 10^{-17}$ J/K)')
    ax1.axvspan(-10.0, +10.0, color='#3498db', alpha=0.15, label=r'Imposed $\pm 10\% C_{\rm th}$')
    ax1.set_xlabel(r'Thermal Capacitance Variation $\Delta C_{\rm th}$ (%)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Switching Latency $t_{\rm lat}(0\,{\rm V})$ (ps)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_ylim(37, 49)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Independent sweeps of alpha_IMTg and alpha_MITg
    df_coupl = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P1_B1_B2_Independent_Gate_Couplings.csv'))
    a_imts = sorted(df_coupl['alpha_IMTg_eV'].unique())
    colors = ['#16a085', '#2980b9', '#8e44ad', '#d35400']
    
    for a_val, col in zip(a_imts, colors):
        sub = df_coupl[df_coupl['alpha_IMTg_eV'] == a_val]
        ax2.plot(sub['alpha_MITg_eV'], sub['Gate_Acceleration_Delta_t_ps'], 'o-', color=col, markersize=8, lw=2.6,
                 label=rf'$\alpha_{{\rm IMTg}} = {a_val:.3f}\ \mathrm{{eV}}$')
        
    ax2.axhline(7.526, color='k', linestyle='--', lw=2.0, label=r'Nominal: $\Delta t_{\rm lat} = 7.53$ ps')
    ax2.set_xlabel(r'Reverse Coupling Barrier $\alpha_{\rm MITg}$ (eV)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Gate-Induced Speedup $\Delta t_{\rm lat}$ (ps)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=12.0, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    save_fig(fig, 'FigS4_Gate_Coupling_Sensitivity', alias='FigS4_Paired_Sensitivity')


# -------------------------------------------------------------------------
# Fig S5: Dynamic Threshold Modulation: First fm = 1/3 and fm = 0.50 Crossings
# -------------------------------------------------------------------------
def figS5():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df_p0 = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P0_A1_Gate_Closure_Paired_Comparison.csv'))
    df_sp = df_p0[df_p0['Closure_Mode'] == 'spatially_averaged']
    
    # Panel A: Threshold Voltages
    ax1.plot(df_sp['V_gate_V'], df_sp['V_onset_ramp_V'], 'o-', color='#1f77b4', lw=2.8, markersize=9,
             label=r'First $f_m = 1/3$ crossing (percolation)')
    ax1.plot(df_sp['V_gate_V'], df_sp['V_midpoint_ramp_V'], 's--', color='#d62728', lw=2.8, markersize=9,
             label=r'$f_m = 0.50$ crossing (transition midpoint)')
    ax1.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Threshold Voltage $V_{\rm app,SET}$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_ylim(4.35, 6.25)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Threshold Reduction relative to VG = 0
    v0_perc = df_sp[df_sp['V_gate_V'] == 0.0]['V_onset_ramp_V'].values[0]
    delta_mv = (v0_perc - df_sp['V_onset_ramp_V'].values) * 1000.0
    ax2.plot(df_sp['V_gate_V'], delta_mv, 'o-', color='#2ca02c', lw=2.8, markersize=9)
    ax2.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Threshold Reduction $\Delta V_{\rm app}$ vs $V_G=0$ (mV)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3)
    for vg, dmv in zip(df_sp['V_gate_V'], delta_mv):
        ax2.annotate(f'{dmv:.1f} mV', (vg, dmv), textcoords="offset points", xytext=(0, 12), ha='center', fontsize=12.5, fontweight='bold')
    ax2.set_xlim(-0.15, 2.15)
    ax2.set_ylim(-20, 380)
    
    save_fig(fig, 'FigS5_Threshold_Criteria', alias='FigS5_Cold_Start_Extraction')


# -------------------------------------------------------------------------
# Fig S6: Event Convergence & Time-Step Stability (fs-Scale Invariance)
# -------------------------------------------------------------------------
def figS6():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 6.2), dpi=300)
    df_conv = pd.read_csv(os.path.join(ROOT_DIR, 'transients/switching_latency_convergence.csv'))
    df_events = pd.read_csv(os.path.join(ROOT_DIR, 'transients/switching_latency_events.csv'))
    
    tighter_labels = ['Tighter_Tol', 'Ultra_Tol', 'Finer_Step_10ps', 'Finer_Step_5ps']
    clean_labels = ['Tighter Tol\n($10^{-10}$)', 'Ultra Tol\n($10^{-12}$)', '10 ps Step\n(Internal)', '5 ps Step\n(Internal)']
    
    delta_0v = []
    delta_2v = []
    base_0v = df_conv[(df_conv['tolerance_config'] == 'Production') & (df_conv['V_G_V'] == 0.0)]['latency_ps'].values[0]
    base_2v = df_conv[(df_conv['tolerance_config'] == 'Production') & (df_conv['V_G_V'] == 2.0)]['latency_ps'].values[0]
    
    for tl in tighter_labels:
        l0 = df_conv[(df_conv['tolerance_config'] == tl) & (df_conv['V_G_V'] == 0.0)]['latency_ps'].values[0]
        l2 = df_conv[(df_conv['tolerance_config'] == tl) & (df_conv['V_G_V'] == 2.0)]['latency_ps'].values[0]
        delta_0v.append((l0 - base_0v) * 1e3)
        delta_2v.append((l2 - base_2v) * 1e3)
        
    x = np.arange(len(clean_labels))
    w = 0.35
    ax1.bar(x - w/2, delta_0v, w, label='$V_G = 0.0$ V', color='#1f77b4')
    ax1.bar(x + w/2, delta_2v, w, label='$V_G = 2.0$ V', color='#d62728')
    ax1.set_xticks(x)
    ax1.set_xticklabels(clean_labels, fontsize=13.5, fontweight='bold')
    ax1.set_ylabel('Latency Change from Production (fs)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.0, fontweight='bold', pad=10)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    ax1.set_ylim(-0.38, 0.38)
    for i, (d0, d2) in enumerate(zip(delta_0v, delta_2v)):
        ax1.text(i - w/2, d0 + 0.02 if d0>=0 else d0 - 0.06, f'{d0:+.2f}', ha='center', fontsize=11.5, fontweight='bold')
        ax1.text(i + w/2, d2 + 0.02 if d2>=0 else d2 - 0.06, f'{d2:+.2f}', ha='center', fontsize=11.5, fontweight='bold')
        
    # Panel B: Continuous event detection vs discrete sample quantization
    df_lat = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P0_A1_Gate_Closure_Paired_Comparison.csv'))
    df_sp = df_lat[df_lat['Closure_Mode'] == 'spatially_averaged']
    
    ax2.plot(df_sp['V_gate_V'], df_sp['Latency_ps'], 'ro-', lw=2.8, markersize=9, label='Continuous Event Detection ($f_m = 1/3$)')
    ax2.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel('Switching Latency (ps)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.0, fontweight='bold', pad=10)
    ax2.set_xlim(-0.15, 2.15)
    ax2.set_ylim(30, 50)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    for vg, lat in zip(df_sp['V_gate_V'], df_sp['Latency_ps']):
        ax2.annotate(f'{lat:.2f} ps', (vg, lat), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=12.5, fontweight='bold')
    
    save_fig(fig, 'FigS6_Event_Convergence', alias='FigS6_Mesh_Convergence')


# -------------------------------------------------------------------------
# Fig S7: Ramp Sampling Limitations & Discrete Binning vs. Continuous Thresholds
# -------------------------------------------------------------------------
def figS7():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df_fine = pd.read_csv(os.path.join(ROOT_DIR, 'hysteresis/fine_ramp_threshold_resolution.csv'))
    df_cont = pd.read_csv(os.path.join(ROOT_DIR, 'hysteresis/continuous_threshold_modulation.csv'))
    df_perc = df_cont[df_cont['Criterion'].str.startswith('Percolation')]
    
    # Panel A: Fine-output phase fraction trajectories
    colors = {0.0: '#1f77b4', 1.0: '#2ca02c', 2.0: '#d62728'}
    for vg, col in colors.items():
        sub = df_fine[df_fine['V_G_V'] == vg]
        sub = sub[(sub['time_ns'] >= 28.0) & (sub['time_ns'] <= 31.5)]
        ax1.plot(sub['time_ns'], sub['fm_avg'], color=col, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
    ax1.axhline(1/3.0, color='k', linestyle='--', lw=2.0, label=r'First $f_m = 1/3$ (percolation)')
    ax1.axhline(0.50, color='gray', linestyle=':', lw=2.0, label=r'$f_m = 0.50$ (midpoint)')
    ax1.set_xlabel('Ramp Time (ns)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Metallic Volume Fraction $f_m$', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_xlim(28.0, 31.5)
    ax1.set_ylim(-0.02, 0.85)
    ax1.grid(True, alpha=0.3)
    # Move legend to upper left: curves are at 0 for t < 29.3 ns (ZERO curve overlap!)
    ax1.legend(loc='upper left', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Discrete Binning Limitations
    ax2.plot(df_perc['V_G_V'], df_perc['Continuous_V_app_SET_V'], 'o-', color='#1f77b4', lw=2.8, markersize=9, label='Continuous Crossing ($4.878 \\to 4.579$ V)')
    ax2.step(df_perc['V_G_V'], df_perc['Sampled_0p5ns_V_app_SET_V'], 's--', color='#e67e22', where='mid', lw=2.4, markersize=9, label='0.5 ns Sampled (80 mV bins)')
    ax2.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Threshold Voltage $V_{\rm app,SET}$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_ylim(4.35, 5.05)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    save_fig(fig, 'FigS7_Ramp_Sampling', alias='FigS7_Voltage_Step_Convergence')


# -------------------------------------------------------------------------
# Fig S8: Prescribed-Heating COMSOL Exports
# -------------------------------------------------------------------------
def figS8():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df0 = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_OFF_Ablated.csv'))
    df1 = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_ON_Baseline.csv'))
    
    sub0 = df0[df0['t_ps'] <= 2000.0]
    sub1 = df1[df1['t_ps'] <= 2000.0]
    t0_ns = sub0['t_ps'] / 1000.0
    t1_ns = sub1['t_ps'] / 1000.0
    
    # Panel A: Volume-average temperature rise
    ax1.plot(t0_ns, sub0['Delta_T_avg_K'], 'r-', lw=2.8,
             label=r'Graphene OFF: $\tau_{63.2\%} = 429.1\ \mathrm{ps}\ (R_{\rm th,avg} = 1.72\times 10^6\ \mathrm{K/W})$')
    ax1.plot(t1_ns, sub1['Delta_T_avg_K'], 'g-', lw=2.8,
             label=r'Graphene ON: $\tau_{63.2\%} = 41.9\ \mathrm{ps}\ (R_{\rm th,avg} = 5.37\times 10^5\ \mathrm{K/W})$')
    ax1.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Volume-Average Rise $\Delta T_{\rm avg}$ (K)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(-0.05, 2.15)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Maximum temperature rise
    ax2.plot(t0_ns, sub0['Delta_T_max_K'], 'r-', lw=2.8, label=r'Graphene OFF ($T_{\rm max}$ rise, $R_{\rm th,max} = 2.42\times 10^6\ \mathrm{K/W}$)')
    ax2.plot(t1_ns, sub1['Delta_T_max_K'], 'g-', lw=2.8, label=r'Graphene ON ($T_{\rm max}$ rise, $R_{\rm th,max} = 7.61\times 10^5\ \mathrm{K/W}$)')
    ax2.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Maximum Temperature Rise $\Delta T_{\rm max}$ (K)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_xlim(0, 2.0)
    ax2.set_ylim(-0.05, 2.95)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    save_fig(fig, 'FigS8_Thermal_Calibration', alias='FigS8_Graphene_Sweep')


# -------------------------------------------------------------------------
# Fig S9: Quantitative TBR Penalties from 3D FEA (Table S4 Alignment)
# -------------------------------------------------------------------------
def figS9():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df_base = pd.read_csv(os.path.join(ROOT_DIR, 'robustness/TBR_50k_FEA_Waveform_Baseline_0.0e+00.csv'), comment='%')
    top_tbrs = ['1.0e-09', '5.0e-09', '1.0e-08', '3.0e-08']
    tbr_ticks = [0, 1, 2, 3, 4]
    tick_labels = ['0 (Base)', '1n', '5n', '10n', '30n']
    
    base_peak = df_base['T_max_K'].max()
    top_peaks = [base_peak]
    bot_peaks = [base_peak]
    
    for tbr_str in top_tbrs:
        df_t = pd.read_csv(os.path.join(ROOT_DIR, 'robustness', f'TBR_50k_FEA_Waveform_Top_{tbr_str}.csv'), comment='%')
        top_peaks.append(df_t['T_max_K'].max())
        df_b = pd.read_csv(os.path.join(ROOT_DIR, 'robustness', f'TBR_50k_FEA_Waveform_Bottom_{tbr_str}.csv'), comment='%')
        bot_peaks.append(df_b['T_max_K'].max())
        
    w = 0.35
    ax1.bar([x - w/2 for x in tbr_ticks], top_peaks, width=w, color='#3f72af', label='Top Interface')
    ax1.bar([x + w/2 for x in tbr_ticks], bot_peaks, width=w, color='#4caf50', label='Bottom Interface')
    ax1.axhline(425, color='r', linestyle=':', lw=2.0, label=r'Tested Parameter Bound ($T \leq 425$ K, Not Device Limit)')
    ax1.set_xticks(tbr_ticks)
    ax1.set_xticklabels(tick_labels, fontsize=14.5, fontweight='bold')
    ax1.set_xlabel(r'Thermal Boundary Resistance $R_{\rm TBR}$ (m$^2$K/W)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Peak Temperature $T_{\rm max}$ (K)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_ylim(345, 470)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    top_penalties = [p - base_peak for p in top_peaks]
    bot_penalties = [p - base_peak for p in bot_peaks]
    ax2.plot(tbr_ticks, top_penalties, 'o-', color='#3f72af', lw=2.8, markersize=9, label='Top Interface')
    ax2.plot(tbr_ticks, bot_penalties, 's-', color='#4caf50', lw=2.8, markersize=9, label='Bottom Interface')
    ax2.set_xticks(tbr_ticks)
    ax2.set_xticklabels(tick_labels, fontsize=14.5, fontweight='bold')
    ax2.set_xlabel(r'Thermal Boundary Resistance $R_{\rm TBR}$ (m$^2$K/W)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Peak Temperature Penalty $\Delta T_{\rm max}$ (K)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_ylim(-2, 52)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    for x_pos, dt_top, dt_bot in zip(tbr_ticks[1:], top_penalties[1:], bot_penalties[1:]):
        if x_pos == 1:
            ax2.annotate(f'+{dt_top:.1f} K', (x_pos, dt_top), textcoords="offset points", xytext=(-5, 10), fontsize=12.0, color='#3f72af', fontweight='bold')
            ax2.annotate(f'+{dt_bot:.1f} K', (x_pos, dt_bot), textcoords="offset points", xytext=(5, -18), fontsize=12.0, color='#4caf50', fontweight='bold')
        elif x_pos == 2:
            ax2.annotate(f'+{dt_top:.1f} K', (x_pos, dt_top), textcoords="offset points", xytext=(-18, 10), fontsize=12.0, color='#3f72af', fontweight='bold')
            ax2.annotate(f'+{dt_bot:.1f} K', (x_pos, dt_bot), textcoords="offset points", xytext=(12, -18), fontsize=12.0, color='#4caf50', fontweight='bold')
        elif x_pos == 3:
            ax2.annotate(f'+{dt_top:.1f} K', (x_pos, dt_top), textcoords="offset points", xytext=(5, -18), fontsize=12.0, color='#3f72af', fontweight='bold')
            ax2.annotate(f'+{dt_bot:.1f} K', (x_pos, dt_bot), textcoords="offset points", xytext=(-8, 10), fontsize=12.0, color='#4caf50', fontweight='bold')
        else:
            ax2.annotate(f'+{dt_top:.1f} K', (x_pos, dt_top), textcoords="offset points", xytext=(5, -18), fontsize=12.0, color='#3f72af', fontweight='bold')
            ax2.annotate(f'+{dt_bot:.1f} K', (x_pos, dt_bot), textcoords="offset points", xytext=(-8, 10), fontsize=12.0, color='#4caf50', fontweight='bold')
        
    save_fig(fig, 'FigS9_Interface_TBR')


# -------------------------------------------------------------------------
# Fig S10: Principal-ROM Circuit Quantities (Load Line)
# -------------------------------------------------------------------------
def figS10():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df0 = pd.read_csv(os.path.join(ROOT_DIR, 'transients/Transient_VG_0.0.csv'))
    df2 = pd.read_csv(os.path.join(ROOT_DIR, 'transients/Transient_VG_2.0.csv'))
    
    ax1.plot(df0['time_ns'], df0['V_app (V)'], 'k-', lw=2.8, label='Applied $V_{\\rm app}$ ($6.35$ V Pulse)')
    ax1.plot(df0['time_ns'], df0['V_D (V)'], 'b-', lw=2.8, label='Device $V_D$ ($V_G = 0.0$ V)')
    ax1.plot(df2['time_ns'], df2['V_D (V)'], 'r--', lw=2.8, label='Device $V_D$ ($V_G = 2.0$ V)')
    ax1.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel('Voltage (V)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_xlim(0, 4.0)
    ax1.set_ylim(-0.5, 7.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    ax2.plot(df0['V_D (V)'], df0['I_D (uA)'], 'bo-', lw=2.2, markersize=6, label='$V_G = 0.0$ V Samples')
    ax2.plot(df2['V_D (V)'], df2['I_D (uA)'], 'r^--', lw=2.2, markersize=6, label='$V_G = 2.0$ V Samples')
    v_load = np.linspace(0, 6.35, 100)
    i_load_uA = (6.35 - v_load) / 50.0 * 1e3
    ax2.plot(v_load, i_load_uA, 'k:', lw=2.0, label=r'Load Line ($V_D + R_L I_D = 6.35$ V)')
    ax2.set_xlabel('Device Voltage $V_D$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Drain Current $I_D$ ($\mu$A)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_xlim(-0.2, 6.0)
    ax2.set_ylim(-5, 140)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    save_fig(fig, 'FigS10_Load_Line', alias='FigS10_HfO2_Sensitivity')


# -------------------------------------------------------------------------
# Fig S11: Thickness Maps (Calls Authoritative Generator)
# -------------------------------------------------------------------------
def figS11():
    import plot_structural_thermal_figures as pstf
    pstf.generate_figS11()


# -------------------------------------------------------------------------
# Fig S12: Four Quantities Across Five Gate Biases (Authoritative Traces)
# -------------------------------------------------------------------------
def figS12():
    fig, axs = plt.subplots(2, 2, figsize=(16.5, 12.5), dpi=300)
    vg_list = [0.0, 0.5, 1.0, 1.5, 2.0]
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#d62728']
    styles = ['-', '--', '-.', ':', '-']
    
    dfs = {}
    for vg in vg_list:
        fpath = os.path.join(ROOT_DIR, 'transients', f'Transient_VG_{vg:.1f}.csv')
        if os.path.exists(fpath):
            dfs[vg] = pd.read_csv(fpath)
            
    # Panel (a): Device Voltage
    ax = axs[0, 0]
    for vg, col, ls in zip(vg_list, colors, styles):
        if vg in dfs:
            df = dfs[vg]
            ax.plot(df['time_ns'], df['V_D (V)'], color=col, linestyle=ls, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
    if 0.0 in dfs:
        ax.plot(dfs[0.0]['time_ns'], dfs[0.0]['V_app (V)'], 'k:', lw=2.0, alpha=0.7, label=r'Applied $V_{\rm app}$ (6.35 V)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel('Device Voltage $V_D$ (V)', fontsize=16.5, fontweight='bold')
    ax.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax.set_xlim(0, 4.0)
    ax.set_ylim(-0.5, 7.5)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    # Panel (b): Drain Current (Move to upper right where ID = 0 after 2.5 ns)
    ax = axs[0, 1]
    for vg, col, ls in zip(vg_list, colors, styles):
        if vg in dfs:
            df = dfs[vg]
            peak_id = df['I_D (uA)'].max()
            ax.plot(df['time_ns'], df['I_D (uA)'], color=col, linestyle=ls, lw=2.8, label=f'$V_G = {vg:.1f}$ V ({peak_id:.1f} ' + r'$\mu$A)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Drain Current $I_D$ ($\mu$A)', fontsize=16.5, fontweight='bold')
    ax.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax.set_xlim(0, 4.0)
    ax.set_ylim(-5, 145)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12.0, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    # Panel (c): Volume-Average Temperature
    ax = axs[1, 0]
    for vg, col, ls in zip(vg_list, colors, styles):
        if vg in dfs:
            df = dfs[vg]
            ax.plot(df['time_ns'], df['T_avg (K)'], color=col, linestyle=ls, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Volume-Average Temp $T_{\rm avg}$ (K)', fontsize=16.5, fontweight='bold')
    ax.set_title('(c)', fontsize=17.5, fontweight='bold', pad=10)
    ax.set_xlim(0, 4.0)
    ax.set_ylim(296, 356)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    # Panel (d): Metallic Volume Fraction (Move to upper right where fm = 0 after 2.7 ns)
    ax = axs[1, 1]
    for vg, col, ls in zip(vg_list, colors, styles):
        if vg in dfs:
            df = dfs[vg]
            ax.plot(df['time_ns'], df['fm_avg'], color=col, linestyle=ls, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
    ax.axhline(1/3.0, color='gray', linestyle=':', lw=2.0, label=r'Percolation ($f_m = 1/3$)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Metallic Volume Fraction $f_m$', fontsize=16.5, fontweight='bold')
    ax.set_title('(d)', fontsize=17.5, fontweight='bold', pad=10)
    ax.set_xlim(0, 4.0)
    ax.set_ylim(-0.05, 1.15)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.25)
    
    save_fig(fig, 'FigS12_Transient_Traces', alias='FigS11_Transient_Traces')


# -------------------------------------------------------------------------
# Fig S13: ROM Energy Accounting (Authoritative Reference vs Coarse Quadrature)
# -------------------------------------------------------------------------
def figS13():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    
    # Authoritative latent heat dataset
    df_lat = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P0_B4_Latent_Heat_Energy_Accounting.csv'))
    df_sub = df_lat[df_lat['Include_Latent_Heat'] == True]
    
    # Coarse quadrature comparison dataset
    df_quad = pd.read_csv(os.path.join(ROOT_DIR, 'transients/transient_energy_metrics.csv'))
    
    x = np.arange(len(df_sub['V_gate_V']))
    w = 0.35
    
    # Panel A: Circuit energy contributions across 0--4 ns window
    ax1.bar(x - w/2, df_sub['E_dev_total_pJ'] * 1e3, w, label=r'Device $E_{\rm dev}$', color='#e74c3c')
    ax1.bar(x + w/2, df_sub['E_res_total_pJ'] * 1e3, w, label=r'Load $E_{\rm res}$ ($50\ \mathrm{k}\Omega$)', color='#3498db')
    ax1.plot(x, df_sub['E_src_total_pJ'] * 1e3, 'go-', lw=2.8, markersize=9, label=r'Total Source $E_{\rm src}$')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{v:.1f} V' for v in df_sub['V_gate_V']], fontsize=14.5, fontweight='bold')
    ax1.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel('Total Pulse Energy (fJ)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_ylim(0, 2100)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Device switching energy to first fm = 1/3 event
    ax2.bar(x - w/2, df_quad['E_dev_switch_continuous_fJ'], width=w, color='#e67e22', edgecolor='#b9651a', lw=1.8,
            label='ODE Reference ($E_{\\rm dev,switch}$ continuous)')
    ax2.bar(x + w/2, df_quad['E_dev_switch_fJ'], width=w, color='#95a5a6', edgecolor='#7f8c8d', lw=1.8,
            label='Discrete Estimate (Table S7 / Output Grid)')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{v:.1f} V' for v in df_sub['V_gate_V']], fontsize=14.5, fontweight='bold')
    ax2.set_xlabel('Gate Bias $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel('Switching Energy $E_{\\rm dev,switch}$ (fJ)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_ylim(0, 8.5)
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.legend(loc='upper right', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    for i, val in enumerate(df_quad['E_dev_switch_continuous_fJ']):
        ax2.text(i - w/2, val + 0.16, f'{val:.2f}', ha='center', fontsize=11.5, fontweight='bold', color='#b9651a')
    for i, val in enumerate(df_quad['E_dev_switch_fJ']):
        ax2.text(i + w/2, val + 0.16, f'{val:.2f}', ha='center', fontsize=11.5, fontweight='bold', color='#444444')
        
    save_fig(fig, 'FigS12_Energy_Accounting', alias='FigS13_Energy_Accounting')


# -------------------------------------------------------------------------
# Fig S14: Fine Forward-Ramp Dynamic Trajectories
# -------------------------------------------------------------------------
def figS14():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0), dpi=300)
    df = pd.read_csv(os.path.join(ROOT_DIR, 'hysteresis/fine_ramp_threshold_resolution.csv'))
    
    colors = {0.0: '#1f77b4', 1.0: '#2ca02c', 2.0: '#d62728'}
    styles = {0.0: '-', 1.0: '--', 2.0: '-.'}
    
    for vg, col in colors.items():
        sub = df[df['V_G_V'] == vg]
        ax1.plot(sub['V_app_V'], sub['I_D_uA'], color=col, linestyle=styles[vg], lw=2.8, label=f'$V_G = {vg:.1f}$ V')
        ax2.plot(sub['V_app_V'], sub['T_avg_K'], color=col, linestyle=styles[vg], lw=2.8, label=f'$V_G = {vg:.1f}$ V')
        
    ax1.set_xlabel('Applied Source Voltage $V_{\\rm app}$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Drain Current $I_D$ ($\mu$A)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold', pad=10)
    ax1.set_xlim(4.4, 5.2)
    ax1.set_ylim(-5, 140)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    ax2.set_xlabel('Applied Source Voltage $V_{\\rm app}$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Average Temperature $T_{\rm avg}$ (K)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold', pad=10)
    ax2.set_xlim(4.4, 5.2)
    ax2.set_ylim(310, 350)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)

    save_fig(fig, 'FigS14_Hysteresis_Curves', alias='FigS13_Forward_Ramp')


# -------------------------------------------------------------------------
# Fig S15: Spatial Switching Sequence (Calls Authoritative Generator)
# -------------------------------------------------------------------------
def figS15():
    import plot_structural_thermal_figures as pstf
    pstf.generate_figS15()


if __name__ == '__main__':
    print("=" * 70)
    print("REGENERATING ALL SUPPLEMENTARY INFORMATION FIGURES")
    print("=" * 70)
    figS1()
    figS2()
    figS3()
    figS4()
    figS5()
    figS6()
    figS7()
    figS8()
    figS9()
    figS10()
    figS11()
    figS12()
    figS13()
    figS14()
    figS15()
    print("=" * 70)
    print("All SI Figures generated successfully in 'manuscript_figures' folder.")
    print("=" * 70)
