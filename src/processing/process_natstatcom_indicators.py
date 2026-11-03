"""
Process and extract official National Statistical Committee (Stat.kg) educational datasets:
1. 11th Grade Graduates (Cohort size) by region (2006-2025)
2. Total Secondary Schools by region (2006-2025)
3. Total Students by region (2006-2025)
4. Female Teachers by region (2006-2025)

Output:
data/04_processed/natstatcom_regional_education_panel_2006_2025.csv
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/01_raw")
PROCESSED_DIR = Path("data/04_processed")

REGION_CONFIG = [
    {"name": "Баткенская область", "id": "kg_batken"},
    {"name": "Джалал-Абадская область", "id": "kg_jalalabad"},
    {"name": "Иссык-Кульская область", "id": "kg_issyk_kul"},
    {"name": "Нарынская область", "id": "kg_naryn"},
    {"name": "Ошская область", "id": "kg_osh"},
    {"name": "Таласская область", "id": "kg_talas"},
    {"name": "Чуйская область", "id": "kg_chuy"},
    {"name": "г.Бишкек", "id": "kg_bishkek"},
    {"name": "г.Ош", "id": "kg_osh_city"},
]

def get_year_col_mapping(df: pd.DataFrame, header_row: int) -> dict:
    cols = df.iloc[header_row].tolist()
    years_map = {}
    for idx, c in enumerate(cols):
        try:
            val = int(float(str(c)))
            if 2006 <= val <= 2025:
                years_map[idx] = val
        except (ValueError, TypeError):
            pass
    return years_map

def extract_metric_series(df: pd.DataFrame, header_row: int, indicator_keyword: str, scale_multiplier: float = 1.0) -> pd.DataFrame:
    years_map = get_year_col_mapping(df, header_row)
    records = []
    
    current_reg_id = None
    for r_idx in range(header_row + 1, len(df)):
        c1 = str(df.iloc[r_idx, 1]).strip()
        c0 = str(df.iloc[r_idx, 0]).strip()
        
        # Check if row is a region header
        matched_reg = None
        for reg in REGION_CONFIG:
            rname = reg["name"].lower()
            if rname in c1.lower() or rname in c0.lower():
                matched_reg = reg["id"]
                break
        if matched_reg:
            current_reg_id = matched_reg
            continue
            
        # Check if row matches the target indicator
        if current_reg_id and indicator_keyword.lower() in c1.lower():
            for col_idx, y in years_map.items():
                val = df.iloc[r_idx, col_idx]
                try:
                    num_str = str(val).replace(',', '.').replace('…', '').strip()
                    if num_str and num_str != 'nan':
                        num_val = float(num_str) * scale_multiplier
                    else:
                        num_val = np.nan
                except Exception:
                    num_val = np.nan
                    
                records.append({
                    "region_id": current_reg_id,
                    "year": y,
                    "value": num_val
                })
            # Reset after extracting for this region
            current_reg_id = None
            
    return pd.DataFrame(records).drop_duplicates(subset=["region_id", "year"])

def process_all_natstatcom():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. 11th Grade Graduates (thousands of people -> multiply by 1000)
    grad_file = RAW_DIR / "stat_graduates_by_territory.xls"
    df_grad = pd.read_excel(grad_file)
    res_grad = extract_metric_series(df_grad, header_row=5, indicator_keyword="Окончили среднюю (полную) школу", scale_multiplier=1000.0)
    res_grad = res_grad.rename(columns={"value": "cohort_graduates_11th"})
    
    # 2. Total Schools (units)
    school_file = RAW_DIR / "stat_schools_by_territory.xls"
    df_school = pd.read_excel(school_file)
    res_school = extract_metric_series(df_school, header_row=5, indicator_keyword="Общеобразовательные организации", scale_multiplier=1.0)
    res_school = res_school.rename(columns={"value": "stat_schools_total"})
    
    # 3. Total Students (people)
    student_file = RAW_DIR / "stat_students_by_territory.xls"
    df_student = pd.read_excel(student_file)
    res_student = extract_metric_series(df_student, header_row=2, indicator_keyword="Общеобразовательные организации", scale_multiplier=1.0)
    res_student = res_student.rename(columns={"value": "stat_students_total"})
    
    # 4. Female Teachers (people)
    teacher_file = RAW_DIR / "stat_female_teachers_by_territory.xls"
    df_teacher = pd.read_excel(teacher_file)
    res_teacher = extract_metric_series(df_teacher, header_row=3, indicator_keyword="Все учителя (включая руководителей)", scale_multiplier=1.0)
    res_teacher = res_teacher.rename(columns={"value": "stat_female_teachers_total"})
    
    # Merge all metrics
    master = pd.merge(res_grad, res_school, on=["region_id", "year"], how="outer")
    master = pd.merge(master, res_student, on=["region_id", "year"], how="outer")
    master = pd.merge(master, res_teacher, on=["region_id", "year"], how="outer")
    
    master = master.sort_values(by=["year", "region_id"]).reset_index(drop=True)
    
    out_csv = PROCESSED_DIR / "natstatcom_regional_education_panel_2006_2025.csv"
    master.to_csv(out_csv, index=False)
    
    logger.info("==================================================")
    logger.info("NATSTATCOM REGIONAL PANEL ASSEMBLED:")
    logger.info(f"Total Rows: {len(master)}")
    logger.info(f"Regions: {master['region_id'].nunique()} (All 9 regions)")
    logger.info(f"Years: {master['year'].nunique()} (2006-2025)")
    logger.info(f"Columns: {list(master.columns)}")
    logger.info(f"Saved to: {out_csv}")
    logger.info("==================================================")
    return master

if __name__ == "__main__":
    process_all_natstatcom()
