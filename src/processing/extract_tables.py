"""
Extractor for ORT analytical tables from official PDF reports.
Extracts:
1. Regional summaries (Oblasts + Bishkek + Osh)
2. District summaries (Districts and towns)
3. Subject tests summary
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_PDF_DIR = Path("data/01_raw/ort_reports")
EXTRACTED_DIR = Path("data/02_extracted")
REFERENCE_DIR = Path("data/03_reference")

def load_district_reference() -> pd.DataFrame:
    """Load canonical districts and aliases."""
    ref_file = REFERENCE_DIR / "districts_master.csv"
    if ref_file.exists():
        return pd.read_csv(ref_file)
    return pd.DataFrame()

def match_district(raw_name: str, ref_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Fuzzy / alias match for raw district or region name."""
    if ref_df.empty or not raw_name:
        return None
        
    cleaned = raw_name.strip().lower()
    cleaned = re.sub(r'[\d\.\,\-\:\;]', ' ', cleaned).strip()
    
    for _, row in ref_df.iterrows():
        # Check canonical names
        if cleaned == str(row['name_ru']).lower() or cleaned == str(row['name_kg']).lower():
            return row.to_dict()
            
        # Check aliases
        aliases = [a.strip().lower() for a in str(row['ort_aliases']).split(',')]
        for alias in aliases:
            if alias and (alias == cleaned or alias in cleaned or cleaned in alias):
                return row.to_dict()
                
    return None

def extract_tables_from_pdf(pdf_path: Path) -> List[List[List[str]]]:
    """Extract raw table matrices using pdfplumber."""
    import pdfplumber
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        logger.info(f"Scanning {pdf_path.name} ({num_pages} pages)...")
        
        for p_idx, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables()
                for t in tables:
                    if t and len(t) >= 3: # Table with at least header + 2 rows
                        all_tables.append({
                            "page": p_idx + 1,
                            "table": t
                        })
            except Exception as e:
                logger.debug(f"Error on page {p_idx+1}: {e}")
                
    return all_tables

def clean_number(val: Any) -> Optional[float]:
    """Clean and parse numerical string (handles Russian comma decimal, spaces)."""
    if val is None:
        return None
    s = str(val).strip().replace(',', '.').replace(' ', '')
    # Match float or int
    match = re.search(r'[-+]?\d*\.?\d+', s)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None

def identify_and_parse_regional_table(tables: List[Dict[str, Any]], year: int, ref_df: pd.DataFrame) -> pd.DataFrame:
    """Identify regional/district tables by header and row keywords."""
    records = []
    
    for item in tables:
        t = item["table"]
        page_num = item["page"]
        
        # Check header rows
        header_text = " ".join([str(c) for row in t[:3] for c in row if c]).lower()
        
        is_district_table = any(k in header_text for k in ["район", "регион", "област", "территори"]) and \
                            any(k in header_text for k in ["балл", "средн", "участник", "чел", "кол-во", "%"])
                            
        if not is_district_table:
            continue
            
        logger.info(f"Found candidate district/regional table on page {page_num} for year {year}")
        
        # Parse data rows
        for row in t[1:]:
            if not row or not any(row):
                continue
                
            first_col = str(row[0]).strip() if row[0] else ""
            if not first_col or first_col.lower() in ["всего", "итого", "среднее", "кыргызстан", "республика"]:
                continue
                
            matched = match_district(first_col, ref_df)
            if matched:
                # Extract numbers from subsequent columns
                nums = [clean_number(c) for c in row[1:] if clean_number(c) is not None]
                
                # Typical columns: participants, mean_score, percent_above_threshold
                participants = None
                mean_score = None
                pass_rate = None
                
                for n in nums:
                    if n > 1000 and participants is None:
                        participants = int(n)
                    elif 80.0 <= n <= 245.0 and mean_score is None:
                        mean_score = n
                    elif 0.0 <= n <= 100.0 and pass_rate is None and n != mean_score:
                        pass_rate = n
                        
                records.append({
                    "year": year,
                    "district_id": matched["district_id"],
                    "district_name": matched["name_ru"],
                    "region_id": matched["region_id"],
                    "region_name": matched["region_name_ru"],
                    "soato_code": matched["soato_code"],
                    "raw_source_name": first_col,
                    "participants_count": participants,
                    "mean_score": mean_score,
                    "pass_rate_pct": pass_rate,
                    "source_page": page_num
                })
                
    if records:
        df = pd.DataFrame(records)
        df = df.drop_duplicates(subset=["year", "district_id"])
        return df
    return pd.DataFrame()

def process_year(year: int):
    """Process a single year's report."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = RAW_PDF_DIR / f"ort_report_{year}.pdf"
    if not pdf_path.exists():
        logger.warning(f"PDF not found for year {year}: {pdf_path}")
        return
        
    ref_df = load_district_reference()
    tables = extract_tables_from_pdf(pdf_path)
    logger.info(f"Year {year}: extracted {len(tables)} candidate tables.")
    
    df_reg = identify_and_parse_regional_table(tables, year, ref_df)
    if not df_reg.empty:
        out_path = EXTRACTED_DIR / f"ort_{year}_district_raw.csv"
        df_reg.to_csv(out_path, index=False)
        logger.info(f"✓ Saved {len(df_reg)} district records to {out_path}")
    else:
        logger.warning(f"No district records matched for year {year}")

if __name__ == "__main__":
    import sys
    year_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    process_year(year_arg)
