"""
Download official administrative boundaries (GeoJSON) for Kyrgyzstan.
Retrieves ADM1 (Oblasts + Republican Cities) and ADM2 (Districts / Raions).
Uses GeoBoundaries open API (run by William & Mary geoLab).
"""

import json
from pathlib import Path
import requests

GEO_DIR = Path("data/01_raw/geo")

def fetch_geoboundary(level: str):
    """Fetch GeoJSON for KGZ at given level (ADM1, ADM2)."""
    api_url = f"https://www.geoboundaries.org/api/current/gbOpen/KGZ/{level}/"
    headers = {'User-Agent': 'Mozilla/5.0 (EduAnalytics-KG Research Project)'}
    
    print(f"Querying GeoBoundaries API for KGZ {level}...")
    resp = requests.get(api_url, headers=headers, timeout=20, verify=False)
    resp.raise_for_status()
    meta = resp.json()
        
    geojson_url = meta.get("gjDownloadURL")
    if not geojson_url:
        print(f"No GeoJSON URL found for {level}")
        return
        
    dest_path = GEO_DIR / f"kgz_{level.lower()}.geojson"
    print(f"Downloading {level} GeoJSON from {geojson_url} -> {dest_path}...")
    
    resp_dl = requests.get(geojson_url, headers=headers, timeout=30, verify=False)
    resp_dl.raise_for_status()
    with open(dest_path, "wb") as f_out:
        f_out.write(resp_dl.content)
        
    print(f"✓ Saved {level} GeoJSON ({dest_path.stat().st_size / 1024:.1f} KB)")

def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    try:
        fetch_geoboundary("ADM1")
        fetch_geoboundary("ADM2")
        print("\nAll boundaries downloaded successfully.")
    except Exception as e:
        print(f"Warning: Geo download encountered: {e}")

if __name__ == "__main__":
    main()
