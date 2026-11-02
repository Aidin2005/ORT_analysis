"""
Download official annual analytical reports from testing.kg (CEATM).
Fetches metadata from https://testing.kg/api/reports, filters Russian-language
annual reports for 2006-2025, and saves them with a manifest.
"""

import re
import json
from pathlib import Path
import requests

BASE_URL = "https://testing.kg"
API_URL = f"{BASE_URL}/api/reports"
OUTPUT_DIR = Path("data/01_raw/ort_reports")

def extract_year(title: str, pdf_url: str):
    """Extract 4-digit year from title or URL."""
    match = re.search(r'\b(20[0-2][0-9])\b', title)
    if match:
        return int(match.group(1))
    match = re.search(r'\b(20[0-2][0-9])\b', pdf_url)
    if match:
        return int(match.group(1))
    return None

def is_annual_russian_report(report: dict) -> bool:
    """Check if the report is the primary Russian annual report."""
    title = report.get("title", "").strip().lower()
    pdf = report.get("pdf", "").strip()

    if not pdf.lower().endswith(".pdf"):
        return False
        
    # Skip Kyrgyz language versions for the primary set
    if any(k in title for k in ["жыл", "боюнча", "жыйынтык", "отчёту 20", "отчету 20"]):
        if not ("отчет" in title and "орт" in title and not "боюнча" in title):
            return False
            
    # Skip autumn/winter sessions
    if any(k in title for k in ["осенн", "зима", "зимний"]):
        return False

    # Skip olympiad instructions, guidelines, regulations, brochures
    skip_keywords = ["олимпиад", "смета", "положение", "инструкция", "правила", 
                     "готовимся", "порядок", "перечень", "нооду", "nsba", "pisa", "неправильный"]
    if any(k in title for k in skip_keywords):
        return False

    valid_keywords = ["отчет", "отчёт", "результаты общереспубликанского", "орт"]
    if any(k in title for k in valid_keywords):
        return True

    return False

def download_file(url: str, dest_path: Path):
    """Download file in chunks with requests."""
    headers = {'User-Agent': 'Mozilla/5.0 (EduAnalytics-KG Research Project)'}
    # verify=False or verify=True, with stream=True
    resp = requests.get(url, headers=headers, stream=True, timeout=30, verify=False)
    resp.raise_for_status()
    with open(dest_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)

def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching report metadata from {API_URL}...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (EduAnalytics-KG Research Project)'}
    resp = requests.get(API_URL, headers=headers, timeout=20, verify=False)
    resp.raise_for_status()
    data = resp.json()

    reports = data.get("reports", [])
    print(f"Found total {len(reports)} items in API.")

    seen_years = {}
    for rep in reports:
        if is_annual_russian_report(rep):
            year = extract_year(rep["title"], rep["pdf"])
            if year:
                # Prefer more comprehensive report if multiple exist
                if year not in seen_years or ("отчет" in rep["title"].lower() and "смета" not in rep["title"].lower()):
                    seen_years[year] = rep

    sorted_years = sorted(seen_years.keys())
    print(f"\nFiltered {len(sorted_years)} annual Russian reports ({sorted_years[0]} - {sorted_years[-1]}):")
    
    manifest = []
    for y in sorted_years:
        rep = seen_years[y]
        pdf_rel = rep["pdf"]
        full_url = BASE_URL + pdf_rel if not pdf_rel.startswith("http") else pdf_rel
        
        file_name = f"ort_report_{y}.pdf"
        dest_file = OUTPUT_DIR / file_name

        print(f"[{y}] {rep['title']}")
        print(f"     URL: {full_url}")

        status = "existing"
        if not dest_file.exists() or dest_file.stat().st_size == 0:
            try:
                print(f"     Downloading {file_name}...")
                download_file(full_url, dest_file)
                status = "downloaded"
                print(f"     ✓ Downloaded ({dest_file.stat().st_size / (1024*1024):.2f} MB)")
            except Exception as e:
                print(f"     ✗ Error: {e}")
                status = f"error: {str(e)}"
        else:
            print(f"     ✓ Already exists ({dest_file.stat().st_size / (1024*1024):.2f} MB)")

        manifest.append({
            "year": y,
            "id": rep["id"],
            "title": rep["title"],
            "url": full_url,
            "local_file": str(dest_file),
            "size_bytes": dest_file.stat().st_size if dest_file.exists() else 0,
            "status": status
        })

    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"\nManifest saved to {manifest_path}")

if __name__ == "__main__":
    main()
