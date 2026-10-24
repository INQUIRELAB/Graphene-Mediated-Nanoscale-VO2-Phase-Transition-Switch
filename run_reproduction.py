#!/usr/bin/env python3
"""run_reproduction.py

Master One-Click Reproduction Pipeline for:
'Graphene-Mediated Electrothermal Control of Phase-Transition Dynamics in Nanoscale VO2 Devices'
INQUIRE Lab, University of Oklahoma & Oklahoma State University

This script:
1. Validates environment dependencies
2. Regenerates all 7 Primary Manuscript Figures (PDF & PNG)
3. Regenerates all Supplementary Figures (Figures S1-S14, S20-S22)
4. Regenerates 3D FEA Structural Thermal Figures from authentic COMSOL solutions
5. Synchronizes source manifests and cryptographic SHA-256 hashes
6. Executes the 12-test automated scientific audit and validation suite
"""

import os
import sys
import subprocess
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

def print_header(title):
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)

def run_script(script_path, description):
    print(f"\n[*] {description}...")
    t0 = time.time()
    res = subprocess.run([sys.executable, script_path], cwd=ROOT_DIR, capture_output=True, text=True)
    dt = time.time() - t0
    if res.returncode == 0:
        print(f"  [SUCCESS] Completed in {dt:.2f}s")
        if res.stdout.strip():
            # Print last 3 lines of output
            lines = [l for l in res.stdout.strip().splitlines() if l.strip()]
            for l in lines[-3:]:
                print(f"    {l}")
    else:
        print(f"  [FAILED] Exit code {res.returncode}")
        print("STDERR:")
        print(res.stderr)
        print("STDOUT:")
        print(res.stdout)
        sys.exit(res.returncode)

def main():
    print_header("GIV-PTS VO2 PHASE-TRANSITION SWITCH: REPRODUCTION PIPELINE")
    print(f"Project Root: {ROOT_DIR}")
    print(f"Python Executable: {sys.executable} (version {sys.version.split()[0]})")

    # Step 1: Main Figures
    run_script(os.path.join(ROOT_DIR, "scripts", "generate_main_figures.py"), "Regenerating Main Figures (Figs 1-7)")

    # Step 2: SI Figures
    run_script(os.path.join(ROOT_DIR, "scripts", "generate_SI_figures.py"), "Regenerating Supplementary Figures (Figs S1-S14)")

    # Step 3: Structural Thermal Figures
    run_script(os.path.join(ROOT_DIR, "scripts", "plot_structural_thermal_figures.py"), "Regenerating 3D FEA Structural Thermal Maps (Figs S11, S15, S20-S22)")

    # Step 4: Manifest Refresh
    run_script(os.path.join(ROOT_DIR, "scripts", "generate_source_manifest.py"), "Refreshing Cryptographic SHA-256 Source Manifest")

    # Step 5: Validation Suite
    print_header("RUNNING 12-TEST SCIENTIFIC AUDIT & VALIDATION SUITE")
    run_script(os.path.join(ROOT_DIR, "scripts", "run_automated_audit_validation.py"), "Executing Audit Verification Suite")

    print_header("REPRODUCTION AND VERIFICATION COMPLETED SUCCESSFULLY!")
    print("All figures regenerated in: figures/, manuscript/figures/, supplementary/figures/")
    print("All 12 audit and reproducibility tests PASSED.")

if __name__ == "__main__":
    main()
