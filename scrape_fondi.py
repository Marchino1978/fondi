import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_nav(html):
    soup = BeautifulSoup(html, "html.parser")
    span = soup.find("span", class_="product-dashboard-token-value-bold color-green")
    if span and span.get_text(strip=True):
        return span.get_text(strip=True)
    # fallback regex
    text = soup.get_text(" ", strip=True)
    match = re.search(r"\b\d{1,3}(\.\d{3})*,\d{2}\b|\b\d+,\d{2}\b", text)
    if match:
        return match.group(0)
    return None

def normalize(value_it):
    return value_it.replace(".", "").replace(",", ".") if value_it else None

def main():
    with open("fondi.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fondi = list(reader)

    with open("fondi_nav.csv", "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["timestamp", "nome", "nav_text_it", "nav_float"])

        for fondo in fondi:
            nome = fondo["nome"]
            url = fondo["url"]
            try:
                html = fetch_html(url)
                nav_text = parse_nav(html)
                nav_float = normalize(nav_text)
                writer.writerow([datetime.now().isoformat(), nome, nav_text or "N/D", nav_float or "N/D"])
                print(f"{nome}: {nav_text}")
            except Exception as e:
                writer.writerow([datetime.now().isoformat(), nome, "ERRORE", ""])
                print(f"{nome}: errore {e}")

if __name__ == "__main__":
    main()
