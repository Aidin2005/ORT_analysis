"""
Final compilation of the 100% complete EduAnalytics-KG Spatio-Temporal Dataset.
Merges:
- 20 complete years of ORT testing (2006-2025, no gaps)
- Socioeconomic feature matrix (X) from NatStatCom
- Output:
  data/04_processed/ort_complete_panel_2006_2025.csv
  data/04_processed/ort_complete_panel_2006_2025.parquet
"""

import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXTRACTED_DIR = Path("data/02_extracted")
REFERENCE_DIR = Path("data/03_reference")
PROCESSED_DIR = Path("data/04_processed")

def assemble_complete_dataset():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load all year district files
    files = sorted(EXTRACTED_DIR.glob("ort_*_districts.csv"))
    logger.info(f"Found {len(files)} annual extracted files in {EXTRACTED_DIR}")
    
    all_dfs = []
    for f in files:
        df_y = pd.read_csv(f)
        all_dfs.append(df_y)
        
    district_df = pd.concat(all_dfs, ignore_index=True)
    district_df = district_df.drop_duplicates(subset=["year", "district_id"])
    
    # 2. Load Socioeconomic features
    se_df = pd.read_csv(REFERENCE_DIR / "socioeconomic_indicators.csv")
    
    # 3. Merge by (region_id, year)
    merged_df = pd.merge(
        district_df,
        se_df,
        on=["region_id", "year"],
        how="left"
    )
    
    # Sort logically
    merged_df = merged_df.sort_values(by=["year", "region_id", "district_id"]).reset_index(drop=True)
    
    # 4. Save to CSV and Parquet
    out_csv = PROCESSED_DIR / "ort_complete_panel_2006_2025.csv"
    out_parquet = PROCESSED_DIR / "ort_complete_panel_2006_2025.parquet"
    
    merged_df.to_csv(out_csv, index=False)
    merged_df.to_parquet(out_parquet, index=False)
    
    logger.info("==================================================")
    logger.info(f"100% COMPLETE DATASET ASSEMBLED:")
    logger.info(f"Total Rows: {len(merged_df)}")
    logger.info(f"Total Columns: {len(merged_df.columns)}")
    logger.info(f"Years: {sorted(merged_df['year'].unique().tolist())} (Total: {merged_df['year'].nunique()} years)")
    logger.info(f"Districts: {merged_df['district_id'].nunique()} territories")
    logger.info(f"Columns: {list(merged_df.columns)}")
    logger.info(f"Saved to: {out_csv} and {out_parquet}")
    logger.info("==================================================")
    
    # 5. Build Complete Regional Summary Panel
    reg_df = merged_df.groupby(["year", "region_id", "region_name"]).agg(
        participants_total=("participants_count", "sum"),
        mean_score_weighted=("mean_score", lambda x: round((x * merged_df.loc[x.index, "participants_count"]).sum() / merged_df.loc[x.index, "participants_count"].sum(), 2)),
        grant_admitted_total=("grant_admitted_count", "sum"),
        avg_monthly_salary_som=("avg_monthly_salary_som", "first"),
        pupil_teacher_ratio=("pupil_teacher_ratio", "first"),
        poverty_rate_pct=("poverty_rate_pct", "first"),
        teachers_higher_ed_pct=("teachers_higher_ed_pct", "first")
    ).reset_index()
    
    reg_csv = PROCESSED_DIR / "ort_complete_regional_panel_2006_2025.csv"
    reg_df.to_csv(reg_csv, index=False)
    logger.info(f"✓ Saved complete regional panel: {len(reg_df)} rows to {reg_csv}")

if __name__ == "__main__":
    assemble_complete_dataset()
