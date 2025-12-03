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

# -----------------------------
# Parser Eurizon
# -----------------------------
def parse_eurizon(html):
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
# Parser Teleborsa (SEDEX certificati)
# -----------------------------
def parse_teleborsa(html):
    soup = BeautifulSoup(html, "html.parser")

    # 1) target diretto: id del prezzo header
    price_span = soup.find("span", id="ctl00_phContents_ctlHeader_lblPrice")
    if price_span:
        raw = price_span.get_text(strip=True)
        if raw:
            return raw  # es: "975" oppure "975,00"

    # 2) fallback: altri span header correlati
    alt = soup.find("span", id=re.compile(r"lblPrice", re.I))
    if alt:
        raw = alt.get_text(strip=True)
        if raw:
            return raw

    # 3) fallback regex su tutta la pagina (ITA formato)
    text = soup.get_text(" ", strip=True)
    match = re.search(r"\b\d{1,3}(\.\d{3})*,\d{2}\b|\b\d{1,3}(\.\d{3})*\b", text)
    if match:
        return match.group(0)

    return None

# -----------------------------
# Normalizzazione
# -----------------------------
def normalize(value_it):
    # accetta sia "975", sia "975,00", sia "1.234,56"
    if not value_it:
        return None
    s = value_it.strip()
    # se contiene virgola decimale, converti IT -> EN
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # numeri interi con eventuale separatore miglia
        s = s.replace(".", "")
    return s

# -----------------------------
# Main
# -----------------------------
def main():
    with open("fondi.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fondi = list(reader)

    with open("fondi_nav.csv", "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out, delimiter=";")
        writer.writerow(["timestamp", "nome", "nav_text_it", "nav_float"])

    for fondo in fondi:
        nome = fondo["nome"].strip()
        url = fondo["url"].strip()
        try:
            html = fetch_html(url)
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
            print(f"{nome}: {nav_text}")
        except Exception as e:
            with open("fondi_nav.csv", "a", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out, delimiter=";")
                writer.writerow([datetime.now().isoformat(), nome, "ERRORE", ""])
            print(f"{nome}: errore {e}")

if __name__ == "__main__":
    main()
