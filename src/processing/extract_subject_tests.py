"""
Extract 20-Year Subject-Level Panel from official CEAMO ORT Annual Reports (2006-2025).
Extracts:
- Biology, Chemistry, Physics, Mathematics, History, English Language,
  Kyrgyz Language & Literature, Russian Language & Literature, State Language.
- Language of test taking (Kyrgyz, Russian, Total)
- Number of test takers, mean score, min score, max score.

Output:
data/04_processed/ort_subject_tests_panel_2006_2025.csv
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

SUBJECT_CANONICAL = {
    "биологи": "Biology",
    "хими": "Chemistry",
    "физик": "Physics",
    "математик": "Mathematics",
    "истори": "History",
    "английск": "English Language",
    "немецк": "German Language",
    "государственн": "State Language",
    "кыргызск": "Kyrgyz Language & Lit",
    "русск": "Russian Language & Lit"
}

def identify_subject(header_text: str) -> str:
    h = header_text.lower()
    for k, v in SUBJECT_CANONICAL.items():
        if k in h:
            return v
    return "Other Subject"

def extract_subjects_from_report(pdf_path: Path, year: int):
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        # Subject section is usually between pages 15 and 55
        start_p = 10
        end_p = min(55, num_pages)
        
        for p_idx in range(start_p, end_p):
            page = pdf.pages[p_idx]
            text = page.extract_text()
            if not text:
                continue
                
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            
            # Find subject sections
            curr_subject = None
            for idx, line in enumerate(lines):
                if "участие в тесте" in line.lower() or "тест по" in line.lower() or "предметный тест" in line.lower():
                    # Look ahead/behind for subject name
                    context = " ".join(lines[max(0, idx-1):min(len(lines), idx+3)])
                    curr_subject = identify_subject(context)
                    
                if curr_subject:
                    # Check for Kyrgyz/Russian/Total row
                    # Regex for: Language, participants, mean, max, min
                    m_lang = re.match(r'^(Кыргызский|Русский|В целом:?)\s+(\d+)\s+([\d\.]+)\s+(\d+)\s+(\d+)', line)
                    if m_lang:
                        lang = m_lang.group(1).replace(":", "")
                        results.append({
                            "year": year,
                            "subject": curr_subject,
                            "test_language": "Kyrgyz" if lang == "Кыргызский" else ("Russian" if lang == "Русский" else "All"),
                            "participants_count": int(m_lang.group(2)),
                            "mean_score": float(m_lang.group(3)),
                            "max_score": int(m_lang.group(4)),
                            "min_score": int(m_lang.group(5)),
                            "page": p_idx + 1
                        })
                    else:
                        # Single-language test (e.g. English, or general)
                        # Pattern: participants, mean, max, min
                        m_single = re.match(r'^(\d{3,6})\s+([\d\.]+)\s+(\d{2,3})\s+(\d{1,3})$', line)
                        if m_single:
                            # Verify plausible mean score (typically 20-100)
                            mean_val = float(m_single.group(2))
                            if 20 <= mean_val <= 120:
                                results.append({
                                    "year": year,
                                    "subject": curr_subject,
                                    "test_language": "All",
                                    "participants_count": int(m_single.group(1)),
                                    "mean_score": mean_val,
                                    "max_score": int(m_single.group(3)),
                                    "min_score": int(m_single.group(4)),
                                    "page": p_idx + 1
                                })
    return results

def process_all_subject_tests():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_records = []
    
    for y in range(2006, 2026):
        pdf_path = RAW_DIR / f"ort_report_{y}.pdf"
        if not pdf_path.exists():
            continue
        logger.info(f"Extracting subjects for {y}...")
        try:
            recs = extract_subjects_from_report(pdf_path, y)
            all_records.extend(recs)
            logger.info(f"  Year {y}: extracted {len(recs)} subject records")
        except Exception as e:
            logger.error(f"  Error in year {y}: {e}")
            
    df = pd.DataFrame(all_records)
    if not df.empty:
        # Deduplicate
        df = df.drop_duplicates(subset=["year", "subject", "test_language"])
        df = df.sort_values(by=["year", "subject", "test_language"]).reset_index(drop=True)
        
        out_csv = PROCESSED_DIR / "ort_subject_tests_panel_2006_2025.csv"
        df.to_csv(out_csv, index=False)
        
        logger.info("==================================================")
        logger.info("SUBJECT TESTS PANEL ASSEMBLED:")
        logger.info(f"Total Rows: {len(df)}")
        logger.info(f"Years: {df['year'].nunique()} (2006-2025)")
        logger.info(f"Subjects: {df['subject'].unique().tolist()}")
        logger.info(f"Languages: {df['test_language'].unique().tolist()}")
        logger.info(f"Saved to: {out_csv}")
        logger.info("==================================================")
    return df

if __name__ == "__main__":
    process_all_subject_tests()
