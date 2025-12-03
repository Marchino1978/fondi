import csv
import requests
from bs4 import BeautifulSoup
import io

# -----------------------------
# Parser per Eurizon
# -----------------------------
def parse_eurizon(url, isin):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        nav_tag = soup.find("span", {"class": "navValue"})  # da adattare all'HTML reale
        if nav_tag:
            value = nav_tag.get_text(strip=True).replace(",", ".")
            return {"isin": isin, "price": float(value)}
    except Exception as e:
        print(f"Errore Eurizon {isin}: {e}")
    return {"isin": isin, "price": None}

# -----------------------------
# Parser per Amundi
# -----------------------------
def parse_amundi(url, isin):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        nav_tag = soup.find("span", {"class": "navValue"})  # da adattare all'HTML reale
        if nav_tag:
            value = nav_tag.get_text(strip=True).replace(",", ".")
            return {"isin": isin, "price": float(value)}
    except Exception as e:
        print(f"Errore Amundi {isin}: {e}")
    return {"isin": isin, "price": None}

# -----------------------------
# Parser per Borsa Italiana
# -----------------------------
def parse_borsaitaliana(url, isin):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.find("td", string="Prezzo di riferimento")
        if price_tag:
            value = price_tag.find_next("td").get_text(strip=True)
            value = value.replace("€", "").replace(".", "").replace(",", ".").strip()
            return {"isin": isin, "price": float(value)}
    except Exception as e:
        print(f"Errore BorsaItaliana {isin}: {e}")
    return {"isin": isin, "price": None}

# -----------------------------
# Dispatcher
# -----------------------------
def get_price(provider, url, isin):
    provider = provider.strip().lower()
    if provider == "eurizon":
        return parse_eurizon(url, isin)
    elif provider == "amundi":
        return parse_amundi(url, isin)
    elif provider == "borsaitaliana":
        return parse_borsaitaliana(url, isin)
    else:
        print(f"Provider non supportato: {provider} (ISIN {isin})")
        return {"isin": isin, "price": None}

# -----------------------------
# Lettura CSV con commenti e separatori vari
# -----------------------------
def read_fondi(path):
    # carica file e filtra righe di commento o vuote
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    filtered = []
    for line in raw_lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        filtered.append(line)

    if not filtered:
        print("Nessuna riga valida trovata in fondi.csv")
        return [], None

    # prova con virgola, se fallisce usa punto e virgola
    data = "".join(filtered)
    for delimiter in [",", ";"]:
        try:
            reader = csv.DictReader(io.StringIO(data), delimiter=delimiter)
            rows = []
            for row in reader:
                # verifica colonne minime
                if not row.get("isin") or not row.get("provider") or not row.get("url"):
                    continue
                rows.append({
                    "isin": row["isin"].strip(),
                    "provider": row["provider"].strip(),
                    "url": row["url"].strip(),
                })
            if rows:
                print(f"Caricate {len(rows)} righe con delimitatore '{delimiter}'")
                return rows, delimiter
        except Exception as e:
            print(f"Errore parsing con delimitatore '{delimiter}': {e}")

    print("Impossibile parse fondi.csv: controlla intestazione 'isin,provider,url' e delimitatore")
    return [], None

# -----------------------------
# Main
# -----------------------------
def main():
    rows, delim = read_fondi("fondi.csv")
    results = []

    for r in rows:
        data = get_price(r["provider"], r["url"], r["isin"])
        results.append(data)

    with open("fondi_nav.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["isin", "price"])
        for r in results:
            writer.writerow([r["isin"], r["price"]])

    print(f"Scritte {len(results)} righe in fondi_nav.csv")

if __name__ == "__main__":
    main()
