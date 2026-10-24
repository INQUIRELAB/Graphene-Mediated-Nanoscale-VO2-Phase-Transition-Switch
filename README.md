# Graphene-Mediated Electrothermal Control of Phase-Transition Dynamics in Nanoscale $\mathrm{VO_2}$ Devices

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.placeholder.svg)](https://doi.org/10.5281/zenodo.placeholder)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Audit Validation](https://img.shields.io/badge/Audit%20Tests-12%2F12%20PASS-brightgreen.svg)](audit/validation_results.json)

Official open-source computational code, simulation datasets, 3D finite-element models, and complete reproduction pipeline for:

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

## Device Architecture & Dual Physical Roles of Graphene

The three-terminal Graphene-Interlayer $\mathrm{VO_2}$ Phase-Transition Switch (**GIV-PTS**) comprises:
- **Active Channel**: $50\text{ nm} \times 50\text{ nm} \times 5\text{ nm}$ $\mathrm{VO_2}$ thin film ($V = 1.25\times 10^{-23}\text{ m}^3$, $m = 5.425\times 10^{-20}\text{ kg}$).
- **Interlayer Heat Spreader**: Centered $48\text{ nm} \times 50\text{ nm}$ monolayer graphene sheet ($1\text{ nm}$ source/drain dielectric setbacks to prevent direct electrical bridging). Equivalent $1\text{ nm}$ physical sheet model uses in-plane thermal conductivity $k = 201\text{ W/(m}\cdot\text{K)}$, preserving sheet conductance $2.010\times 10^{-7}\text{ W/K}$.
- **Gate Dielectric**: $5\text{ nm}$ $\mathrm{HfO_2}$ ($\\epsilon_r = 25.0$).
- **Thermal Sinks**: $100\text{ nm}$ $\mathrm{SiO_2}$ over Si substrate held at $T_{\rm amb} = 300\text{ K}$; lateral metal contacts (Au/Ti) act as $300\text{ K}$ isothermal boundaries.

```
       [ Top Gate ]
          |
     [ 5 nm HfO2 ] (eps_r = 25)
          |
   [ Graphene Sheet ] (Heat spreader & Quantum Capacitance)
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

## Key Reconciled Physical Results

| Metric | Graphene OFF | Graphene ON | Relative Effect | Verification Test |
| :--- | :---: | :---: | :---: | :---: |
| **Volume-Avg Thermal Resistance** ($R_{\rm th,avg}$) | $1.7241\times 10^6\text{ K/W}$ | $5.3718\times 10^5\text{ K/W}$ | **$-68.80\%$** ($3.21\times$ heat removal) | `[TST-03]` |
| **Thermal Rise Time** ($\tau$ $63.2\%$) | $429.10\text{ ps}$ | $41.89\text{ ps}$ | **$10.24\times$** faster thermal dissipation | `[TST-03]` |
| **Dynamic Percolation Threshold** ($V_{\rm app,SET}$ at $f_m = 1/3$) | $4.8784\text{ V}$ ($V_G=0\text{V}$) | $4.5792\text{ V}$ ($V_G=2\text{V}$) | **$-299.7\text{ mV}$** gate threshold reduction | `[TST-09]` |
| **Midpoint Phase Conversion** ($f_m = 0.50$) | $5.6072\text{ V}$ ($V_G=0\text{V}$) | $4.5792\text{ V}$ ($V_G=2\text{V}$) | **$-1028.0\text{ mV}$** load-throttled shift | `[TST-09]` |
| **Switching Latency** ($t_{\rm lat}$ at $6.35\text{V}$ pulse) | $43.74\text{ ps}$ ($V_G=0\text{V}$) | $36.21\text{ ps}$ ($V_G=2\text{V}$) | **$-7.53\text{ ps}$** gate acceleration | `[TST-06]` |
| **Continuous Event Switching Energy** ($E_{\rm dev,sw}$) | $5.6027\text{ fJ}$ ($V_G=0\text{V}$) | $4.6461\text{ fJ}$ ($V_G=2\text{V}$) | **$-17.07\%$** device switching energy | `[TST-10]` |
| **Full-Window Circuit Energy Conservation** | $|E_{\rm src} - (E_{\rm dev} + E_R)|$ | $< 5.3\times 10^{-14}$ | Conserved to machine precision | `[TST-08]` |
| **Steady-State Thermal Plateau Balance** | $V_D I_D - \Delta T/R_{\rm th}$ | $< 6.0\times 10^{-13}\text{ K}$ | $T_{\rm plateau} = 340.135\text{ K}$ at $V_G = 0.5\text{V}$ | `[TST-05]` |
| **Contact Bypass Immunity** ($R_{\rm bypass} = 1.2\text{ M}\Omega$) | $I_{\rm ON}/I_{\rm OFF} = 109.04$ | $>99.9\%$ channel current | Zero-shunt approximation validated | `[TST-12]` |

---

## Repository Structure

```
.
├── README.md                      # Comprehensive project documentation
├── LICENSE                        # MIT License
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules
├── run_reproduction.py            # Master one-click automated reproduction runner
├── authoritative_model_config.json # Authoritative frozen physical parameters
│
├── manuscript/                    # Manuscript LaTeX sources, bib, figures, and compiled PDF
│   ├── GIV_PTS_AEM_Manuscript.tex # Primary manuscript source
│   ├── giv_pts_references.bib     # Complete BibTeX bibliography
│   ├── VO2_Transistor_Manuscript.pdf # Full compiled manuscript PDF
│   └── figures/                   # Main publication figures (PDF & high-res PNG)
│
├── supplementary/                 # Supporting Information sources and compiled PDF
│   ├── GIV_PTS_AEM_Supporting_Information.tex # Supplementary source
│   ├── giv_pts_references.bib     # BibTeX bibliography
│   ├── VO2_Transistor_Supplementary.pdf # Full compiled supplementary PDF
│   └── figures/                   # All SI publication figures (PDF & high-res PNG)
│
├── scripts/                       # Executable simulation & figure generation scripts
│   ├── giv_pts_model.py           # Core stiff electrothermal ROM
│   ├── generate_main_figures.py   # Regenerates Figures 1 to 7
│   ├── generate_SI_figures.py     # Regenerates Figures S1 to S14
│   ├── plot_structural_thermal_figures.py # Regenerates 3D FEA structural thermal figures
│   ├── run_automated_audit_validation.py # Automated 12-test scientific validation suite
│   ├── generate_source_manifest.py # Cryptographic SHA-256 manifest generator
│   ├── resolve_continuous_threshold_modulation.py # Forward ramp extraction
│   └── latency_sensitivity_analysis.py # Gate latency & thermal sensitivity sweeps
│
├── validated_data/                # Verified simulation outputs & FEA exports
│   ├── spatial_fields/            # Authentic COMSOL 3D in-plane & cross-section field exports
│   ├── thermal_calibration/       # Authentic stationary & transient thermal calibrations
│   ├── pulse_results/             # Authoritative pulse transient dynamics and energy
│   ├── ramp_results/              # Continuous forward-ramp threshold crossings
│   └── bypass_sensitivity/        # Interlayer bypass and shunting sensitivity data
│
├── csv_exports/                   # Authentic COMSOL CSV exports matching paper tables
├── transients/                    # Full 0-4 ns numerical ODE solution traces (VG = 0.0 to 2.0 V)
├── hysteresis/                    # Forward-ramp dynamic trajectory datasets
├── robustness/                    # 3D FEA Thermal Boundary Resistance (TBR) parametric sweeps
├── supporting/                    # Supporting calibration & cutline datasets
│
├── comsol/                        # COMSOL Multiphysics 6.3 API scripts & model access
│   ├── Run_Authoritative_Thermal_Calibration.java # Java source for generating & solving 3D model
│   ├── ExportAuthenticCOMSOLSpatialFields.java    # Java source for field exports
│   └── COMSOL_MODEL_ACCESS.md     # Model documentation, checksums, and access instructions
│
└── audit/                         # Scientific audit records & verification manifests
    ├── source_manifest.json       # SHA-256 cryptographic hashes for all key files
    ├── configuration_hashes.csv   # Checksum tables for frozen configs
    ├── parameter_provenance.csv   # Complete parameter provenance table
    ├── configuration_comparison.csv # Configuration comparison across model versions
    ├── issue_tracker.csv          # Comprehensive audit resolution log
    ├── comsol_provenance_audit.md # Detailed COMSOL model provenance audit
    └── validation_results.json    # Machine-readable output of the 12-test validation suite
```

---

## Quick Start & Reproduction

### 1. Prerequisites & Environment Setup

Clone this repository and set up a Python virtual environment:

```bash
git clone https://github.com/INQUIRELAB/Graphene-Mediated-Nanoscale-VO2-Phase-Transition-Switch.git
cd Graphene-Mediated-Nanoscale-VO2-Phase-Transition-Switch

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. One-Click Complete Reproduction

To regenerate all main figures, supplementary figures, 3D FEA structural thermal maps, and execute the complete 12-test scientific audit suite in one command:

```bash
python run_reproduction.py
```

### 3. Individual Figure Generation Commands

- **Main Manuscript Figures (Figures 1–7)**:
  ```bash
  python scripts/generate_main_figures.py
  ```
  Generates `Fig1_Architecture.pdf`, `Fig2_Thermal_Spreading_Maps.pdf`, `Fig3_Thermal_Flux_Vectors.pdf`, `Fig4_Thermal_Pulse_Recovery.pdf`, `Fig5_Constitutive_Electrostatics.pdf`, `Fig6_Phase_Conversion_Thresholds.pdf`, and `Fig7_Transient_Dynamics_Energy.pdf` in `figures/` and `manuscript/figures/`.

- **Supplementary Information Figures (Figures S1–S14)**:
  ```bash
  python scripts/generate_SI_figures.py
  ```
  Generates `FigS1` through `FigS14` in `figures/` and `supplementary/figures/`.

- **3D FEA Structural Thermal Figures (Figures S11, S15, S20–S22)**:
  ```bash
  python scripts/plot_structural_thermal_figures.py
  ```
  Generates authentic 3D spatial field contours, cutlines, and heat flux vector streamplots from native COMSOL exports.

### 4. Running the Automated Audit & Validation Suite

To independently verify numerical self-consistency, energy conservation, thermal plateaus, and cryptographic checksums:

```bash
python scripts/run_automated_audit_validation.py
```

Expected output:
```
===========================================================================
  REV9 RIGOROUS SCIENTIFIC AUDIT & REPRODUCIBILITY VALIDATION SUITE
===========================================================================
[TST-01] Phonon Frequency & Energy Conversion (hf vs hbar*omega) ... PASSED
[TST-02] Poole-Frenkel Coefficient Physical Derivation (epsilon_r = 40 vs 9) ... PASSED
[TST-03] Thermal Calibration Reconciliation (Stationary vs Transient Endpoints) ... PASSED
[TST-04] Cutline Midpoint vs 3D Volume Hotspot Temperature ... PASSED
[TST-05] Steady-State Thermal Plateau Balance (VG = 0.5 V & all gates) ... PASSED
[TST-06] Transient Internal Channel Energy Balance (residual: 0.0075 fJ, rel: 0.11%) ... PASSED
[TST-07] Electrical Load-Line Self-Consistency (V_app = V_D + R_L*I_D) ... PASSED
[TST-08] Full-Window Circuit Energy Conservation (residual < 1.04e-25 J) ... PASSED
[TST-09] Continuous Event Extraction (5.6027 fJ vs 6.57 fJ discrete) ... PASSED
[TST-10] Switching Energy (4.65-5.60 fJ) vs Full-Window Dissipation (99.7-156.0 fJ) ... PASSED
[TST-11] File Hashes, Configuration Integrity & Model Provenance (39 files) ... PASSED
[TST-12] Comprehensive Cross-Table Source Consistency ... PASSED

===========================================================================
AUTOMATED VALIDATION RESULTS: ALL_TESTS_PASSED
Passed: 12 / 12
===========================================================================
```

---

## Compiling Manuscript and Supplementary LaTeX Documents

Precompiled PDFs are provided in `manuscript/VO2_Transistor_Manuscript.pdf` and `supplementary/VO2_Transistor_Supplementary.pdf`.

To recompile from LaTeX source:
```bash
# Manuscript
cd manuscript
pdflatex GIV_PTS_AEM_Manuscript.tex
biber GIV_PTS_AEM_Manuscript
pdflatex GIV_PTS_AEM_Manuscript.tex
pdflatex GIV_PTS_AEM_Manuscript.tex
cd ..

# Supplementary Information
cd supplementary
pdflatex GIV_PTS_AEM_Supporting_Information.tex
biber GIV_PTS_AEM_Supporting_Information
pdflatex GIV_PTS_AEM_Supporting_Information.tex
pdflatex GIV_PTS_AEM_Supporting_Information.tex
cd ..
```

---


```

---

## Acknowledgments & Funding

This material is based upon work supported by the **Air Force Office of Scientific Research (AFOSR)** under award number **FA9550-25-1-0322**.
