# COMSOL Multiphysics 6.3 Model Access & Verification

This directory contains the authentic Java API scripts to build, solve, and export the 3D finite-element thermal model of the GIV-PTS device.

## Model Summary
- **Software**: COMSOL Multiphysics 6.3 (Build 290)
- **Geometry**: $50\times 50\times 5\text{ nm}^3$ $\mathrm{VO_2}$ channel, $1\text{ nm}$ monolayer graphene equivalent sheet ($k=201\text{ W/(m}\cdot\text{K)}$), $5\text{ nm}$ $\mathrm{HfO_2}$, $100\text{ nm}$ $\mathrm{SiO_2}$.
- **Input Power**: $1.00\ \mu\text{W}$ volumetric heat source ($Q_0 = 8.00\times 10^{16}\text{ W/m}^3$).
- **Exported Field Outputs**: Full in-plane ($z = 2.5\text{ nm}$) and cross-sectional ($y = 25\text{ nm}$) 3D meshes saved in `validated_data/spatial_fields/` and `csv_exports/`.

## Script Index
1. `Run_Authoritative_Thermal_Calibration.java`: Generates the complete 3D FEA geometry, applies mesh boundary conditions, solves stationary and transient studies, and exports calibration curves.
2. `ExportAuthenticCOMSOLSpatialFields.java`: Extracts authentic temperature and heat-flux vector fields across the cutlines and cutplanes.
3. `ExportAuthenticCOMSOLSpatialFields.log`: Verifiable execution log documenting solver convergence, build environment, and solution metrics.

## Pre-Solved Binary Model (.mph)
The pre-solved full solution file (`Run_Authoritative_Thermal_Calibration_Model.mph`, 217.6 MB) exceeds GitHub's 100 MB single-file limit. 
- **Checksum (SHA-256)**: `ff87e8e219185981e5881e21cd16b6c304bc6ebb82ca8ec41b05c500f126c077`
- **Access**: Available as a release asset in the repository's [GitHub Releases](https://github.com/INQUIRELAB/Graphene-Mediated-Nanoscale-VO2-Phase-Transition-Switch/releases) or via Zenodo DOI.
