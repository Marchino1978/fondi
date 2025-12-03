import csv
import requests
from bs4 import BeautifulSoup

# -----------------------------
# Parser Eurizon
# -----------------------------
def parse_eurizon(url, nome):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # esempio: cerca NAV in una classe (da adattare all'HTML reale di Eurizon)
        nav_tag = soup.find("span", {"class": "navValue"})
        if nav_tag:
            value = nav_tag.get_text(strip=True).replace(",", ".")
            return {"nome": nome, "price": float(value)}
    except Exception as e:
        print(f"Errore Eurizon {nome}: {e}")
    return {"nome": nome, "price": None}

# -----------------------------
# Parser Borsa Italiana
# -----------------------------
def parse_borsaitaliana(url, nome):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.find("td", string=lambda s: s and "Prezzo di riferimento" in s)
        if price_tag:
            value = price_tag.find_next("td").get_text(strip=True)
            value = value.replace("€", "").replace(".", "").replace(",", ".").strip()
            return {"nome": nome, "price": float(value)}
    except Exception as e:
        print(f"Errore BorsaItaliana {nome}: {e}")
    return {"nome": nome, "price": None}

# -----------------------------
# Dispatcher: sceglie parser in base all'URL
# -----------------------------
def get_price(url, nome):
    if "eurizoncapital.com" in url:
        return parse_eurizon(url, nome)
    elif "borsaitaliana.it" in url:
        return parse_borsaitaliana(url, nome)
    else:
        print(f"Provider non riconosciuto per {nome} ({url})")
        return {"nome": nome, "price": None}

# -----------------------------
# Main
# -----------------------------
def main():
    results = []
    with open("fondi.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # salta intestazione "nome,url"

        for row in reader:
            if not row or row[0].startswith("#"):
                continue  # ignora commenti o righe vuote

            try:
                nome, url = row
            except ValueError:
                print(f"Riga non valida: {row}")
                continue

            data = get_price(url.strip(), nome.strip())
            results.append(data)

    # scrive output
    with open("fondi_nav.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nome", "price"])
        for r in results:
            writer.writerow([r["nome"], r["price"]])

    print(f"Scritte {len(results)} righe in fondi_nav.csv")

if __name__ == "__main__":
    main()
