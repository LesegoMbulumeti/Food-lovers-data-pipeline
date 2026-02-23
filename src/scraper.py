import csv
import hashlib
import os
import re
import time

import requests
from bs4 import BeautifulSoup


BASE_URL   = "https://foodloversmarket.co.za"
API_URL    = f"{BASE_URL}/wp-json/wp/v2/store?per_page=100&page="
ROOT_DIR    = os.path.dirname(os.path.dirname(__file__))
OUTPUT_RAW  = os.path.join(ROOT_DIR, "data", "raw", "stores_raw.json")
OUTPUT_CSV  = os.path.join(ROOT_DIR, "data", "processed", "stores.csv")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

PROVINCE_SLUG_MAP = {
    "western-cape":           "Western Cape",
    "eastern-cape":           "Eastern Cape",
    "northern-cape":          "Northern Cape",
    "kwazulu-natal":          "KwaZulu-Natal",
    "gauteng":                "Gauteng",
    "limpopo":                "Limpopo",
    "mpumalanga":             "Mpumalanga",
    "free-state":             "Free State",
    "north-west":             "North West",
    "south-western-districts":"Western Cape",
}

SA_CITIES = [
    "Cape Town", "Johannesburg", "Pretoria", "Durban", "Port Elizabeth",
    "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley",
    "Sandton", "Randburg", "Roodepoort", "Boksburg", "Germiston",
    "Centurion", "Midrand", "Fourways", "Ballito", "Umhlanga",
    "Pietermaritzburg", "Richards Bay", "George", "Knysna", "Hermanus",
    "Stellenbosch", "Paarl", "Worcester", "Mossel Bay", "Hartenbos",
    "Klerksdorp", "Rustenburg", "Mahikeng", "Witbank", "Secunda",
    "Kathu", "Upington", "Springbok", "Jeffreys Bay", "Grahamstown",
    "Lenasia", "Soweto", "Jabulani", "Bassonia", "Ferndale",
    "Bothasig", "Brackenfell", "Hillfox", "Edenvale", "Benoni",
    "Alberton", "Krugersdorp", "Vanderbijlpark", "Vereeniging",
]

# ------------------------------------------------------------------ helpers

def branch_id(name: str, address: str) -> str:
    """Stable 12-char hex ID derived from store name + address."""
    return hashlib.md5(f"{name}_{address}".encode()).hexdigest()[:12]

def extract_postal_code(text: str) -> str:
    m = re.search(r"\b\d{4}\b", text)
    return m.group() if m else ""

def extract_province(url: str) -> str:
    for slug, province in PROVINCE_SLUG_MAP.items():
        if f"/{slug}/" in url:
            return province
    return ""

def extract_city(text: str) -> str:
    for city in SA_CITIES:
        if city.lower() in text.lower():
            return city
    return ""

# ------------------------------------------------------------------ API fetch

def fetch_all_stores() -> list:
    """Paginate through the WP REST API and return raw store records."""
    session = requests.Session()
    session.headers.update(HEADERS)
    stores, page = [], 1

    while True:
        print(f"  Fetching page {page}...")
        r = session.get(API_URL + str(page), timeout=15)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        stores.extend(batch)
        page += 1
        time.sleep(0.5)  

    return stores


def parse_store(item: dict) -> dict:
    """Extract and clean fields from a single WP API store record."""
    # Store name (HTML-encoded in WP, so decode it)
    raw_name = item.get("title", {}).get("rendered", "") or item.get("name", "")
    name = BeautifulSoup(raw_name, "html.parser").get_text(strip=True)

    # Address fields — WP custom fields may be nested under 'acf' or at root
    acf  = item.get("acf", {}) or {}
    meta = item.get("meta", {}) or {}

    address = (
        acf.get("address")
        or acf.get("store_address")
        or item.get("address", "")
        or ""
    )

    lat = str(
        acf.get("latitude") or acf.get("lat")
        or meta.get("latitude") or meta.get("lat")
        or item.get("latitude") or item.get("lat")
        or ""
    )
    lng = str(
        acf.get("longitude") or acf.get("lng")
        or meta.get("longitude") or meta.get("lng")
        or item.get("longitude") or item.get("lng")
        or ""
    )

    link    = item.get("link", "")
    address = address.replace("\n", ", ").strip()

    return {
        "branch_id":    branch_id(name, address),
        "store_name":   name,
        "address_line": address,
        "city":         extract_city(address),
        "province":     extract_province(link),
        "postal_code":  extract_postal_code(address),
        "latitude":     lat,
        "longitude":    lng,
    }


def save_raw(raw: list, path: str = OUTPUT_RAW):
    """Save the untouched API response as JSON for reprocessing later."""
    import json
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    print(f"Saved raw API response → {path}")

def save_csv(stores: list, path: str = OUTPUT_CSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(stores[0].keys()))
        writer.writeheader()
        writer.writerows(stores)
    print(f"Saved {len(stores)} stores → {path}")


if __name__ == "__main__":
    print("Fetching stores from Food Lover's Market API...")
    raw = fetch_all_stores()
    print(f"  {len(raw)} records retrieved.\n")

    if not raw:
        print("No data returned. Check the API URL or your internet connection.")
    else:
        save_raw(raw)                                  
        stores = [parse_store(item) for item in raw]
        save_csv(stores)                                   
        print("\nDone.")