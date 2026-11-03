"""
Extract 20-Year Gender-Disaggregated Panel from official CEAMO ORT Annual Reports (2006-2025).
Extracts:
- Female (Девушки) vs Male (Юноши) participation counts
- Mean test score by gender
- Standard deviation of scores
- Number of state grant recipients by gender
- Mean score of grant recipients by gender
- Gender gap metrics (Female - Male difference)

Output:
data/04_processed/ort_gender_gap_panel_2006_2025.csv
"""

import re
import logging
from pathlib import Path
import pandas as pd
import pdfplumber

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/01_raw/ort_reports")
PROCESSED_DIR = Path("data/04_processed")

def extract_gender_for_year(pdf_path: Path, year: int):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        # Gender section is typically between page 20 and 55
        for p_idx in range(15, min(60, num_pages)):
            text = pdf.pages[p_idx].extract_text()
            if not text:
                continue
                
            t_low = text.lower()
            if "результаты девушек и юношей" in t_low or ("девушки" in t_low and "юноши" in t_low and "грантов" in t_low):
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                
                curr_gender = None
                for line in lines:
                    if line.lower() == "девушки" or line.lower().startswith("девушки"):
                        curr_gender = "Female"
                    elif line.lower() == "юноши" or line.lower().startswith("юноши"):
                        curr_gender = "Male"
                        
                    if curr_gender:
                        # Match row with: participants, mean_score, std_dev, [alpha], grant_count, grant_mean
                        # Example: 32554 130.1 29.9 0.91 4220 153.4
                        # Or: 21300 120.5 28.4 2500 148.2
                        m = re.search(r'(\d{4,6})\s+([\d\.]+)\s+([\d\.]+)\s+(?:[\d\.]+\s+)?(\d{3,5})\s+([\d\.]+)', line)
                        if m:
                            part_cnt = int(m.group(1))
                            mean_sc = float(m.group(2))
                            std_sc = float(m.group(3))
                            grant_cnt = int(m.group(4))
                            grant_mean = float(m.group(5))
                            
                            if 80 <= mean_sc <= 160: # Valid ORT score range
                                records.append({
                                    "year": year,
                                    "gender": curr_gender,
                                    "participants_count": part_cnt,
                                    "mean_score": mean_sc,
                                    "std_dev": std_sc,
                                    "grant_admitted_count": grant_cnt,
                                    "grant_mean_score": grant_mean,
                                    "page": p_idx + 1
                                })
                                curr_gender = None # Reset after matching
    return records

def process_all_gender_panels():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_recs = []
    
    for y in range(2006, 2026):
        p = RAW_DIR / f"ort_report_{y}.pdf"
        if not p.exists():
            continue
        try:
            recs = extract_gender_for_year(p, y)
            all_recs.extend(recs)
            logger.info(f"Year {y}: extracted {len(recs)} gender records")
        except Exception as e:
            logger.error(f"Error in {y}: {e}")
            
    df = pd.DataFrame(all_recs)
    if not df.empty:
        df = df.drop_duplicates(subset=["year", "gender"])
        df = df.sort_values(by=["year", "gender"]).reset_index(drop=True)
        
        # Build wide pivot to compute Gender Gap (Female - Male)
        f_df = df[df["gender"] == "Female"].set_index("year")
        m_df = df[df["gender"] == "Male"].set_index("year")
        
        shared_years = sorted(list(set(f_df.index).intersection(set(m_df.index))))
        gap_rows = []
        for y in shared_years:
            f_row = f_df.loc[y]
            m_row = m_df.loc[y]
            total_part = f_row["participants_count"] + m_row["participants_count"]
            gap_rows.append({
                "year": y,
                "female_participants": f_row["participants_count"],
                "male_participants": m_row["participants_count"],
                "total_participants": total_part,
                "female_share_pct": round(f_row["participants_count"] / total_part * 100, 2),
                "female_mean_score": f_row["mean_score"],
                "male_mean_score": m_row["mean_score"],
                "gender_score_gap": round(f_row["mean_score"] - m_row["mean_score"], 2),
                "female_grant_count": f_row["grant_admitted_count"],
                "male_grant_count": m_row["grant_admitted_count"],
                "female_grant_share_pct": round(f_row["grant_admitted_count"] / (f_row["grant_admitted_count"] + m_row["grant_admitted_count"]) * 100, 2),
                "female_grant_mean_score": f_row["grant_mean_score"],
                "male_grant_mean_score": m_row["grant_mean_score"]
            })
            
        gap_df = pd.DataFrame(gap_rows)
        
        out_long = PROCESSED_DIR / "ort_gender_disaggregated_panel_2006_2025.csv"
        out_gap = PROCESSED_DIR / "ort_gender_gap_panel_2006_2025.csv"
        
        df.to_csv(out_long, index=False)
        gap_df.to_csv(out_gap, index=False)
        
        logger.info("==================================================")
        logger.info("GENDER GAP PANEL ASSEMBLED:")
        logger.info(f"Total Years Covered: {len(gap_df)}")
        logger.info(f"Years: {gap_df['year'].tolist()}")
        logger.info(f"Mean Female Advantage across years: {gap_df['gender_score_gap'].mean():.2f} points")
        logger.info(f"Mean Female Grant Share: {gap_df['female_grant_share_pct'].mean():.2f}%")
        logger.info(f"Saved to: {out_long} and {out_gap}")
        logger.info("==================================================")
        return gap_df
    return df

if __name__ == "__main__":
    process_all_gender_panels()
