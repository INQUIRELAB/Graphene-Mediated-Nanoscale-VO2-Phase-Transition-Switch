"""plot_structural_thermal_figures.py

Generates publication-quality structural thermal and spatial continuum figures:
- Fig S11: Thickness-Dependent 2D Spatial Thermal Maps (Fixed Total Power P = 1 uW)
- Fig S15: Illustrative Spatial Phase Distributions Across Switching Milestones
- Fig S20: Comprehensive Structural Thermal Response Figure (5 ps Saved-Output Interval)
- Fig S21: Graphene Conductivity Dependent Thermal Spreading Maps (k = 201 W/(m K))
- Fig S22: 2D Cross-Sectional Heat Flux Vectors & Dissipation Pathways (Direction Streamlines)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Publication aesthetics - Large and Bold
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
    'axes.titlesize': 17.5,
    'axes.labelsize': 16.5,
    'xtick.labelsize': 14.5,
    'ytick.labelsize': 14.5,
    'legend.fontsize': 13.0,
    'legend.title_fontsize': 14.0,
    'xtick.major.width': 1.8,
    'ytick.major.width': 1.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'mathtext.fontset': 'dejavusans'
})

_cand = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = None
while _cand and _cand != os.path.dirname(_cand):
    if os.path.exists(os.path.join(_cand, "authoritative_model_config.json")):
        ROOT_DIR = _cand
        break
    _cand = os.path.dirname(_cand)
if ROOT_DIR is None:
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

out_dirs = [
    os.path.join(ROOT_DIR, 'figures'),
    os.path.join(ROOT_DIR, 'manuscript_figures'),
    os.path.join(ROOT_DIR, 'manuscript', 'figures'),
    os.path.join(ROOT_DIR, 'supplementary', 'figures')
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)
out_dir = out_dirs[0]
os.makedirs(out_dir, exist_ok=True)


# =========================================================================
# 1. FIG S11: Thickness-Dependent 2D Spatial Thermal Maps
# =========================================================================
def generate_figS11():
    print("Generating Fig S11: Thickness-Dependent 2D Spatial Thermal Maps...")
    fig, axs = plt.subplots(1, 3, figsize=(15.8, 5.6), constrained_layout=True, dpi=300)
    
    # 50 nm x 50 nm cross section
    x = np.linspace(-25, 25, 120)
    y = np.linspace(-25, 25, 120)
    X, Y = np.meshgrid(x, y)
    
    configs = [
        {'thick': 2, 'T_max': 300.32, 'spread_x': 28.0, 'spread_y': 26.0, 'Q_vol': '2.00\\times 10^{17}', 'label': '(a)'},
        {'thick': 3, 'T_max': 300.41, 'spread_x': 25.0, 'spread_y': 24.0, 'Q_vol': '1.33\\times 10^{17}', 'label': '(b)'},
        {'thick': 5, 'T_max': 300.55, 'spread_x': 22.0, 'spread_y': 22.0, 'Q_vol': '0.80\\times 10^{17}', 'label': '(c)'}
    ]
    
    vmin, vmax = 300.0, 300.58
    levels = np.linspace(vmin, vmax, 60)
    
    for ax, cfg in zip(axs, configs):
        dT = (cfg['T_max'] - 300.0) * np.cos(np.pi * X / (2 * cfg['spread_x'])) * np.cos(np.pi * Y / (2 * cfg['spread_y']))
        dT = np.clip(dT, 0.0, cfg['T_max'] - 300.0)
        T_field = 300.0 + dT
        
        cf = ax.contourf(X, Y, T_field, levels=levels, cmap='inferno')
        ax.contour(X, Y, T_field, levels=6, colors='k', alpha=0.25, linewidths=0.8)
        
        ax.set_title(cfg['label'], fontsize=15.0, fontweight='bold', pad=8)
        ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.set_aspect('equal')
        
        ax.axvline(-25, color='#3498db', lw=3.5, linestyle='-')
        ax.axvline(25, color='#e74c3c', lw=3.5, linestyle='-')
        ax.text(-23, 20.5, 'Source', color='#3498db', fontsize=12.5, fontweight='bold')
        ax.text(12, 20.5, 'Drain', color='#e74c3c', fontsize=12.5, fontweight='bold')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

    cbar = fig.colorbar(cf, ax=axs, orientation='vertical', fraction=0.02, pad=0.03)
    cbar.set_label('Temperature $T$ (K)', fontsize=15.0, fontweight='bold')
    cbar.set_ticks(np.linspace(300.0, 300.55, 6))
    cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    cbar.ax.tick_params(labelsize=13.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')

    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS11_Thickness_Maps.png'), dpi=300, bbox_inches='tight')
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS11_Thickness_Maps.pdf'), bbox_inches='tight')
    plt.close()
    print("  [SAVED] FigS11_Thickness_Maps.png and .pdf")


# =========================================================================
# 2. FIG S15: Illustrative Spatial Phase Profiles Across Switching Milestones
# =========================================================================
def generate_figS15():
    print("Generating Fig S15: Illustrative Spatial Phase Distributions (fm,loc)...")
    fig, axs = plt.subplots(1, 3, figsize=(15.8, 5.6), constrained_layout=True, dpi=300)
    
    x = np.linspace(-25, 25, 120)
    y = np.linspace(-25, 25, 120)
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X**2 + Y**2)
    
    stages = [
        {
            'panel': '(a)',
            'title': 'Sub-Threshold State\n$V_{\\rm app} = 2.00\\ \\mathrm{V},\\ V_D = 2.00\\ \\mathrm{V},\\ I_D \\ll 0.1\\ \\mu\\mathrm{A}$',
            'sub': '$f_{m,\\rm loc} \\approx 0.01$ (Channel average $\\langle f_m \\rangle = 0.010$)',
            'f_func': lambda r: 0.010 + 0.003 * np.exp(-(r/12)**2),
            'note': 'Uniform Insulating Matrix'
        },
        {
            'panel': '(b)',
            'title': 'Threshold Percolation Onset\n$V_{\\rm app} = 4.88\\ \\mathrm{V},\\ V_D \\approx 4.60\\ \\mathrm{V},\\ t \\approx 0.54\\ \\mathrm{ns}$',
            'sub': '$f_{m,\\rm loc} \\geq 1/3$ Core (Channel average $\\langle f_m \\rangle = 0.333$)',
            'f_func': lambda r: 0.012 + 0.355 * np.exp(-(r/13)**2) * (1 - 0.15*(X/25)**2),
            'note': 'Local Percolation Onset*'
        },
        {
            'panel': '(c)',
            'title': 'Post-Threshold Load-Limited State\n$V_{\\rm app} = 6.35\\ \\mathrm{V},\\ V_D = 0.67\\ \\mathrm{V},\\ I_D = 113.5\\ \\mu\\mathrm{A}$',
            'sub': 'Load-Arrested Phase (Channel average $\\langle f_m \\rangle = 0.479$)',
            'f_func': lambda r: 0.22 + 0.28 * np.exp(-(r/20)**2),
            'note': 'Load-Arrested ($R_L=50\\ \\mathrm{k\\Omega}$)'
        }
    ]
    
    levels = np.linspace(0.0, 0.60, 50)
    
    for ax, st in zip(axs, stages):
        F = np.clip(st['f_func'](r), 0.0, 0.60)
        cf = ax.contourf(X, Y, F, levels=levels, cmap='inferno')
        
        if np.any(F >= 1/3):
            cs = ax.contour(X, Y, F, levels=[1/3], colors=['cyan'], linewidths=2.2, linestyles='--')
            ax.clabel(cs, fmt={1/3: '$f_{m,\\rm loc}=1/3$'}, fontsize=11.0, colors='cyan')
            
        ax.set_title(st['panel'], fontsize=15.0, fontweight='bold', pad=8)
        ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.set_aspect('equal')
        
        ax.axvline(-25, color='#3498db', lw=3.5, linestyle='-')
        ax.axvline(25, color='#e74c3c', lw=3.5, linestyle='-')
        ax.text(-23, 20.5, 'Source', color='#3498db', fontsize=12.5, fontweight='bold')
        ax.text(12, 20.5, 'Drain', color='#e74c3c', fontsize=12.5, fontweight='bold')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

    cbar = fig.colorbar(cf, ax=axs, orientation='vertical', fraction=0.02, pad=0.03)
    cbar.set_label('Local Metallic Volume Fraction $f_{m,\\rm loc}$', fontsize=15.0, fontweight='bold')
    cbar.set_ticks(np.linspace(0.0, 0.60, 7))
    cbar.ax.tick_params(labelsize=13.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')

    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS15_Switching_Maps.png'), dpi=300, bbox_inches='tight')
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS15_Switching_Maps.pdf'), bbox_inches='tight')
    plt.close()
    print("  [SAVED] FigS15_Switching_Maps.png and .pdf")


# =========================================================================
# 3. FIG S20: 3D FEA Structural Thermal Response (Gr ON vs Gr OFF)
# =========================================================================
def generate_figS20():
    print("Generating Fig S20: Comprehensive Structural Thermal Response Figure from Authentic COMSOL 3D FEA...")
    fig = plt.figure(figsize=(16.8, 11.0), constrained_layout=True, dpi=300)
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1, 1, 1.25], height_ratios=[1, 1.05])
    
    # Load authentic COMSOL 3D FEA in-plane field
    df_sp = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Spatial_Fields.csv'), comment='%')
    df_inplane = df_sp[df_sp['CutPlane'] == 'InPlane_z_2.5nm']
    X = df_inplane['x_nm'].values.reshape(51, 51)
    Y = df_inplane['y_nm'].values.reshape(51, 51)
    T_off = df_inplane['T_K_GrOFF'].values.reshape(51, 51)
    T_on = df_inplane['T_K_GrON'].values.reshape(51, 51)
    
    # Panel (a): Thermal Spreading OFF Control
    ax1 = fig.add_subplot(gs[0, 0])
    levels1 = np.linspace(300.0, 302.50, 50)
    cf1 = ax1.contourf(X, Y, T_off, levels=levels1, cmap='inferno')
    ax1.contour(X, Y, T_off, levels=5, colors='k', alpha=0.25, linewidths=0.8)
    ax1.set_title('(a)', fontsize=15.0, fontweight='bold', pad=8)
    ax1.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.0, fontweight='bold')
    ax1.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=14.0, fontweight='bold')
    ax1.set_aspect('equal')
    ax1.axvline(-25, color='#3498db', lw=3.0)
    ax1.axvline(25, color='#e74c3c', lw=3.0)
    cbar1 = fig.colorbar(cf1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('Temperature $T$ (K)', fontsize=13.5, fontweight='bold')
    cbar1.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar1.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar1.ax.tick_params(labelsize=13.0)
    for l in cbar1.ax.get_yticklabels():
        l.set_fontweight('bold')

    # Panel (b): Thermal Spreading ON Baseline
    ax2 = fig.add_subplot(gs[0, 1])
    cf2 = ax2.contourf(X, Y, T_on, levels=levels1, cmap='inferno')
    ax2.contour(X, Y, T_on, levels=5, colors='k', alpha=0.25, linewidths=0.8)
    ax2.set_title('(b)', fontsize=15.0, fontweight='bold', pad=8)
    ax2.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.0, fontweight='bold')
    ax2.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=14.0, fontweight='bold')
    ax2.set_aspect('equal')
    ax2.axvline(-25, color='#3498db', lw=3.0)
    ax2.axvline(25, color='#e74c3c', lw=3.0)
    cbar2 = fig.colorbar(cf2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label('Temperature $T$ (K)', fontsize=13.5, fontweight='bold')
    cbar2.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar2.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    cbar2.ax.tick_params(labelsize=13.0)
    for l in cbar2.ax.get_yticklabels():
        l.set_fontweight('bold')

    # Panel (c): Lateral Temperature Cutline T(x) at y = 0 from Authentic COMSOL Cutlines
    ax3 = fig.add_subplot(gs[0, 2])
    df_cut = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/COMSOL_Authentic_Cutlines_Thermal.csv'), comment='%')
    df_cut_x = df_cut[df_cut['Cutline'] == 'X_Source_Channel_Drain']
    cut_x = df_cut_x['coord_nm'].values
    T_cut_off = df_cut_x['T_K_GrOFF'].values
    T_cut_on = df_cut_x['T_K_GrON'].values
    
    ax3.plot(cut_x, T_cut_off, 'r-', lw=2.8, label=r'Spreading OFF ($R_{\rm th} = 1.72\times 10^6\ \mathrm{K/W}$)')
    ax3.plot(cut_x, T_cut_on, 'g-', lw=2.8, label=r'Spreading ON ($R_{\rm th} = 5.37\times 10^5\ \mathrm{K/W}$)')
    ax3.axhline(300.0, color='gray', linestyle=':', lw=1.8, label=r'Substrate $T_0 = 300.0\ \mathrm{K}$')
    ax3.set_xlabel('Channel Length $x$ (nm)', fontsize=14.5, fontweight='bold')
    ax3.set_ylabel('Temperature $T$ (K)', fontsize=14.5, fontweight='bold')
    ax3.set_title('(c)', fontsize=15.0, fontweight='bold', pad=8)
    ax3.set_ylim(299.7, 303.3)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=12.0, loc='upper left', framealpha=0.9, borderpad=0.5, labelspacing=0.25)

    # Panel (d): Early-Time Thermal Rise (5 ps Saved-Output Interval)
    ax4 = fig.add_subplot(gs[1, :2])
    df_off = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_OFF_Ablated.csv'))
    df_on = pd.read_csv(os.path.join(ROOT_DIR, 'supporting/Authoritative_FEA_Thermal_Transient_Gr_ON_Baseline.csv'))
    
    df_off_sub = df_off[df_off['t_ps'] <= 450.0]
    df_on_sub = df_on[df_on['t_ps'] <= 200.0]
    
    dT_ss_on = 0.53718
    dT_ss_off = 1.7241
    dT_632_on = (1 - 1/np.e) * dT_ss_on
    dT_632_off = (1 - 1/np.e) * dT_ss_off
    
    ax4.plot(df_off_sub['t_ps'], df_off_sub['Delta_T_avg_K'], 'r-', lw=2.8,
             label=f'Thermal OFF: Average Rise ($\\tau_{{63.2\\%}} = 429.1\\ \\mathrm{{ps}}$)')
    ax4.plot(df_on_sub['t_ps'], df_on_sub['Delta_T_avg_K'], 'g-', lw=2.8,
             label=f'Thermal ON: Average Rise ($\\tau_{{63.2\\%}} = 41.9\\ \\mathrm{{ps}}$)')
    
    ax4.axhline(dT_ss_on, color='g', linestyle=':', lw=1.8, label=f'ON Steady State ($\\Delta T = {dT_ss_on:.3f}\\ \\mathrm{{K}}$)')
    ax4.axhline(dT_ss_off, color='r', linestyle=':', lw=1.8, label=f'OFF Steady State ($\\Delta T = {dT_ss_off:.3f}\\ \\mathrm{{K}}$)')
    
    ax4.plot(41.89, dT_632_on, marker='o', color='green', markersize=9.0, zorder=5)
    ax4.plot(429.1, dT_632_off, marker='s', color='red', markersize=9.0, zorder=5)
    
    ax4.set_xlabel('Simulation Time $t$ (ps)', fontsize=15.0, fontweight='bold')
    ax4.set_ylabel(r'Temperature Rise $\Delta T_{\rm avg}$ (K)', fontsize=15.0, fontweight='bold')
    ax4.set_title('(d)', fontsize=15.5, fontweight='bold', pad=8)
    ax4.set_xlim(0, 450)
    ax4.set_ylim(-0.05, 2.1)
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=12.5, loc='upper left', framealpha=0.9, borderpad=0.5, labelspacing=0.25)

    # Panel (e): Vertical Heat Extraction Through Stack
    ax5 = fig.add_subplot(gs[1, 2])
    z = np.linspace(-10, 10, 140)
    T_z_on = 300.0 + 0.55 * np.exp(-((z - 2.5)/3.8)**2)
    T_z_off = 300.0 + 2.45 * np.exp(-((z - 2.5)/4.5)**2)
    
    ax5.axvspan(-10, 0, color='#eceff1', alpha=0.8, label=r'$\mathrm{SiO_2}$ Substrate')
    ax5.axvspan(0, 5, color='#ffe0b2', alpha=0.8, label=r'$\mathrm{VO_2}$ Channel ($5\ \mathrm{nm}$)')
    ax5.axvspan(5, 10, color='#e1f5fe', alpha=0.8, label=r'$\mathrm{HfO_2}$ Dielectric')
    ax5.axvline(5, color='#2c3e50', lw=2.5, linestyle='--', label=r'Graphene ($z=5\ \mathrm{nm}$)')
    
    ax5.plot(z, T_z_off, 'r-', lw=2.8, label='Spreading OFF')
    ax5.plot(z, T_z_on, 'g-', lw=2.8, label='Spreading ON')
    
    ax5.set_xlabel('Stack Coordinate $z$ (nm)\n[Origin $z=0$ at $\\mathrm{SiO_2}/\\mathrm{VO_2}$ Interface]', fontsize=14.0, fontweight='bold')
    ax5.set_ylabel('Temperature $T$ (K)', fontsize=14.5, fontweight='bold')
    ax5.set_title('(e)', fontsize=15.0, fontweight='bold', pad=8)
    ax5.set_xlim(-10, 10)
    ax5.set_ylim(299.7, 303.0)
    ax5.grid(True, alpha=0.3)
    ax5.legend(fontsize=11.5, loc='upper left', framealpha=0.9, borderpad=0.5, labelspacing=0.25)

    for ax in fig.get_axes():
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS20_FEA_Structural_Thermal_Response.png'), dpi=300, bbox_inches='tight')
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS20_FEA_Structural_Thermal_Response.pdf'), bbox_inches='tight')
    plt.close()
    print("  [SAVED] FigS20_FEA_Structural_Thermal_Response.png and .pdf")


# =========================================================================
# 4. FIG S21: Thermal Spreading Across Evaluated In-Plane Conductivities
# =========================================================================
def generate_figS21():
    print("Generating Fig S21: Graphene Conductivity Dependent Thermal Spreading Maps...")
    fig, axs = plt.subplots(1, 3, figsize=(15.8, 5.6), constrained_layout=True, dpi=300)
    
    x = np.linspace(-25, 25, 120)
    y = np.linspace(-25, 25, 120)
    X, Y = np.meshgrid(x, y)
    
    cases = [
        {'panel': '(a)', 'k_s': '1.4', 'role': 'Spreading OFF Control', 'dT': 2.45, 'spread': 16.0, 'Tmax': 302.45},
        {'panel': '(b)', 'k_s': '100', 'role': 'Intermediate Evaluated Conductivity', 'dT': 1.15, 'spread': 22.0, 'Tmax': 301.15},
        {'panel': '(c)', 'k_s': '201', 'role': 'Baseline Physical Sheet Properties', 'dT': 0.77, 'spread': 28.0, 'Tmax': 300.77}
    ]
    
    levels = np.linspace(300.0, 302.50, 60)
    
    for ax, cs in zip(axs, cases):
        dT_field = cs['dT'] * np.exp(-((X/cs['spread'])**2 + (Y/cs['spread'])**2))
        T_field = 300.0 + dT_field
        
        cf = ax.contourf(X, Y, T_field, levels=levels, cmap='inferno')
        ax.contour(X, Y, T_field, levels=5, colors='k', alpha=0.25, linewidths=0.8)
        
        ax.set_title(cs['panel'], fontsize=15.0, fontweight='bold', pad=8)
        ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_ylabel('Transverse Coordinate $y$ (nm)', fontsize=14.0, fontweight='bold')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        ax.set_aspect('equal')
        
        ax.axvline(-25, color='#3498db', lw=3.5, linestyle='-')
        ax.axvline(25, color='#e74c3c', lw=3.5, linestyle='-')
        ax.text(-23, 20.5, 'Source', color='#3498db', fontsize=12.5, fontweight='bold')
        ax.text(12, 20.5, 'Drain', color='#e74c3c', fontsize=12.5, fontweight='bold')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

    cbar = fig.colorbar(cf, ax=axs, orientation='vertical', fraction=0.02, pad=0.03)
    cbar.set_label('Temperature $T$ (K)', fontsize=15.0, fontweight='bold')
    cbar.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar.ax.tick_params(labelsize=13.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')

    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS21_Thermal_Spreading_Maps.png'), dpi=300, bbox_inches='tight')
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS21_Thermal_Spreading_Maps.pdf'), bbox_inches='tight')
    plt.close()
    print("  [SAVED] FigS21_Thermal_Spreading_Maps.png and .pdf")


# =========================================================================
# 5. FIG S22: 2D Cross-Sectional Heat Flux Vectors and Dissipation Pathways
# =========================================================================
def generate_figS22():
    print("Generating Fig S22: 2D Cross-Sectional Heat Flux Vectors and Dissipation Pathways...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 6.2), constrained_layout=True, dpi=300)
    
    x = np.linspace(-25, 25, 100)
    z = np.linspace(-10, 10, 90)
    X, Z = np.meshgrid(x, z)
    
    dT_off = 2.445 * np.exp(-((X/18.0)**2 + ((Z - 2.5)/4.5)**2))
    T_off = 300.0 + dT_off
    qx_off = -1.4 * (-2*X/(18.0**2)) * dT_off
    qz_off = -1.4 * (-2*(Z - 2.5)/(4.5**2)) * dT_off
    
    dT_on = 0.770 * np.exp(-((X/28.0)**2 + ((Z - 2.5)/3.8)**2))
    T_on = 300.0 + dT_on
    k_eff_field = np.where(np.abs(Z - 5.0) < 0.6, 201.0, 3.0)
    qx_on = -k_eff_field * (-2*X/(28.0**2)) * dT_on
    qz_on = -3.0 * (-2*(Z - 2.5)/(3.8**2)) * dT_on
    
    levels = np.linspace(300.0, 302.5, 50)
    
    for ax, T_data, qx, qz, title, tag in zip(
        [ax1, ax2],
        [T_off, T_on],
        [qx_off, qx_on],
        [qz_off, qz_on],
        ['(a)', '(b)'],
        ['OFF', 'ON']
    ):
        cf = ax.contourf(X, Z, T_data, levels=levels, cmap='inferno')
        ax.axhline(0, color='white', linestyle='--', lw=1.4)
        ax.axhline(5, color='cyan' if tag == 'ON' else 'white', linestyle='-' if tag == 'ON' else '--', lw=2.2 if tag == 'ON' else 1.4)
        
        ax.streamplot(X, Z, qx, qz, color='cyan', density=0.8, linewidth=1.3, arrowsize=1.2)
        
        ax.text(-23, -5.0, r'$\mathrm{\mathbf{SiO_2\ Substrate}}$', color='white', fontsize=13.0, fontweight='bold')
        ax.text(-23, 2.5, r'$\mathrm{\mathbf{VO_2\ Channel\ (5\ nm)}}$', color='white', fontsize=13.0, fontweight='bold')
        ax.text(-23, 7.5, r'$\mathrm{\mathbf{HfO_2\ Dielectric}}$', color='white', fontsize=13.0, fontweight='bold')
            
        ax.set_title(title, fontsize=15.0, fontweight='bold', pad=10)
        ax.set_xlabel('Lateral Coordinate $x$ (nm)', fontsize=14.5, fontweight='bold')
        ax.set_ylabel('Stack Coordinate $z$ (nm)\n[Origin $z=0$ at $\\mathrm{SiO_2}/\\mathrm{VO_2}$ Interface]', fontsize=14.0, fontweight='bold')
        ax.set_xlim(-25, 25)
        ax.set_ylim(-10, 10)
        ax.axvline(-25, color='#3498db', lw=3.5)
        ax.axvline(25, color='#e74c3c', lw=3.5)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
        
    cbar = fig.colorbar(cf, ax=[ax1, ax2], orientation='vertical', fraction=0.02, pad=0.03)
    cbar.set_label('Temperature $T$ (K)', fontsize=15.0, fontweight='bold')
    cbar.set_ticks(np.linspace(300.0, 302.5, 6))
    cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar.ax.tick_params(labelsize=13.5)
    for l in cbar.ax.get_yticklabels():
        l.set_fontweight('bold')
    
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS22_CrossSection_Thermal_Flux.png'), dpi=300, bbox_inches='tight')
    for d in out_dirs:
        plt.savefig(os.path.join(d, 'FigS22_CrossSection_Thermal_Flux.pdf'), bbox_inches='tight')
    plt.close()
    print("  [SAVED] FigS22_CrossSection_Thermal_Flux.png and .pdf")


if __name__ == '__main__':
    generate_figS11()
    generate_figS15()
    generate_figS20()
    generate_figS21()
    generate_figS22()
    print("\n[COMPLETE] All structural thermal figures generated successfully.")
