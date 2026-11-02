"""
Unified extraction pipeline for EduAnalytics-KG.
Extracts:
1. District-level panel: ort_districts_2006_2025.csv
2. Region-level panel: ort_regions_2006_2025.csv
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import pdfplumber

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_PDF_DIR = Path("data/01_raw/ort_reports")
EXTRACTED_DIR = Path("data/02_extracted")
REFERENCE_DIR = Path("data/03_reference")
PROCESSED_DIR = Path("data/04_processed")

def clean_num(val: Any) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip().replace(',', '.').replace(' ', '')
    m = re.search(r'[-+]?\d*\.?\d+', s)
    if m:
        try:
            return float(m.group(0))
        except ValueError:
            return None
    return None

def clean_name(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def load_master_districts() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_DIR / "districts_master.csv")

def match_district_row(name: str, master_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    cleaned = clean_name(name).lower()
    if not cleaned or any(k in cleaned for k in ["всего", "итого", "кыргызстан", "республика", "район/ город", "выпускник", "школ", "категори", "вуз"]):
        return None
        
    for _, row in master_df.iterrows():
        # Match canonical name
        if str(row["name_ru"]).lower() in cleaned or cleaned in str(row["name_ru"]).lower():
            return row.to_dict()
            
        # Match aliases
        aliases = [a.strip().lower() for a in str(row["ort_aliases"]).split(",") if a.strip()]
        for a in aliases:
            if a in cleaned or cleaned in a:
                return row.to_dict()
                
    return None

def extract_year_districts(pdf_path: Path, year: int, master_df: pd.DataFrame) -> List[Dict[str, Any]]:
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t in tables:
                if not t or len(t) < 4:
                    continue
                    
                # Check if this table has district data
                # Usually columns: [район/город, участников, ср.балл, >110, грант_кол, грант_балл, контр_кол, контр_балл]
                for row in t:
                    if not row or not row[0]:
                        continue
                    first_cell = clean_name(row[0])
                    matched = match_district_row(first_cell, master_df)
                    if not matched:
                        continue
                        
                    # Extract numeric cells
                    nums = [clean_num(c) for c in row[1:] if clean_num(c) is not None]
                    if len(nums) < 2:
                        continue
                        
                    # Extract standard fields
                    participants = int(nums[0]) if len(nums) > 0 and nums[0] > 0 else None
                    mean_score = float(nums[1]) if len(nums) > 1 and 80 <= nums[1] <= 180 else None
                    passed_110 = int(nums[2]) if len(nums) > 2 and nums[2] >= 0 else None
                    
                    grant_n = int(nums[3]) if len(nums) > 3 and nums[3] >= 0 else None
                    grant_mean = float(nums[4]) if len(nums) > 4 and 100 <= nums[4] <= 245 else None
                    contract_n = int(nums[5]) if len(nums) > 5 and nums[5] >= 0 else None
                    contract_mean = float(nums[6]) if len(nums) > 6 and 100 <= nums[6] <= 245 else None
                    
                    if participants and passed_110 is not None and passed_110 <= participants:
                        pass_rate = round(passed_110 / participants * 100, 2)
                    else:
                        pass_rate = None
                    
                    if participants and mean_score:
                        records.append({
                            "year": year,
                            "district_id": matched["district_id"],
                            "district_name": matched["name_ru"],
                            "region_id": matched["region_id"],
                            "region_name": matched["region_name_ru"],
                            "soato_code": matched["soato_code"],
                            "raw_source_name": first_cell,
                            "participants_count": participants,
                            "mean_score": mean_score,
                            "passed_110_count": passed_110,
                            "pass_rate_pct": pass_rate,
                            "grant_admitted_count": grant_n,
                            "grant_mean_score": grant_mean,
                            "contract_admitted_count": contract_n,
                            "contract_mean_score": contract_mean,
                            "source_page": p_idx + 1
                        })
                        
    return records

def run_extraction():
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    master_df = load_master_districts()
    pdf_files = sorted(RAW_PDF_DIR.glob("ort_report_*.pdf"))
    
    all_district_records = []
    
    for pdf_p in pdf_files:
        m = re.search(r'ort_report_(\d{4})\.pdf', pdf_p.name)
        if not m:
            continue
        year = int(m.group(1))
        logger.info(f"Processing {pdf_p.name} (Year {year})...")
        
        try:
            records = extract_year_districts(pdf_p, year, master_df)
            if records:
                # Deduplicate by district_id
                df_y = pd.DataFrame(records).drop_duplicates(subset=["district_id"])
                logger.info(f"  ✓ Extracted {len(df_y)} districts for year {year}")
                df_y.to_csv(EXTRACTED_DIR / f"ort_{year}_districts.csv", index=False)
                all_district_records.extend(df_y.to_dict(orient="records"))
            else:
                logger.warning(f"  ✗ No district records extracted for year {year}")
        except Exception as e:
            logger.error(f"  Error processing year {year}: {e}")

    # Build final District Panel
    if all_district_records:
        panel_df = pd.DataFrame(all_district_records)
        panel_df = panel_df.drop_duplicates(subset=["year", "district_id"])
        panel_df = panel_df.sort_values(by=["year", "region_id", "district_id"]).reset_index(drop=True)
        
        out_csv = PROCESSED_DIR / "ort_district_panel_2006_2025.csv"
        out_parquet = PROCESSED_DIR / "ort_district_panel_2006_2025.parquet"
        
        panel_df.to_csv(out_csv, index=False)
        panel_df.to_parquet(out_parquet, index=False)
        
        logger.info(f"\n==========================================")
        logger.info(f"DISTRICT PANEL READY: {len(panel_df)} total records")
        logger.info(f"Years: {sorted(panel_df['year'].unique().tolist())}")
        logger.info(f"Districts: {panel_df['district_id'].nunique()}")
        logger.info(f"Saved to: {out_csv} and {out_parquet}")
        logger.info(f"==========================================")

        # Build Regional Aggregation Panel
        reg_df = panel_df.groupby(["year", "region_id", "region_name"]).agg(
            participants_total=("participants_count", "sum"),
            mean_score_weighted=("mean_score", lambda x: round((x * panel_df.loc[x.index, "participants_count"]).sum() / panel_df.loc[x.index, "participants_count"].sum(), 2)),
            passed_110_total=("passed_110_count", "sum"),
            grant_admitted_total=("grant_admitted_count", "sum"),
            contract_admitted_total=("contract_admitted_count", "sum")
        ).reset_index()
        
        reg_df["pass_rate_pct"] = (reg_df["passed_110_total"] / reg_df["participants_total"] * 100).round(2)
        
        reg_csv = PROCESSED_DIR / "ort_regional_panel_2006_2025.csv"
        reg_parquet = PROCESSED_DIR / "ort_regional_panel_2006_2025.parquet"
        
        reg_df.to_csv(reg_csv, index=False)
        reg_df.to_parquet(reg_parquet, index=False)
        logger.info(f"REGIONAL PANEL READY: {len(reg_df)} records saved to {reg_csv}")

if __name__ == "__main__":
    run_extraction()
