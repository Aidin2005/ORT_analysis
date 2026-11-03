"""
Process and clean the official ISUO / Open Data Kyrgyzstan school registry (2,386 schools).
Standardizes district and region names, matches to canonical district_ids,
extracts school categories (Gymnasiums, Lyceums, Private, Public),
and aggregates district-level school infrastructure statistics.
"""

import re
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_FILE = Path("data/01_raw/schools_registry_data_gov_kg.xlsx")
REF_FILE = Path("data/03_reference/districts_master.csv")
PROCESSED_DIR = Path("data/04_processed")

DISTRICT_MAPPING = {
    'октябрьский р-н': 'kg_bishkek_oktyabr',
    'первомайский р-н': 'kg_bishkek_pervomay',
    'свердловский р-н': 'kg_bishkek_sverdlov',
    'ленинский р-н': 'kg_bishkek_lenin',
    'г.бишкек': 'kg_bishkek_lenin',
    'г.ош': 'kg_osh_city',
    'ыссык-атинский р-н': 'kg_chuy_yssyk_ata',
    'кара-буринский р-н': 'kg_talas_aitmatov',
    'базар-курганский р-н': 'kg_jalalabad_bazar_korgon',
    'г.баткен': 'kg_batken_batken',
    'г.джалал-абад': 'kg_jalalabad_city',
    'г.нарын': 'kg_naryn_city',
    'г.талас': 'kg_talas_city',
    'г.токмок': 'kg_chuy_tokmok',
    'г.каракол': 'kg_issyk_kul_karakol',
    'г.балыкчы': 'kg_issyk_kul_balykchy',
    'г.кызыл-кия': 'kg_batken_kyzyl_kiya',
    'г.сулюкта': 'kg_batken_sulyukta',
    'г.майлуу-суу': 'kg_jalalabad_mailuu_suu',
    'г.таш-кумыр': 'kg_jalalabad_tash_kumyr',
    'г.кара-куль': 'kg_jalalabad_kara_kul'
}

def clean_key(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = s.lower().replace('р-н', 'район').replace('обл.', 'область').strip()
    s = re.sub(r'[\s\.\,\-]+', ' ', s).strip()
    return s

def build_district_resolver(ref_df: pd.DataFrame):
    mapping = dict(DISTRICT_MAPPING)
    for _, r in ref_df.iterrows():
        did = r['district_id']
        mapping[clean_key(str(r['name_ru']))] = did
        mapping[clean_key(str(r['name_kg']))] = did
        aliases = str(r['ort_aliases']).split(',')
        for a in aliases:
            if a.strip():
                mapping[clean_key(a)] = did
    return mapping

def process_schools_registry():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    if not RAW_FILE.exists():
        logger.error(f"Raw file {RAW_FILE} does not exist.")
        return
        
    logger.info(f"Loading raw school registry from {RAW_FILE}...")
    raw_df = pd.read_excel(RAW_FILE)
    
    # Header is at row index 0
    df = raw_df.iloc[1:].copy()
    df.columns = ['num', 'school_name', 'okpo', 'property_form', 'region_raw', 'district_raw']
    df['school_name'] = df['school_name'].astype(str).str.strip()
    df['property_form'] = df['property_form'].astype(str).str.strip()
    df['region_raw'] = df['region_raw'].astype(str).str.strip()
    df['district_raw'] = df['district_raw'].astype(str).str.strip()
    
    ref_df = pd.read_csv(REF_FILE)
    resolver = build_district_resolver(ref_df)
    
    # Assign district_id
    district_ids = []
    region_ids = []
    for _, row in df.iterrows():
        d_raw = row['district_raw'].lower().strip()
        matched_id = DISTRICT_MAPPING.get(d_raw)
        if not matched_id:
            cleaned = clean_key(d_raw)
            matched_id = resolver.get(cleaned)
            if not matched_id:
                for k, v in resolver.items():
                    if k in cleaned or cleaned in k:
                        matched_id = v
                        break
                        
        if not matched_id:
            # Fallback by region
            matched_id = 'kg_unknown'
            
        district_ids.append(matched_id)
        
        # Determine region_id from district_id
        if matched_id.startswith('kg_'):
            parts = matched_id.split('_')
            reg_id = f"kg_{parts[1]}"
            if len(parts) >= 3 and parts[1] == 'issyk' and parts[2] == 'kul':
                reg_id = "kg_issyk_kul"
            elif len(parts) >= 3 and parts[1] == 'osh' and parts[2] == 'city':
                reg_id = "kg_osh_city"
        else:
            reg_id = 'kg_unknown'
        region_ids.append(reg_id)
        
    df['district_id'] = district_ids
    df['region_id'] = region_ids
    
    # Categorization
    df['is_private'] = df['property_form'].str.lower().str.contains('частная|ооо|зао|общество').astype(int)
    
    def get_category(name):
        n = name.lower()
        if 'гимнази' in n or 'лицей' in n:
            return 'Gymnasium / Lyceum'
        elif 'учебно-воспитательный комплекс' in n or 'увк' in n:
            return 'Educational Complex (UVK)'
        elif 'интернат' in n:
            return 'Boarding School'
        elif 'вечерн' in n or 'заочн' in n:
            return 'Evening / Extramural'
        elif 'специальн' in n or 'вспомогат' in n:
            return 'Special Needs School'
        else:
            return 'Standard Secondary School'
            
    df['school_type'] = df['school_name'].apply(get_category)
    df['is_specialized'] = df['school_type'].isin(['Gymnasium / Lyceum', 'Educational Complex (UVK)']).astype(int)
    
    out_schools = PROCESSED_DIR / "kg_schools_registry_enriched_2024.csv"
    df.to_csv(out_schools, index=False)
    logger.info(f"✓ Saved enriched schools registry ({len(df)} schools) to {out_schools}")
    
    # 2. Aggregate District School Infrastructure Statistics
    stats = df[df['district_id'] != 'kg_unknown'].groupby(['region_id', 'district_id']).agg(
        schools_total_count=('school_name', 'count'),
        private_schools_count=('is_private', 'sum'),
        specialized_schools_count=('is_specialized', 'sum'),
        boarding_schools_count=('school_type', lambda x: (x == 'Boarding School').sum())
    ).reset_index()
    
    stats['private_schools_share'] = (stats['private_schools_count'] / stats['schools_total_count']).round(4)
    stats['specialized_schools_share'] = (stats['specialized_schools_count'] / stats['schools_total_count']).round(4)
    
    out_stats = PROCESSED_DIR / "district_school_infrastructure_stats.csv"
    stats.to_csv(out_stats, index=False)
    logger.info(f"✓ Saved district school infrastructure stats ({len(stats)} districts) to {out_stats}")
    return df, stats

if __name__ == "__main__":
    process_schools_registry()
