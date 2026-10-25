# Graphene-Mediated Electrothermal Control of Phase-Transition Dynamics in Nanoscale $\mathrm{VO_2}$ Devices

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.placeholder.svg)](https://doi.org/10.5281/zenodo.placeholder)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Official open-source computational simulation framework, reduced-order electrothermal models, 3D finite-element thermal calibration scripts, and complete research reproduction pipeline for:

> **Graphene-Mediated Electrothermal Control of Phase-Transition Dynamics in Nanoscale $\mathrm{VO_2}$ Devices**  
> Gourab Datta$^{1,2}$, Sarah Sharif$^{1,2}$, Hritom Das$^{3}$, and Mike Banad$^{1,2,*}$  
> $^{1}$*Intelligent Neuromorphic and Quantum Understanding for Innovative Research and Engineering (INQUIRE) Lab, University of Oklahoma, Norman, OK, USA*  
> $^{2}$*School of Electrical and Computer Engineering, University of Oklahoma, Norman, OK, USA*  
> $^{3}$*School of Electrical and Computer Engineering, Oklahoma State University, Stillwater, OK, USA*  
> $^{*}$*Corresponding author: `bana@ou.edu`*

---

## Abstract

Phase-transition devices offer compact switching elements for emerging electronics, yet their design requires balancing electronic control with the heat generated during operation. A lower switching voltage alone does not reveal whether a device responds faster or consumes less energy, because phase conversion, heat removal, and circuit loading act together. Here, we develop a computational framework for a graphene-interlayer vanadium dioxide ($\mathrm{VO_2}$) device that connects three-dimensional thermal finite-element analysis (FEA) with gate-dependent phase kinetics and a load-resolved circuit model. Matched comparisons reveal that thermal spreading, switching speed, and energy consumption cannot be optimized through a single device metric. Under the evaluated protocols, the fitted spreading configuration raises ramp onset while shortening pulse latency, and gate-induced reductions in device energy coexist with increased source-energy consumption. Charge-coupling and interface controls identify which trends persist and which predictions depend strongly on the chosen constitutive description. The resulting framework relates material and interface choices to distinct measures of onset, conversion, recovery, and energy, providing a basis for evaluating electrothermal design tradeoffs within specified device and operating conditions.

---

## Device Architecture & Operating Principles

The three-terminal Graphene-Interlayer $\mathrm{VO_2}$ Phase-Transition Switch (**GIV-PTS**) comprises:
- **Active Channel**: $50\text{ nm} \times 50\text{ nm} \times 5\text{ nm}$ $\mathrm{VO_2}$ thin film ($V = 1.25\times 10^{-23}\text{ m}^3$, $m = 5.425\times 10^{-20}\text{ kg}$).
- **Interlayer Heat Spreader**: Centered $48\text{ nm} \times 50\text{ nm}$ monolayer graphene sheet with $1\text{ nm}$ source/drain dielectric setbacks to prevent direct electrical bridging. An equivalent $1\text{ nm}$ physical sheet model uses in-plane thermal conductivity $k = 201\text{ W/(m}\cdot\text{K)}$, preserving sheet conductance $2.010\times 10^{-7}\text{ W/K}$.
- **Gate Dielectric**: $5\text{ nm}$ $\mathrm{HfO_2}$ ($\epsilon_r = 25.0$).
- **Thermal Sinks**: $100\text{ nm}$ $\mathrm{SiO_2}$ over Si substrate held at $T_{\rm amb} = 300\text{ K}$; lateral metal contacts (Au/Ti) act as $300\text{ K}$ isothermal heat-removal boundaries.

```
       [ Top Gate ]
          |
     [ 5 nm HfO2 ] (eps_r = 25)
          |
   [ Graphene Sheet ] (Heat Spreader & Quantum Capacitance Interlayer)
  +-------+-----------------------+-------+
  |  1nm  |      VO2 Channel      |  1nm  |  (50 nm x 50 nm x 5 nm)
  |Setback|  Insulator-to-Metal   |Setback|
  +-------+-----------------------+-------+
  [Source]                         [Drain] ---> Series Load R_L = 50 kOhm
     |                                |
  =========================================
          SiO2 Substrate (300 K)
```

---

## Computational Framework & Governing Physics

The coupled reduced-order model (ROM) solves the self-consistent interaction between gate-induced charge transfer, phase-transition kinetics, dynamic heat generation and dissipation, and external series circuit loading.

### 1. Quantum Capacitance & Longitudinal Charge Closure
The gate-to-channel voltage partition accounts for the finite density of states in monolayer graphene via its quantum capacitance:
$$v_+ = \frac{q N_{\rm 2D}}{C_{\rm ox}} + \frac{\hbar v_F \sqrt{\pi N_{\rm 2D}}}{q}, \quad C_{\rm ox} = \frac{\epsilon_0 \epsilon_r}{t_{\rm ox}}$$
where $v = V_G - u V_D$ with normalized coordinate $u = x/L$, regularized by $v_+ = (v + \sqrt{v^2 + \delta_V^2})/2$ ($\delta_V = 0.01\text{ V}$). The effective transferred density entering the channel phase kinetics is:
$$N_{\rm VO2} = \eta_{\rm CT} \int_0^1 N_{\rm 2D}(V_G - u V_D)\, du$$
with charge-transfer efficiency $\eta_{\rm CT} = 0.50$ applied once.

### 2. Two-State Phase Kinetics with Regularized Activation Barriers
The dynamical state of the channel is tracked by the volume-average metallic volume fraction $f_m \in [0, 1]$:
$$\frac{df_m}{dt} = k_{\rm IMT}(1 - f_m) - k_{\rm MIT} f_m, \quad k_j = \nu \exp\left(-\frac{G^\ddagger_j}{k_{B,\text{eV}} T}\right)$$
with attempt frequency $\nu = 6.64\times 10^{13}\text{ s}^{-1}$ (anchored to the $V\text{--}V$ homopolar optical phonon mode) and smoothly regularized positive activation barriers:
$$G^\ddagger_j = \frac{1}{2}\left(A_j + \sqrt{A_j^2 + \delta_G^2}\right), \quad \delta_G = 0.005\text{ eV}$$
where:
$$A_{\rm IMT} = \Delta G_0 - \alpha_{\rm th}(T - T_0) - a_{\rm IMT} x_g$$
$$A_{\rm MIT} = \Delta G_0 + \alpha_{\rm th}(T - T_0) + a_{\rm MIT} x_g$$
with dimensionless coordinate $x_g = \beta_X N_{\rm VO2}$, $\beta_X = 10^{-18}\text{ m}^2$, $a_{\rm IMT} = 0.517\text{ eV}$, and $a_{\rm MIT} = 0.215\text{ eV}$.

### 3. Dynamic Heat Balance with Explicit Phase Enthalpy
Lumped-element thermal dynamics balances Joule heating against heat removal through the calibrated thermal pathway:
$$C_{\rm th} \frac{dT}{dt} + H_{\rm tr} \frac{df_m}{dt} = V_D I_D - \frac{T - T_{\rm amb}}{R_{\rm th}}$$
where $H_{\rm tr} = \Delta H_t \rho_{\rm VO2} \mathcal{V} = 2.76675\text{ fJ}$ is the total transformation enthalpy ($\Delta H_t = 5.1\times 10^4\text{ J/kg}$, $\rho_{\rm VO2} = 4340\text{ kg/m}^3$). For graphene ON, 3D FEA calibration yields $R_{\rm th} = 5.3718\times 10^5\text{ K/W}$ and $C_{\rm th} = 7.7989\times 10^{-17}\text{ J/K}$ ($\tau_{\rm th} = 41.89\text{ ps}$).

### 4. Effective-Medium Electrical Transport & Circuit Load Line
Mixed-phase electrical conductivity follows the symmetric Bruggeman effective-medium approximation:
$$f_m \frac{\sigma_{\rm met} - \sigma_{\rm eff}}{\sigma_{\rm met} + 2\sigma_{\rm eff}} + (1 - f_m)\frac{\sigma_{\rm ins,PF} - \sigma_{\rm eff}}{\sigma_{\rm ins,PF} + 2\sigma_{\rm eff}} = 0$$
with Poole-Frenkel field-assisted conduction in the insulating phase:
$$\sigma_{\rm ins,PF} = \sigma_{\rm ins} \exp\left[\min\left(\frac{\beta_E \sqrt{E_{\rm reg}}}{k_{B,\text{J}} T}, 5\right)\right], \quad E_{\rm reg} = \sqrt{(V_D/L)^2 + E_0^2}$$
where $\beta_E = 1.923\times 10^{-24}\text{ J}\cdot\text{m}^{1/2}\text{V}^{-1/2}$. At every time step, the device is constrained by the external load line:
$$V_{\rm app}(t) = V_D(t) + R_L I_D(t), \quad R_L = 50\text{ k}\Omega, \quad I_D = \frac{V_D \sigma_{\rm eff} W t_{\rm VO2}}{L}$$

---

## Key Reconciled Physical Results

| Physical Observable | Graphene OFF | Graphene ON | Relative Effect & Physical Significance |
| :--- | :---: | :---: | :--- |
| **Volume-Average Thermal Resistance** ($R_{\rm th,avg}$) | $1.7241\times 10^6\text{ K/W}$ | $5.3718\times 10^5\text{ K/W}$ | **$-68.80\%$** ($3.21\times$ higher heat dissipation rate) |
| **Thermal Rise Time** ($\tau_{\text{63.2\%}}$) | $429.10\text{ ps}$ | $41.89\text{ ps}$ | **$10.24\times$** faster thermal dissipation into lateral sinks |
| **Dynamic Percolation Threshold** ($V_{\rm SET}$ at $f_m = 1/3$) | $4.878\text{ V}$ ($V_G=0\text{ V}$) | $4.579\text{ V}$ ($V_G=2\text{ V}$) | **$-299.7\text{ mV}$** gate-induced threshold reduction |
| **Midpoint Phase Conversion** ($V_{\rm SET}$ at $f_m = 0.50$) | $5.607\text{ V}$ ($V_G=0\text{ V}$) | $4.579\text{ V}$ ($V_G=2\text{ V}$) | **$-1028.0\text{ mV}$** load-throttled transition shift |
| **Switching Latency** ($6.35\text{ V}$ pulse, $50\text{ k}\Omega$) | $43.74\text{ ps}$ ($V_G=0\text{ V}$) | $36.21\text{ ps}$ ($V_G=2\text{ V}$) | **$-7.53\text{ ps}$** gate acceleration (17.2% faster) |
| **Active-Device Switching Energy** ($E_{\rm dev,sw}$) | $5.6027\text{ fJ}$ ($V_G=0\text{ V}$) | $4.6461\text{ fJ}$ ($V_G=2\text{ V}$) | **$-17.07\%$** energy dissipated in channel to event |
| **Full-Window Circuit Dissipation** ($0\to 4\text{ ns}$) | $156.0\text{ fJ}$ ($V_G=0\text{ V}$) | $99.7\text{ fJ}$ ($V_G=2\text{ V}$) | Device dissipation decreases while source energy increases ($1.415\to 1.487\text{ pJ}$) |

---

## Environment Setup & Quick Start

### 1. Prerequisites
The framework requires Python 3.9+ with standard scientific libraries:
```bash
git clone https://github.com/INQUIRELAB/Graphene-Mediated-Nanoscale-VO2-Phase-Transition-Switch.git
cd Graphene-Mediated-Nanoscale-VO2-Phase-Transition-Switch

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. One-Click Reproduction of All Research Findings
To execute the complete simulation suite and reproduce all physical tables, time constants, switching latencies, dynamic thresholds, and energy metrics:
```bash
python run_simulations.py
```
This runs the stiff implicit Radau integrator across all operating conditions and outputs the full set of physical observables in under 10 seconds.

---

## Detailed Research Reproduction by Module

### Module 1: Thermal Characterization & Heat Spreading
Demonstrates the lateral heat-spreading capability of the monolayer graphene interlayer:
```python
import giv_pts_model as gm
cfg = gm.get_config()

r_on = cfg.R_th_on     # 5.3718e5 K/W
r_off = cfg.R_th_off   # 1.7241e6 K/W
tau_on = r_on * cfg.C_th_on * 1e12    # 41.89 ps
tau_off = r_off * cfg.C_th_off * 1e12 # 429.11 ps

print(f"Thermal Resistance Reduction: {(1 - r_on/r_off)*100:.2f}%")
print(f"Thermal Time Constant Ratio : {tau_off/tau_on:.2f}x faster")
```

### Module 2: Gate-Controlled Dynamic Pulse Switching
Simulates the nonlinear phase transition under a $6.35\text{ V}$ pulse excitation ($1\text{ ps}$ logistic edge, $2\text{ ns}$ flat top) through a $50\text{ k}\Omega$ series resistor:
```python
import giv_pts_model as gm

cfg = gm.get_config()

# Event condition: percolation threshold fm = 1/3
def hit_percolation(t, y):
    return y[0] - (1.0 / 3.0)
hit_percolation.terminal = True
hit_percolation.direction = 1

# Solve at VG = 0 V and VG = 2 V
sol_0v = gm.solve_transient(0.0, gm.pulse_waveform, (0, 4e-9), cfg=cfg, events=hit_percolation)
sol_2v = gm.solve_transient(2.0, gm.pulse_waveform, (0, 4e-9), cfg=cfg, events=hit_percolation)

lat_0v = (sol_0v.t_events[0][0] - 0.5e-9) * 1e12  # 43.74 ps
lat_2v = (sol_2v.t_events[0][0] - 0.5e-9) * 1e12  # 36.21 ps
print(f"Gate Acceleration: {lat_0v - lat_2v:.2f} ps faster at VG = 2 V")
```

### Module 3: Dynamic Forward-Ramp Threshold Voltage Modulation
Evaluates dynamic threshold voltages under a $0.16\text{ V/ns}$ forward ramp ($0 \to 8\text{ V}$ in $50\text{ ns}$):
```bash
python scripts/resolve_continuous_threshold_modulation.py
```
This evaluates the non-aliased continuous crossing voltages:
- **Percolation onset ($f_m = 1/3$)**: shifts from $4.878\text{ V}$ ($V_G=0\text{ V}$) to $4.579\text{ V}$ ($V_G=2\text{ V}$), giving $\Delta V_{\rm SET} \approx -300\text{ mV}$.
- **Transition midpoint ($f_m = 0.50$)**: shifts from $5.607\text{ V}$ ($V_G=0\text{ V}$) to $4.579\text{ V}$ ($V_G=2\text{ V}$), giving $\Delta V_{\rm SET} = -1.028\text{ V}$.

### Module 4: Parameter Sensitivity & Model Robustness
Analyzes the stability of gate-induced acceleration under $\pm 10\%$ thermal capacitance variation and $\pm 20\%$ gate-charge coupling variation:
```bash
python scripts/latency_sensitivity_analysis.py
```
Confirms that differential latency modulation ($\Delta t_{\rm lat} = t_{\rm lat}(0\text{V}) - t_{\rm lat}(2\text{V})$) remains strictly positive across all physical uncertainty bounds, spanning $6.03\text{ ps}$ to $9.19\text{ ps}$.

---

## 3D Finite-Element Modeling in COMSOL Multiphysics

The thermal parameters ($R_{\rm th}$, $C_{\rm th}$, spatial temperature fields, and heat flux distributions) were computed using COMSOL Multiphysics 6.3 (Build 290).

The Java API scripts to generate and solve the 3D model are provided in [`comsol/`](comsol/):
1. [`comsol/Run_Authoritative_Thermal_Calibration.java`](comsol/Run_Authoritative_Thermal_Calibration.java): Complete 3D geometry generator, mesh builder, boundary condition assigner, and stationary/transient solver.
2. [`comsol/ExportAuthenticCOMSOLSpatialFields.java`](comsol/ExportAuthenticCOMSOLSpatialFields.java): Extracts full 3D in-plane ($z = 2.5\text{ nm}$) and cross-sectional ($y = 25\text{ nm}$) temperature meshes and heat flux vector fields.
3. [`comsol/COMSOL_MODEL_ACCESS.md`](comsol/COMSOL_MODEL_ACCESS.md): Documents the pre-solved binary model (`Run_Authoritative_Thermal_Calibration_Model.mph`, 217.6 MB) with SHA-256 checksum and download release link.

To execute via COMSOL batch:
```bash
comsolbatch -inputfile comsol/Run_Authoritative_Thermal_Calibration.java
```

---

## Repository Structure

```
.
├── README.md                                # Comprehensive scientific documentation & reproduction guide
├── LICENSE                                  # Open-source MIT License
├── requirements.txt                         # Python dependencies (numpy, scipy, pandas, matplotlib)
├── .gitignore                               # Git ignore configuration
├── authoritative_model_config.json          # Master device geometry and material parameter set
├── run_simulations.py                       # One-click master simulation reproduction script
│
├── scripts/                                 # Device-physics simulation modules
│   ├── giv_pts_model.py                     # Canonical stiff electrothermal solver & ROM engine
│   ├── resolve_continuous_threshold_modulation.py # Forward ramp threshold simulation
│   └── latency_sensitivity_analysis.py      # Paired parameter sensitivity sweeps
│
├── validated_data/                          # Authenticated simulation outputs & calibration data
│   ├── spatial_fields/                      # 3D in-plane and cross-sectional temperature exports
│   ├── thermal_calibration/                 # Stationary and transient thermal calibration curves
│   ├── pulse_results/                       # Pulse transient trajectories and energy accounting
│   ├── ramp_results/                        # Forward-ramp threshold crossing data
│   └── bypass_sensitivity/                  # Graphene contact bypass and shunting analyses
│
├── csv_exports/                             # Exported numerical tables matching paper results
├── transients/                              # High-resolution numerical ODE solution traces (0-4 ns)
├── hysteresis/                              # Dynamic ramp trajectories and threshold datasets
├── robustness/                              # Thermal Boundary Resistance (TBR) parametric sweeps
├── supporting/                              # Supporting spatial cutline and transient datasets
│
└── comsol/                                  # 3D FEA source models & API execution scripts
    ├── Run_Authoritative_Thermal_Calibration.java
    ├── ExportAuthenticCOMSOLSpatialFields.java
    ├── ExportAuthenticCOMSOLSpatialFields.log
    └── COMSOL_MODEL_ACCESS.md
```

---

## Citation

If you use this computational model, simulation code, or thermal calibration data in your research, please cite:

```bibtex
@article{Datta2026GrapheneVO2,
  title={Graphene-Mediated Electrothermal Control of Phase-Transition Dynamics in Nanoscale $\mathrm{VO_2}$ Devices},
  author={Datta, Gourab and Sharif, Sarah and Das, Hritom and Banad, Mike},
  journal={Advanced Electronic Materials},
  year={2026}
}
```

---

## License & Acknowledgments

This project is licensed under the [MIT License](LICENSE).

This material is based upon work supported by the **Air Force Office of Scientific Research (AFOSR)** under award number **FA9550-25-1-0322**.
