"""
Extract District-to-University Higher Education Mobility Flows from official CEAMO ORT Annual Reports.
Builds the Origin-Destination academic migration network:
- origin_district_id (48-54 territories)
- target_university_name (KNU, KSTU, KSMA, OshSU, etc.)
- admitted_count (grant students admitted)
- mean_score (average score of admitted cohort)

Output:
data/04_processed/ort_district_to_university_flows.csv
data/04_processed/ort_district_to_university_flows.parquet
"""

import re
import logging
from pathlib import Path
import pandas as pd
import pdfplumber

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/01_raw/ort_reports")
REFERENCE_DIR = Path("data/03_reference")
PROCESSED_DIR = Path("data/04_processed")

def load_district_resolver():
    ref_df = pd.read_csv(REFERENCE_DIR / "districts_master.csv")
    mapping = {}
    for _, r in ref_df.iterrows():
        did = r['district_id']
        mapping[str(r['name_ru']).lower().strip()] = did
        mapping[str(r['name_kg']).lower().strip()] = did
        for alias in str(r['ort_aliases']).split(','):
            if alias.strip():
                mapping[alias.lower().strip()] = did
    return mapping

def resolve_district(raw_name: str, mapping: dict) -> str:
    if not raw_name:
        return "kg_unknown"
    cleaned = raw_name.lower().replace("г.", "").replace("город", "").replace("район", "").replace("р-н", "").strip()
    cleaned = re.sub(r'[\s\.\,\-]+', ' ', cleaned).strip()
    
    # Direct match
    if cleaned in mapping:
        return mapping[cleaned]
    # Substring search
    for k, v in mapping.items():
        k_c = k.replace("г.", "").replace("город", "").replace("район", "").replace("р-н", "").strip()
        if k_c and (k_c in cleaned or cleaned in k_c):
            return v
    return "kg_unknown"

def extract_uni_flows_year(pdf_path: Path, year: int, resolver: dict):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        start_p = None
        for i in range(40, min(85, num_pages)):
            t = pdf.pages[i].extract_text()
            if t and any(k in t.lower() for k in ['приложение vi', 'приложение 6', 'распределение зачисленных абитуриентов по вузам']):
                start_p = i + 1
                break
        if not start_p:
            return records
            
        current_region = None
        current_district = None
        
        for p_idx in range(start_p, min(start_p + 35, num_pages)):
            page = pdf.pages[p_idx]
            text = page.extract_text()
            if not text or any(k in text.lower() for k in ['приложение vii', 'приложение 7', 'рейтинг вузов']):
                break
                
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for l in lines:
                if 'область' in l.lower() and len(l) < 45:
                    current_region = l
                elif any(k in l.lower() for k in ['район', 'г.', 'город']) and len(l) < 55:
                    current_district = l
                    
                # Match line: admitted_count, mean_score, university
                m = re.match(r'^(\d{1,4})\s+([\d\.]+)\s+(.+)$', l)
                if m:
                    cnt = int(m.group(1))
                    mean_sc = float(m.group(2))
                    uni_name = m.group(3).strip()
                    if 100 <= mean_sc <= 245 and len(uni_name) > 3 and not uni_name.isdigit():
                        did = resolve_district(current_district or "", resolver)
                        records.append({
                            'year': year,
                            'district_raw': current_district or 'Unknown',
                            'district_id': did,
                            'region_raw': current_region or 'Unknown',
                            'university_name': uni_name,
                            'admitted_count': cnt,
                            'mean_score': mean_sc
                        })
    return records

def process_all_university_flows():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    resolver = load_district_resolver()
    all_recs = []
    
    # Process available years with university flow tables (2015-2025)
    for y in range(2015, 2026):
        p = RAW_DIR / f"ort_report_{y}.pdf"
        if not p.exists():
            continue
        try:
            recs = extract_uni_flows_year(p, y, resolver)
            all_recs.extend(recs)
            logger.info(f"Year {y}: extracted {len(recs)} university mobility edges")
        except Exception as e:
            logger.error(f"Error extracting flows for {y}: {e}")
            
    df = pd.DataFrame(all_recs)
    if not df.empty:
        df = df.drop_duplicates(subset=["year", "district_raw", "university_name"])
        df = df.sort_values(by=["year", "district_id", "admitted_count"], ascending=[True, True, False]).reset_index(drop=True)
        
        out_csv = PROCESSED_DIR / "ort_district_to_university_flows.csv"
        out_parquet = PROCESSED_DIR / "ort_district_to_university_flows.parquet"
        
        df.to_csv(out_csv, index=False)
        df.to_parquet(out_parquet, index=False)
        
        logger.info("==================================================")
        logger.info("ACADEMIC MOBILITY MATRIX ASSEMBLED:")
        logger.info(f"Total Edges (Rows): {len(df)}")
        logger.info(f"Years: {df['year'].nunique()} ({df['year'].min()}-{df['year'].max()})")
        logger.info(f"Unique Universities: {df['university_name'].nunique()}")
        logger.info(f"Total Grant Students Tracked: {df['admitted_count'].sum():,}")
        logger.info(f"Saved to: {out_csv} and {out_parquet}")
        logger.info("==================================================")
    return df

if __name__ == "__main__":
    process_all_university_flows()
