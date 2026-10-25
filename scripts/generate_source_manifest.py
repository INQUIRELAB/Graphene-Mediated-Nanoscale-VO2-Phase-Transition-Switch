import os
import json
import hashlib
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def sha256_file(filepath):
    """Computes standard raw byte SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_manifest():
    key_files = [
        "authoritative_model_config.json",
        "README_REPRODUCIBILITY.md",
        "CHANGELOG.md",
        "generate_main_figures.py",
        "generate_SI_figures.py",
        "plot_structural_thermal_figures.py",
        "scripts/giv_pts_model.py",
        "scripts/resolve_continuous_threshold_modulation.py",
        "scripts/build_validated_datasets.py",
        "scripts/generate_verified_figures.py",
        "scripts/generate_audit_metadata_tables.py",
        "scripts/run_automated_audit_validation.py",
        "comsol/Run_Authoritative_Thermal_Calibration.java",
        "comsol/ExportAuthenticCOMSOLSpatialFields.java",
        "comsol/Run_Authoritative_Thermal_Calibration_Model.mph",
        "ExportAuthenticCOMSOLSpatialFields.log",
        "validated_data/spatial_fields/Authoritative_FEA_Thermal_Spatial_Fields.csv",
        "validated_data/spatial_fields/COMSOL_Authentic_Cutlines_Thermal.csv",
        "validated_data/spatial_fields/cutline_x_sample_table.csv",
        "validated_data/spatial_fields/spatial_coordinate_vs_volume_max.csv",
        "validated_data/thermal_calibration/Authoritative_FEA_Thermal_Stationary.csv",
        "validated_data/thermal_calibration/Authoritative_FEA_Thermal_Transient_Gr_OFF_Ablated.csv",
        "validated_data/thermal_calibration/Authoritative_FEA_Thermal_Transient_Gr_ON_Baseline.csv",
        "validated_data/thermal_calibration/thermal_calibration_reconciliation.csv",
        "validated_data/pulse_results/authoritative_pulse_energy_audit.csv",
        "validated_data/ramp_results/continuous_threshold_modulation.csv",
        "validated_data/bypass_sensitivity/graphene_bypass_comprehensive_audit.csv",
        "audit/issue_tracker.csv",
        "audit/numerical_discrepancies.csv",
        "audit/comsol_provenance_audit.md",
        "audit/unresolved_issues.md",
        "reports/Numerical_Reconciliation_Rev9.md",
        "reports/Spatial_Field_Provenance_Rev9.md",
        "reports/Thermal_Calibration_Audit_Rev9.md",
        "reports/ROM_Reproduction_Rev9.md",
        "reports/Professor_Comments_Response_Rev9.md",
        "reports/Independent_Review_Readiness.md",
        "manuscript_revised/main_revised.tex",
        "manuscript_revised/supplementary_revised.tex"
    ]
    
    manifest = {
        "metadata": {
            "title": "Authoritative Reproducibility Package Source Manifest (Rev9)",
            "date": "2026-10-21",
            "hashing_algorithm": "SHA-256 (Raw Binary Bytes)",
            "hashing_standard": "hashlib.sha256(open(f, 'rb').read()).hexdigest()"
        },
        "files": {}
    }
    
    hash_rows = []
    
    for rel_path in key_files:
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            file_hash = sha256_file(full_path)
            file_size = os.path.getsize(full_path)
            manifest["files"][rel_path] = {
                "sha256": file_hash,
                "size_bytes": file_size
            }
            hash_rows.append({
                "Relative_Path": rel_path,
                "SHA256": file_hash,
                "Size_Bytes": file_size,
                "Status": "VERIFIED_PRESENT"
            })
        else:
            manifest["files"][rel_path] = {
                "sha256": None,
                "size_bytes": None,
                "error": "FILE_NOT_FOUND"
            }
            hash_rows.append({
                "Relative_Path": rel_path,
                "SHA256": "FILE_NOT_FOUND",
                "Size_Bytes": 0,
                "Status": "MISSING"
            })
            
    manifest_path = os.path.join(BASE_DIR, "audit", "source_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    csv_path = os.path.join(BASE_DIR, "audit", "configuration_hashes.csv")
    pd.DataFrame(hash_rows).to_csv(csv_path, index=False)
    
    print(f"[SUCCESS] Wrote source manifest to {manifest_path}")
    print(f"[SUCCESS] Wrote configuration hashes CSV to {csv_path}")
    print(f"Authoritative Config SHA-256: {manifest['files']['authoritative_model_config.json']['sha256']}")
    return manifest

if __name__ == "__main__":
    build_manifest()
