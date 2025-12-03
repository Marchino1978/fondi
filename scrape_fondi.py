import csv
import requests
from bs4 import BeautifulSoup

# -----------------------------
# Parser per Eurizon
# -----------------------------
def parse_eurizon(url, isin):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # esempio: cerca NAV in una classe (da adattare all'HTML reale)
        nav_tag = soup.find("span", {"class": "navValue"})
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

        nav_tag = soup.find("span", {"class": "navValue"})
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
    if provider == "eurizon":
        return parse_eurizon(url, isin)
    elif provider == "amundi":
        return parse_amundi(url, isin)
    elif provider == "borsaitaliana":
        return parse_borsaitaliana(url, isin)
    else:
        print(f"Provider {provider} non supportato")
        return {"isin": isin, "price": None}

# -----------------------------
# Main
# -----------------------------
def main():
    results = []
    with open("fondi.csv", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)  # salta intestazione

        for row in reader:
            # ignora righe vuote o commenti
            if not row or row[0].startswith("#"):
                continue

            try:
                isin, provider, url = row
            except ValueError:
                print(f"Riga non valida: {row}")
                continue

            data = get_price(provider.strip().lower(), url.strip(), isin.strip())
            results.append(data)

    # scrive output
    with open("fondi_nav.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["isin", "price"])
        for r in results:
            writer.writerow([r["isin"], r["price"]])

if __name__ == "__main__":
    main()
