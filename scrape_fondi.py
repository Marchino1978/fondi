import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------------
# Fetch HTML con gestione errori
# -----------------------------
def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        if not r.text or len(r.text.strip()) == 0:
            raise ValueError("HTML vuoto da " + url)
        return r.text
    except Exception as e:
        print(f"Errore fetch {url}: {e}")
        return None

# -----------------------------
# Parser Eurizon
# -----------------------------
def parse_eurizon(html):
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    span = soup.find("span", class_="product-dashboard-token-value-bold color-green")
    if span and span.get_text(strip=True):
        return span.get_text(strip=True)

    text = soup.get_text(" ", strip=True)
    match = re.search(r"\b\d{1,3}(\.\d{3})*,\d{2}\b|\b\d+,\d{2}\b", text)
    if match:
        return match.group(0)
    return None

# -----------------------------
# Parser Teleborsa
# -----------------------------
def parse_teleborsa(html):
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    price_span = soup.find("span", id="ctl00_phContents_ctlHeader_lblPrice")
    if price_span:
        raw = price_span.get_text(strip=True)
        if raw:
            return raw

    alt = soup.find("span", id=re.compile(r"lblPrice", re.I))
    if alt:
        raw = alt.get_text(strip=True)
        if raw:
            return raw

    text = soup.get_text(" ", strip=True)
    match = re.search(r"\b\d{1,3}(\.\d{3})*,\d{2}\b|\b\d{1,3}(\.\d{3})*\b", text)
    if match:
        return match.group(0)

    return None

# -----------------------------
# Normalizzazione valori IT -> EN
# -----------------------------
def normalize(value_it):
    if not value_it:
        return None
    s = value_it.strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    return s

# -----------------------------
# Main
# -----------------------------
def main():
    # Legge lista fondi da CSV
    with open("fondi.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fondi = list(reader)

    # Inizializza output
    with open("fondi_nav.csv", "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out, delimiter=";")
        writer.writerow(["timestamp", "nome", "nav_text_it", "nav_float"])

    # Loop sui fondi
    for fondo in fondi:
        nome = fondo["nome"].strip()
        url = fondo["url"].strip()
        try:
            html = fetch_html(url)
            if not html:
                raise ValueError("HTML non disponibile")

            if "eurizoncapital.com" in url:
                nav_text = parse_eurizon(html)
            elif "teleborsa.it" in url:
                nav_text = parse_teleborsa(html)
            else:
                nav_text = None

            nav_float = normalize(nav_text)
            with open("fondi_nav.csv", "a", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out, delimiter=";")
                writer.writerow([datetime.now().isoformat(), nome, nav_text or "N/D", nav_float or "N/D"])
            print(f"{nome}: {nav_text or 'N/D'}")
        except Exception as e:
            with open("fondi_nav.csv", "a", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out, delimiter=";")
                writer.writerow([datetime.now().isoformat(), nome, "ERRORE", ""])
            print(f"{nome}: errore {repr(e)}")

if __name__ == "__main__":
    main()
