"""generate_main_figures.py

Generates all primary manuscript figures strictly synchronized with the authoritative,
reconciled device-physics model and FEA calibration:
- Fig 1: Device Architecture & Operating Principles (P0 Contact Topology & Isolation)
- Fig 2: In-Plane Continuum Thermal Maps & Graphene Spreading (New Main Fig 2)
- Fig 3: Cross-Sectional Heat Flux Vectors & Dissipation Pathways (New Main Fig 3)
- Fig 4: Prescribed-Heating Thermal Traces & Post-Pulse Multi-Scale Recovery (New Main Fig 4)
- Fig 5: Constitutive Gate Electrostatics of the ROM & Phase Equilibria (New Main Fig 5)
- Fig 6: Protocol-Dependent Phase-Conversion Thresholds (New Main Fig 6)
- Fig 7: Principal ROM Pulse Dynamics, Phase Quenching & Converged Circuit Energy (New Main Fig 7)

Also generates backward-compatible aliases so all existing references remain valid.
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

# Publication styling settings - Large and Bold for Manuscript Readability
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


# =========================================================================
# Fig 1: Device Architecture & Operating Principles
# =========================================================================
def fig1_architecture():
    print("[1/7] Generating Fig 1: Device Architecture & Operating Principles...")
    fig = plt.figure(figsize=(16.8, 6.2), dpi=300)
    gs = GridSpec(1, 3, width_ratios=[1.35, 1.0, 1.0])
    
    # Panel A: Dimensioned Cross-Section with Electrical Isolation & Lateral Extent
    ax1 = fig.add_subplot(gs[0])
    ax1.axis('off')
    ax1.set_title('(a)', loc='left', fontweight='bold', fontsize=17.5)
    
    # Substrate SiO2 (300 nm, drawn bottom)
    rect_sub = patches.Rectangle((0.10, 0.05), 0.80, 0.15, facecolor='#bdc3c7', edgecolor='#7f8c8d', lw=1.8)
    ax1.add_patch(rect_sub)
    ax1.text(0.50, 0.125, r'$\mathrm{\mathbf{SiO_2\ Substrate\ (300\ nm,\ T_0 = 300\ K)}}$', ha='center', va='center', color='black', fontsize=13.5, fontweight='bold')
    
    # Source metal contact (x = 0-10 nm equivalent)
    rect_src = patches.Rectangle((0.01, 0.20), 0.12, 0.38, facecolor='#f1c40f', edgecolor='#b7950b', lw=1.8)
    ax1.add_patch(rect_src)
    ax1.text(0.07, 0.39, 'Source\n(GND, 300 K)', ha='center', va='center', fontweight='bold', fontsize=13.0)
    
    # Drain metal contact (x = 40-50 nm equivalent)
    rect_drn = patches.Rectangle((0.87, 0.20), 0.12, 0.38, facecolor='#f1c40f', edgecolor='#b7950b', lw=1.8)
    ax1.add_patch(rect_drn)
    ax1.text(0.93, 0.39, 'Drain\n($V_D$, 300 K)', ha='center', va='center', fontweight='bold', fontsize=13.0)
    
    # VO2 Channel (50 nm length, 5 nm thickness)
    rect_vo2 = patches.Rectangle((0.14, 0.20), 0.72, 0.18, facecolor='#e74c3c', edgecolor='#922b21', lw=1.8)
    ax1.add_patch(rect_vo2)
    ax1.text(0.50, 0.29, r'$\mathrm{\mathbf{VO_2\ Channel\ (50\times 50\times 5\ nm^3)}}$', ha='center', va='center', color='white', fontweight='bold', fontsize=14.5)
    
    # Dielectric Standoffs (1 nm at each side)
    rect_std1 = patches.Rectangle((0.14, 0.38), 0.03, 0.06, facecolor='#85c1e9', edgecolor='#2980b9', lw=1.4)
    rect_std2 = patches.Rectangle((0.83, 0.38), 0.03, 0.06, facecolor='#85c1e9', edgecolor='#2980b9', lw=1.4)
    ax1.add_patch(rect_std1)
    ax1.add_patch(rect_std2)
    
    # Monolayer Graphene Spreader (48 nm extent, centered, isolated from S/D)
    rect_gr = patches.Rectangle((0.17, 0.38), 0.66, 0.06, facecolor='#2c3e50', edgecolor='#1a252f', lw=1.6)
    ax1.add_patch(rect_gr)
    ax1.text(0.50, 0.41, 'Isolated Monolayer Graphene (48 nm)', ha='center', va='center', color='white', fontweight='bold', fontsize=12.0)
    
    # HfO2 Gate Dielectric (5 nm, kappa = 25)
    rect_ox = patches.Rectangle((0.14, 0.44), 0.72, 0.16, facecolor='#3498db', edgecolor='#1f618d', lw=1.8)
    ax1.add_patch(rect_ox)
    ax1.text(0.50, 0.52, r'$\mathrm{\mathbf{HfO_2\ Dielectric\ (5\ nm,\ \epsilon_r=25)}}$', ha='center', va='center', color='white', fontweight='bold', fontsize=14.0)
    
    # Top Gate Metal Electrode
    rect_gate = patches.Rectangle((0.14, 0.60), 0.72, 0.22, facecolor='#7f8c8d', edgecolor='#515a5a', lw=1.8)
    ax1.add_patch(rect_gate)
    ax1.text(0.50, 0.71, r'$\mathrm{\mathbf{Top\ Gate\ Electrode\ (V_G)}}$', ha='center', va='center', color='white', fontweight='bold', fontsize=14.5)
    
    # Annotation for dielectric standoff placed neatly above Source/Drain outside the gate
    ax1.annotate('1 nm Standoff\n(No DC Shunt)', xy=(0.155, 0.44), xytext=(0.07, 0.88),
                 ha='center', va='center',
                 arrowprops=dict(arrowstyle="->", color='#c0392b', lw=1.8),
                 fontsize=12.5, fontweight='bold', color='#c0392b')
    ax1.annotate('1 nm Standoff\n(No DC Shunt)', xy=(0.845, 0.44), xytext=(0.93, 0.88),
                 ha='center', va='center',
                 arrowprops=dict(arrowstyle="->", color='#c0392b', lw=1.8),
                 fontsize=12.5, fontweight='bold', color='#c0392b')
    ax1.set_xlim(-0.02, 1.02)
    ax1.set_ylim(-0.02, 1.02)

    # Panel B: Electrostatic Pathway with Independent Forward/Reverse Couplings (Assumed Schematic)
    ax2 = fig.add_subplot(gs[1])
    ax2.axis('off')
    ax2.set_title('(b)', loc='left', fontweight='bold', fontsize=17.5)
    nodes = ['V$_G$', 'N$_{2D}$', 'N$_{\mathrm{VO_2}}$', '$x_g$']
    colors = ['#bdc3c7', '#3498db', '#e74c3c', '#9b59b6']
    for i, (node, color) in enumerate(zip(nodes, colors)):
        circle = patches.Circle((0.24, 0.82 - i*0.22), 0.08, facecolor=color, edgecolor='k', lw=1.8)
        ax2.add_patch(circle)
        ax2.text(0.24, 0.82 - i*0.22, node, ha='center', va='center', fontweight='bold', color='w', fontsize=14.0)
        if i < 3:
            ax2.arrow(0.24, 0.74 - i*0.22, 0, -0.05, head_width=0.035, head_length=0.03, fc='k', ec='k', lw=1.8)
    ax2.text(0.38, 0.71, 'Quantum Capacitance\n' + r'$C_{\rm top} = 44.3\ \mathrm{mF/m^2}$', va='center', fontsize=13.0, fontweight='bold')
    ax2.text(0.38, 0.49, 'Assumed Charge Transfer\n' + r'$\eta_{\rm CT} = 0.50$ (Phenomenological)', va='center', fontsize=13.0, fontweight='bold')
    ax2.text(0.38, 0.27, 'Dimensionless Coordinate\n' + r'$x_g = \beta_X N_{\rm VO_2}$', va='center', fontsize=13.0, fontweight='bold')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0.05, 0.98)

    # Panel C: Dual-Mode Thermal Heat Removal Pathway (Contacts + Substrate)
    ax3 = fig.add_subplot(gs[2])
    ax3.axis('off')
    ax3.set_title('(c)', loc='left', fontweight='bold', fontsize=17.5)
    ax3.add_patch(patches.Rectangle((0.15, 0.42), 0.70, 0.18, facecolor='#e74c3c', alpha=0.35, edgecolor='#c0392b', lw=1.8))
    ax3.text(0.50, 0.51, r'$\mathrm{\mathbf{VO_2\ Channel\ Heat\ Source}}$' + '\n' + r'$(Q_0 = 8.0\times 10^{16}\ \mathrm{W/m^3})$',
             ha='center', va='center', color='#922b21', fontweight='bold', fontsize=13.0)
    
    # Lateral heat removal to contact pads
    ax3.arrow(0.42, 0.62, 0.32, 0, head_width=0.03, head_length=0.04, fc='#2c3e50', ec='#2c3e50', lw=2.4)
    ax3.arrow(0.58, 0.62, -0.32, 0, head_width=0.03, head_length=0.04, fc='#2c3e50', ec='#2c3e50', lw=2.4)
    ax3.text(0.50, 0.74, 'Heat Removal to Contact Pads\n' + r'via Graphene ($k = 201\ \mathrm{W/(m\cdot K)},\ \tau_1 = 36.0\ \mathrm{ps}$)',
             ha='center', va='bottom', color='#2c3e50', fontsize=12.5, fontweight='bold')
    
    # Vertical heat removal to substrate
    ax3.arrow(0.50, 0.42, 0, -0.16, head_width=0.04, head_length=0.03, fc='#c0392b', ec='#c0392b', lw=2.4)
    ax3.text(0.50, 0.16, 'Heat Removal to Substrate\n' + r'via $\mathrm{SiO_2}$ ($k = 1.4\ \mathrm{W/(m\cdot K)},\ \tau_2 = 78.6\ \mathrm{ps}$)',
             ha='center', va='top', color='#c0392b', fontsize=12.5, fontweight='bold')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    save_fig(fig, 'Fig1_Architecture')


# =========================================================================
# Fig 2: In-Plane Continuum Thermal Maps & Graphene Spreading (New Main Fig 2)
# =========================================================================
def fig2_thermal_maps():
    print("[2/7] Generating Fig 2: In-Plane Continuum Thermal Maps from Authentic COMSOL 3D FEA...")
    fig, axs = plt.subplots(1, 2, figsize=(14.5, 6.0), constrained_layout=True, dpi=300)
    
    # Load genuine COMSOL 3D FEA field export
    df_sp = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Spatial_Fields.csv'), comment='%')
    df_inplane = df_sp[df_sp['CutPlane'] == 'InPlane_z_2.5nm']
    X = df_inplane['x_nm'].values.reshape(51, 51)
    Y = df_inplane['y_nm'].values.reshape(51, 51)
    T_off = df_inplane['T_K_GrOFF'].values.reshape(51, 51)
    T_on = df_inplane['T_K_GrON'].values.reshape(51, 51)
    
    levels = np.linspace(300.0, 302.50, 50)
    
    # Panel (a): Graphene OFF Control
    ax = axs[0]
    cf0 = ax.contourf(X, Y, T_off, levels=levels, cmap='inferno')
    ax.contour(X, Y, T_off, levels=5, colors='k', alpha=0.25, linewidths=0.9)
    ax.set_title('(a)', fontsize=17.5, fontweight='bold')
    ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=16.5, fontweight='bold')
    ax.set_aspect('equal')
    ax.axvline(-25, color='#3498db', lw=3.2)
    ax.axvline(25, color='#e74c3c', lw=3.2)
    
    # Panel (b): Graphene ON Baseline
    ax = axs[1]
    cf1 = ax.contourf(X, Y, T_on, levels=levels, cmap='inferno')
    ax.contour(X, Y, T_on, levels=5, colors='k', alpha=0.25, linewidths=0.9)
    ax.set_title('(b)', fontsize=17.5, fontweight='bold')
    ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=16.5, fontweight='bold')
    ax.set_aspect('equal')
    ax.axvline(-25, color='#3498db', lw=3.2)
    ax.axvline(25, color='#e74c3c', lw=3.2)
    
    cbar = fig.colorbar(cf1, ax=axs, orientation='vertical', fraction=0.025, pad=0.03)
    cbar.set_label('Temperature $T$ (K)', fontsize=16.5, fontweight='bold')
    cbar.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar.ax.tick_params(labelsize=14.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')
    
    save_fig(fig, 'Fig2_Thermal_Spreading_Maps', alias='FigS21_Thermal_Spreading_Maps')


# =========================================================================
# Fig 3: Cross-Sectional Heat Flux Vectors (New Main Fig 3)
# =========================================================================
def fig3_thermal_flux():
    print("[3/7] Generating Fig 3: Cross-Sectional Heat Flux Vectors from Authentic COMSOL 3D FEA...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.0, 7.0), constrained_layout=True, dpi=300)
    
    # Load genuine COMSOL 3D FEA cross-section export
    df_sp = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Spatial_Fields.csv'), comment='%')
    df_cross = df_sp[df_sp['CutPlane'] == 'CrossSection_y_0nm']
    X = df_cross['x_nm'].values.reshape(41, 51)
    Z = df_cross['z_nm'].values.reshape(41, 51)
    T_off = df_cross['T_K_GrOFF'].values.reshape(41, 51)
    T_on = df_cross['T_K_GrON'].values.reshape(41, 51)
    qx_off = df_cross['qx_W_m2_GrOFF'].values.reshape(41, 51)
    qz_off = df_cross['qz_W_m2_GrOFF'].values.reshape(41, 51)
    qx_on = df_cross['qx_W_m2_GrON'].values.reshape(41, 51)
    qz_on = df_cross['qz_W_m2_GrON'].values.reshape(41, 51)
    
    levels = np.linspace(300.0, 302.5, 50)
    
    titles = [
        '(a)',
        '(b)'
    ]
    
    for ax, T_data, qx, qz, title, tag in zip([ax1, ax2], [T_off, T_on], [qx_off, qx_on], [qz_off, qz_on], titles, ['OFF', 'ON']):
        cf = ax.contourf(X, Z, T_data, levels=levels, cmap='inferno')
        ax.axhline(0, color='white', linestyle='--', lw=1.4)
        ax.axhline(5, color='cyan' if tag == 'ON' else 'white', linestyle='-' if tag == 'ON' else '--', lw=2.2 if tag == 'ON' else 1.4)
        
        # Heat flux streamlines (direction only) from genuine COMSOL vector field
        ax.streamplot(X, Z, qx, qz, color='cyan', density=0.8, linewidth=1.4, arrowsize=1.3)
        
        ax.text(-23, -5.5, r'$\mathrm{\mathbf{SiO_2\ Substrate}}$', color='white', fontsize=13.5, fontweight='bold')
        ax.text(-23, 2.5, r'$\mathrm{\mathbf{VO_2\ Channel\ (5\ nm)}}$', color='white', fontsize=13.5, fontweight='bold')
        ax.text(-23, 7.5, r'$\mathrm{\mathbf{HfO_2\ Dielectric}}$', color='white', fontsize=13.5, fontweight='bold')
            
        ax.set_title(title, fontsize=17.5, fontweight='bold', pad=12)
        ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=16.5, fontweight='bold')
        ax.set_ylabel('Stack Coordinate $z$ (nm)', fontsize=16.5, fontweight='bold')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-10, 10)
        ax.axvline(-25, color='#3498db', lw=3.5)
        ax.axvline(25, color='#e74c3c', lw=3.5)
        
    cbar = fig.colorbar(cf, ax=[ax1, ax2], orientation='vertical', fraction=0.02, pad=0.03)
    cbar.set_label('Temperature $T$ (K)', fontsize=16.5, fontweight='bold')
    cbar.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar.ax.tick_params(labelsize=14.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')

    save_fig(fig, 'Fig3_Thermal_Flux_Vectors', alias='FigS22_CrossSection_Thermal_Flux')


# =========================================================================
# Fig 4: Prescribed-Heating Thermal Traces & Post-Pulse Multi-Scale Recovery (New Main Fig 4)
# =========================================================================
def fig4_thermal_recovery():
    print("[4/7] Generating Fig 4: Prescribed Heating & Thermal Recovery...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=300)
    
    # Panel A: 3D FEA Prescribed-Heating Thermal Rise (1 uW Step)
    df0 = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_OFF_Ablated.csv'))
    df1 = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_ON_Baseline.csv'))
    sub0 = df0[df0['t_ps'] <= 2000.0]
    sub1 = df1[df1['t_ps'] <= 2000.0]
    
    t0_ns = sub0['t_ps'] / 1000.0
    t1_ns = sub1['t_ps'] / 1000.0
    
    ax1.plot(t0_ns, sub0['Delta_T_avg_K'], 'r-', lw=2.8,
             label=r'Graphene OFF: $\tau_{63.2\%} = 429.1\ \mathrm{ps}\ (R_{\rm th} = 1.72\times 10^6\ \mathrm{K/W})$')
    ax1.plot(t1_ns, sub1['Delta_T_avg_K'], 'g-', lw=2.8,
             label=r'Graphene ON: $\tau_{63.2\%} = 41.9\ \mathrm{ps}\ (R_{\rm th} = 5.37\times 10^5\ \mathrm{K/W})$')
    ax1.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Volume-Average Rise $\Delta T_{\rm avg}$ (K)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold')
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(-0.05, 2.15)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)

    # Panel B: Dynamic Single-Pole ROM Recovery & Phase Quenching (Origin at t - 2.50 ns)
    df_rec = pd.read_csv(os.path.join(ROOT_DIR, 'transients/thermal_recovery_model_comparison.csv'))
    t_post = df_rec['t_post_shutoff_ps']
    
    # Left axis: Single-pole ROM cooling
    ax2.plot(t_post, df_rec['single_pole_norm_DeltaT'] * 100.0, 'b-', lw=2.8,
             label=r'Dynamic Cooling ($V_G = 0\ \mathrm{V}$, $\tau = 41.9\ \mathrm{ps}$)')
    tau_ps = 41.894
    t_pass = np.linspace(0, 300, 301)
    ax2.plot(t_pass, np.exp(-t_pass / tau_ps) * 100.0, 'k--', lw=2.0, alpha=0.7,
             label=r'Passive Cooling ($\Delta T_0 e^{-t/\tau}$)')
    ax2.axhline(5.0, color='r', linestyle=':', lw=1.8, label=r'5% Threshold (Passive: 125.5 ps | Dynamic: 151.2 ps)')
    
    # Phase fraction quenching on right axis
    ax2_r = ax2.twinx()
    ax2_r.plot(t_post, df_rec['single_pole_fm'], 'g-.', lw=2.6, label=r'Metallic Fraction $f_m(t)$ ($V_G = 0\ \mathrm{V}$)')
    ax2_r.axhline(1/3.0, color='gray', linestyle=':', lw=1.8, label=r'Percolation Threshold ($f_c = 1/3$)')
    ax2_r.set_ylabel(r'Metallic Volume Fraction $f_m$', color='green', fontsize=16.5, fontweight='bold')
    ax2_r.tick_params(axis='y', labelcolor='green', labelsize=15.0)
    for l in ax2_r.get_yticklabels():
        l.set_fontweight('bold')
    ax2_r.set_ylim(0.0, 0.75)

    ax2.set_xlabel(r'Post-Pulse Time $t - 2.50\ \mathrm{ns}$ (ps)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Normalized Excess Temp $\Delta T / \Delta T_0$ (%)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold')
    ax2.set_xlim(0, 300)
    ax2.set_ylim(0, 118)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=12.0, framealpha=0.9, borderpad=0.5, labelspacing=0.25)

    save_fig(fig, 'Fig4_Thermal_Pulse_Recovery', alias='Fig4_Graphene_Stabilization')


# =========================================================================
# Fig 5: Constitutive Gate Electrostatics of the ROM & Phase Equilibria (New Main Fig 5)
# =========================================================================
def fig5_electrostatics():
    print("[5/7] Generating Fig 5: Constitutive Gate Electrostatics...")
    cfg = gm.get_config()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=300)
    
    # Panel A: Transferred sheet density from quantum-capacitance closure
    vg_vals = np.linspace(0.0, 2.0, 100)
    vd_cases = [
        (0.0, '#1f77b4', '-'),
        (1.0, '#2ca02c', '--'),
        (2.0, '#d62728', '-.')
    ]
    for vd, col, ls in vd_cases:
        n2d_vals = [gm.calc_N2D(vg, vd, cfg) * 1e-16 for vg in vg_vals]
        ax1.plot(vg_vals, n2d_vals, color=col, linestyle=ls, lw=2.8, label=f'$V_D = {vd:.1f}$ V')
        
    ax1.set_xlabel('Gate Voltage $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Transferred Sheet Density $N_{\mathrm{VO_2}}$ ($10^{16}\ \mathrm{m}^{-2}$)', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold')
    ax1.set_xlim(0.0, 2.0)
    ax1.set_ylim(-0.5, 21.0)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=13.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)

    # Panel B: Equilibrium metallic fraction evaluated with regularized barriers at VD = 0
    T_vals = np.linspace(300.0, 360.0, 120)
    vg_cases = [
        (0.0, '#1f77b4', '-'),
        (1.0, '#2ca02c', '--'),
        (2.0, '#d62728', '-.')
    ]
    for vg, col, ls in vg_cases:
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
        ax2.plot(T_vals, fm_list, color=col, linestyle=ls, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
        
    ax2.axhline(1/3.0, color='gray', linestyle=':', lw=1.8, label=r'Percolation ($f_c = 1/3$)')
    ax2.set_xlabel('Temperature $T$ (K)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Equilibrium Metallic Fraction $f_{m,\rm eq}$', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold')
    ax2.set_xlim(300.0, 360.0)
    ax2.set_ylim(-0.02, 1.25)
    ax2.grid(True, alpha=0.3)
    # Headroom y in [1.00, 1.25] is 100% vacant above saturation fm=1.0, ensuring zero curve overlap
    ax2.legend(loc='upper center', ncol=2, fontsize=13.0, framealpha=0.9, borderpad=0.4, columnspacing=1.0)

    save_fig(fig, 'Fig5_Constitutive_Electrostatics', alias='Fig2_Electrostatics')


# =========================================================================
# Fig 6: Protocol-Dependent Phase-Conversion Thresholds (New Main Fig 6)
# =========================================================================
def fig6_electrical_switching():
    print("[6/7] Generating Fig 6: Protocol-Dependent Thresholds...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=300)
    
    # Panel A: Forward source ramp phase-fraction trajectories (zero-origin 0.16 V/ns ramp)
    df_fine = pd.read_csv(os.path.join(ROOT_DIR, 'hysteresis/fine_ramp_threshold_resolution.csv'))
    colors = {0.0: '#1f77b4', 1.0: '#2ca02c', 2.0: '#d62728'}
    for vg, col in colors.items():
        sub = df_fine[df_fine['V_G_V'] == vg]
        sub = sub[(sub['time_ns'] >= 28.0) & (sub['time_ns'] <= 31.5)]
        ax1.plot(sub['time_ns'], sub['fm_avg'], color=col, lw=2.8, label=f'$V_G = {vg:.1f}$ V')
        
    ax1.axhline(1/3.0, color='k', linestyle='--', lw=1.8, label=r'First $f_m = 1/3$ (percolation)')
    ax1.axhline(0.50, color='gray', linestyle=':', lw=1.8, label=r'$f_m = 0.50$ (transition midpoint)')
    ax1.set_xlabel('Ramp Time (ns)', fontsize=16.5, fontweight='bold')
    ax1.set_ylabel(r'Metallic Volume Fraction $f_m$', fontsize=16.5, fontweight='bold')
    ax1.set_title('(a)', fontsize=17.5, fontweight='bold')
    ax1.set_xlim(28.0, 31.5)
    ax1.set_ylim(-0.02, 0.85)
    ax1.grid(True, alpha=0.3)
    # Move legend to upper left where fm is 0 for all curves at t < 29.3 ns (ZERO curve overlap!)
    ax1.legend(loc='upper left', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Regenerated thresholds after spatial closure controls
    df_p0 = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P0_A1_Gate_Closure_Paired_Comparison.csv'))
    df_sp = df_p0[df_p0['Closure_Mode'] == 'spatially_averaged']
    
    ax2.plot(df_sp['V_gate_V'], df_sp['V_onset_ramp_V'], 'o-', color='#1f77b4', lw=2.8, markersize=9,
             label=r'First $f_m = 1/3$ crossing ($\Delta = 299.7\ \mathrm{mV}$)')
    ax2.plot(df_sp['V_gate_V'], df_sp['V_midpoint_ramp_V'], 's--', color='#d62728', lw=2.8, markersize=9,
             label=r'$f_m = 0.50$ crossing ($\Delta = 1028.0\ \mathrm{mV}$)')
    
    ax2.set_xlabel('Gate Voltage $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_ylabel(r'Threshold Voltage $V_{\rm app,SET}$ (V)', fontsize=16.5, fontweight='bold')
    ax2.set_title('(b)', fontsize=17.5, fontweight='bold')
    ax2.set_ylim(4.35, 6.25)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=13.0, framealpha=0.9, borderpad=0.5, labelspacing=0.3)

    save_fig(fig, 'Fig6_Phase_Conversion_Thresholds', alias='Fig3_Electrical_Switching')


# =========================================================================
# Fig 7: Principal ROM Pulse Dynamics & Energy Budget (New Main Fig 7)
# =========================================================================
def fig7_transient():
    print("[7/7] Generating Fig 7: ROM Dynamics & Energy Budget...")
    fig, axs = plt.subplots(2, 2, figsize=(16.5, 12.5), dpi=300)
    t0_df = pd.read_csv(os.path.join(ROOT_DIR, 'transients/Transient_VG_0.0.csv'))
    t2_df = pd.read_csv(os.path.join(ROOT_DIR, 'transients/Transient_VG_2.0.csv'))
    
    # Panel A: Drain current
    ax = axs[0, 0]
    p0 = t0_df['I_D (uA)'].max()
    p2 = t2_df['I_D (uA)'].max()
    ax.plot(t0_df['time_ns'], t0_df['I_D (uA)'], 'b-', lw=2.8, label=rf'$V_G = 0.0$ V (Peak: {p0:.1f} $\mu$A)')
    ax.plot(t2_df['time_ns'], t2_df['I_D (uA)'], 'r--', lw=2.8, label=rf'$V_G = 2.0$ V (Peak: {p2:.1f} $\mu$A)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Drain Current $I_D$ ($\mu$A)', fontsize=16.5, fontweight='bold')
    ax.set_title('(a)', fontsize=17.5, fontweight='bold')
    ax.set_xlim(0, 4.0)
    ax.set_ylim(-5, 145)
    ax.grid(True, alpha=0.3)
    # Move to upper right where current is 0 after t = 2.5 ns (ZERO overlap with pulse!)
    ax.legend(loc='upper right', fontsize=13.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel B: Volume-average temperature
    ax = axs[0, 1]
    ax.plot(t0_df['time_ns'], t0_df['T_avg (K)'], 'b-', lw=2.8, label=r'$V_G = 0.0$ V (Plat: 341.1 K)')
    ax.plot(t2_df['time_ns'], t2_df['T_avg (K)'], 'r--', lw=2.8, label=r'$V_G = 2.0$ V (Plat: 325.9 K)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Volume-Average Temp $T_{\rm avg}$ (K)', fontsize=16.5, fontweight='bold')
    ax.set_title('(b)', fontsize=17.5, fontweight='bold')
    ax.set_xlim(0, 4.0)
    ax.set_ylim(296, 356)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=13.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel C: Metallic volume fraction
    ax = axs[1, 0]
    ax.plot(t0_df['time_ns'], t0_df['fm_avg'], 'b-', lw=2.8, label=r'$V_G = 0.0$ V')
    ax.plot(t2_df['time_ns'], t2_df['fm_avg'], 'r--', lw=2.8, label=r'$V_G = 2.0$ V')
    ax.axhline(1/3.0, color='gray', linestyle=':', lw=1.8, label=r'Percolation ($f_c = 1/3$)')
    ax.set_xlabel('Time (ns)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel(r'Metallic Volume Fraction $f_m$', fontsize=16.5, fontweight='bold')
    ax.set_title('(c)', fontsize=17.5, fontweight='bold')
    ax.set_xlim(0, 4.0)
    ax.set_ylim(-0.05, 1.15)
    ax.grid(True, alpha=0.3)
    # Move to upper right where fm is 0 after t = 2.7 ns (ZERO overlap with data or line!)
    ax.legend(loc='upper right', fontsize=13.5, framealpha=0.9, borderpad=0.5, labelspacing=0.3)
    
    # Panel D: Device and load energy over full 4 ns window with Switching-Event Inset
    ax = axs[1, 1]
    df_lat = pd.read_csv(os.path.join(ROOT_DIR, 'csv_exports/P0_B4_Latent_Heat_Energy_Accounting.csv'))
    df_sub = df_lat[df_lat['Include_Latent_Heat'] == True]
    df_audit = pd.read_csv(os.path.join(ROOT_DIR, 'validated_data/pulse_results/authoritative_pulse_energy_audit.csv'))
    
    x = np.arange(len(df_sub['V_gate_V']))
    w = 0.35
    ax.bar(x - w/2, df_sub['E_dev_total_pJ'] * 1e3, w, label=r'Device $E_{\rm dev}$ ($0\to 4\ \mathrm{ns}$)', color='#e74c3c')
    ax.bar(x + w/2, df_sub['E_res_total_pJ'] * 1e3, w, label=r'Load $E_{\rm res}$ ($50\ \mathrm{k}\Omega$, $0\to 4\ \mathrm{ns}$)', color='#3498db')
    ax.plot(x, df_sub['E_src_total_pJ'] * 1e3, 'go-', lw=2.8, markersize=9, label=r'Total Source $E_{\rm src}$ ($0\to 4\ \mathrm{ns}$)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{v:.1f} V' for v in df_sub['V_gate_V']], fontsize=15.0, fontweight='bold')
    ax.set_xlabel('Gate Voltage $V_G$ (V)', fontsize=16.5, fontweight='bold')
    ax.set_ylabel('Full-Pulse Energy (fJ)', fontsize=16.5, fontweight='bold')
    ax.set_title('(d)', fontsize=17.5, fontweight='bold')
    ax.set_ylim(0, 3200)
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(loc='upper left', ncol=1, fontsize=12.5, framealpha=0.9, borderpad=0.5, labelspacing=0.25)

    # Inset plot: nanoscale switching event energy (0 to t_event) - perfectly clear of bars
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    ax_ins = inset_axes(ax, width='36%', height='34%', loc='upper right', borderpad=1.2)
    ax_ins.set_facecolor('white')
    ax_ins.plot(df_audit['V_G_V'], df_audit['Switching_E_dev_fJ'], 's-', color='#c0392b', lw=2.4, markersize=7)
    ax_ins.set_title(r'Switching Event ($0\to t_{\rm event}$)', fontsize=12.5, fontweight='bold')
    ax_ins.set_xlabel(r'Gate $V_G$ (V)', fontsize=11.5, fontweight='bold')
    ax_ins.set_ylabel(r'$E_{\rm dev,sw}$ (fJ)', fontsize=11.5, fontweight='bold')
    ax_ins.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
    ax_ins.set_xticklabels(['0', '0.5', '1', '1.5', '2'], fontsize=11.0, fontweight='bold')
    ax_ins.tick_params(axis='both', which='major', labelsize=11.0)
    ax_ins.set_ylim(4.2, 6.0)
    ax_ins.grid(True, alpha=0.3)

    save_fig(fig, 'Fig7_Transient_Dynamics_Energy', alias='Fig6_Transient_Validation')


if __name__ == '__main__':
    print("=" * 70)
    print("REGENERATING ALL 7 PRIMARY MANUSCRIPT FIGURES")
    print("=" * 70)
    fig1_architecture()
    fig2_thermal_maps()
    fig3_thermal_flux()
    fig4_thermal_recovery()
    fig5_electrostatics()
    fig6_electrical_switching()
    fig7_transient()
    print("=" * 70)
    print("All Main Figures generated successfully in 'manuscript_figures' folder.")
    print("=" * 70)
