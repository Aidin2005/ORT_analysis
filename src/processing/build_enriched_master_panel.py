"""
Build the enriched multi-level EduAnalytics-KG master panel.
Merges:
1. Base district-year ORT panel (889 rows, 2006-2025)
2. NatStatCom official education panel (11th grade cohort size, schools, students, teachers)
3. ISUO school infrastructure stats (2,386 schools aggregated by district)
4. Computes ORT Participation Rate and Infrastructure Ratios

Outputs:
data/04_processed/ort_complete_panel_enriched_2006_2025.csv
data/04_processed/ort_complete_panel_enriched_2006_2025.parquet
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/04_processed")

def build_enriched_master_panel():
    base_file = PROCESSED_DIR / "ort_complete_panel_2006_2025.csv"
    natstat_file = PROCESSED_DIR / "natstatcom_regional_education_panel_2006_2025.csv"
    school_stats_file = PROCESSED_DIR / "district_school_infrastructure_stats.csv"
    
    if not base_file.exists():
        logger.error(f"Base panel {base_file} does not exist.")
        return
        
    logger.info("Loading datasets...")
    base_df = pd.read_csv(base_file)
    natstat_df = pd.read_csv(natstat_file)
    school_stats_df = pd.read_csv(school_stats_file)
    
    logger.info(f"Base panel shape: {base_df.shape}")
    logger.info(f"NatStatCom panel shape: {natstat_df.shape}")
    logger.info(f"School infrastructure stats shape: {school_stats_df.shape}")
    
    # 1. Merge NatStatCom regional time-series features
    enriched = pd.merge(
        base_df,
        natstat_df,
        on=["region_id", "year"],
        how="left"
    )
    
    # 2. Merge district-level school infrastructure features
    # Select key infrastructure columns
    infra_cols = [
        "district_id",
        "schools_total_count",
        "private_schools_count",
        "private_schools_share",
        "specialized_schools_count",
        "specialized_schools_share",
        "boarding_schools_count"
    ]
    school_sub = school_stats_df[infra_cols].drop_duplicates(subset=["district_id"])
    
    enriched = pd.merge(
        enriched,
        school_sub,
        on="district_id",
        how="left"
    )
    
    # 3. Compute domain-specific indicators
    # Regional level ORT participation rate = participants_count / cohort_graduates_11th
    # For districts, compute participation relative to cohort estimate or regional cohort share
    reg_totals = enriched.groupby(["region_id", "year"])["participants_count"].transform("sum")
    enriched["reg_participants_total"] = reg_totals
    enriched["district_share_in_region_participants"] = (enriched["participants_count"] / enriched["reg_participants_total"]).round(4)
    
    # District estimated 11th grade cohort size
    enriched["district_est_graduates_cohort"] = (enriched["cohort_graduates_11th"] * enriched["district_share_in_region_participants"]).round(1)
    
    # Regional ORT coverage rate (% of high school graduates who take ORT)
    enriched["regional_ort_coverage_rate_pct"] = (enriched["reg_participants_total"] / enriched["cohort_graduates_11th"] * 100).round(2)
    # Clip to realistic percentage (cap at 100% in case of private/past-year graduates taking test)
    enriched["regional_ort_coverage_rate_pct"] = enriched["regional_ort_coverage_rate_pct"].clip(upper=100.0)
    
    # Student-to-school density (students per school in region)
    enriched["students_per_school_reg"] = (enriched["stat_students_total"] / enriched["stat_schools_total"]).round(1)
    
    # Female teacher share / density
    enriched["female_teachers_per_school_reg"] = (enriched["stat_female_teachers_total"] / enriched["stat_schools_total"]).round(1)
    
    # Sort logically
    enriched = enriched.sort_values(by=["year", "region_id", "district_id"]).reset_index(drop=True)
    
    # Save enriched panel
    out_csv = PROCESSED_DIR / "ort_complete_panel_enriched_2006_2025.csv"
    out_parquet = PROCESSED_DIR / "ort_complete_panel_enriched_2006_2025.parquet"
    
    enriched.to_csv(out_csv, index=False)
    enriched.to_parquet(out_parquet, index=False)
    
    logger.info("==================================================")
    logger.info("ENRICHED MASTER DATASET ASSEMBLED:")
    logger.info(f"Total Rows: {len(enriched)}")
    logger.info(f"Total Columns: {len(enriched.columns)} (expanded from {base_df.shape[1]})")
    logger.info(f"Districts: {enriched['district_id'].nunique()}")
    logger.info(f"Years: {enriched['year'].nunique()} (2006-2025)")
    logger.info(f"New Feature Columns Added:")
    for col in enriched.columns:
        if col not in base_df.columns:
            logger.info(f"  + {col}")
    logger.info(f"Saved to: {out_csv} and {out_parquet}")
    logger.info("==================================================")
    return enriched

if __name__ == "__main__":
    build_enriched_master_panel()
