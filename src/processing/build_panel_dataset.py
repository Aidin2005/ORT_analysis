"""
Assembly script for EduAnalytics-KG Spatial-Temporal Panel Dataset.
Merges:
1. Extracted ORT district test metrics (2006-2025)
2. Master district reference registry with SOATO codes
3. Generates data quality metrics and final parquet/csv outputs
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXTRACTED_DIR = Path("data/02_extracted")
REFERENCE_DIR = Path("data/03_reference")
PROCESSED_DIR = Path("data/04_processed")

def load_master_districts() -> pd.DataFrame:
    """Load canonical districts master table."""
    master_file = REFERENCE_DIR / "districts_master.csv"
    if not master_file.exists():
        raise FileNotFoundError(f"Master file not found: {master_file}")
    return pd.read_csv(master_file)

def assemble_panel() -> pd.DataFrame:
    """Read all extracted year files and compile into panel dataset."""
    raw_files = sorted(EXTRACTED_DIR.glob("ort_*_district_raw.csv"))
    if not raw_files:
        logger.warning("No extracted files found in data/02_extracted/")
        return pd.DataFrame()

    dfs = []
    for f in raw_files:
        logger.info(f"Loading {f.name}...")
        df_year = pd.read_csv(f)
        dfs.append(df_year)

    panel_df = pd.concat(dfs, ignore_index=True)
    
    # Merge with master districts to guarantee canonical attributes
    master_df = load_master_districts()
    master_cols = ["district_id", "name_ru", "name_kg", "region_id", "region_name_ru", "soato_code"]
    
    merged = pd.merge(
        panel_df.drop(columns=[c for c in master_cols if c in panel_df.columns and c != "district_id"], errors='ignore'),
        master_df[master_cols],
        on="district_id",
        how="left"
    )

    # Sort logically by year and district
    merged = merged.sort_values(by=["year", "region_id", "district_id"]).reset_index(drop=True)
    return merged

def validate_panel(df: pd.DataFrame) -> dict:
    """Validate panel dataset consistency and completeness."""
    if df.empty:
        return {"status": "empty", "rows": 0}

    total_rows = len(df)
    unique_years = sorted(df["year"].unique().tolist())
    unique_districts = df["district_id"].nunique()

    # Check key duplicates
    duplicates = df.duplicated(subset=["year", "district_id"]).sum()
    
    # Scores validation
    valid_scores = df["mean_score"].dropna()
    score_min = float(valid_scores.min()) if not valid_scores.empty else None
    score_max = float(valid_scores.max()) if not valid_scores.empty else None
    score_mean = float(valid_scores.mean()) if not valid_scores.empty else None

    # Missing values
    missing_scores = int(df["mean_score"].isna().sum())
    missing_participants = int(df["participants_count"].isna().sum()) if "participants_count" in df.columns else total_rows

    report = {
        "status": "valid" if duplicates == 0 else "duplicates_detected",
        "total_records": total_rows,
        "years_covered": unique_years,
        "districts_count": unique_districts,
        "duplicates": int(duplicates),
        "score_stats": {
            "min": score_min,
            "max": score_max,
            "mean": score_mean,
            "missing_count": missing_scores
        },
        "missing_participants": missing_participants
    }
    return report

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_panel = assemble_panel()
    
    if df_panel.empty:
        logger.info("Panel is currently empty. Run table extraction first.")
        return

    report = validate_panel(df_panel)
    logger.info(f"Validation summary:\n{report}")

    # Save to CSV and Parquet
    csv_out = PROCESSED_DIR / "ort_district_panel_2006_2025.csv"
    parquet_out = PROCESSED_DIR / "ort_district_panel_2006_2025.parquet"
    
    df_panel.to_csv(csv_out, index=False)
    df_panel.to_parquet(parquet_out, index=False)
    
    logger.info(f"✓ Saved panel dataset to {csv_out} and {parquet_out}")

if __name__ == "__main__":
    main()
