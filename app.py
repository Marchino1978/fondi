from flask import Flask, jsonify
import os
import base64
import requests

# Import diretto della logica di scraping
# Assicurati che in scrape_fondi.py ci sia una funzione main()
from scrape_fondi import main as scrape_fondi_main

app = Flask(__name__)

# Endpoint di healthcheck per Render
@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

# Endpoint di keep-alive (ping leggero per UptimeRobot)
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# Funzione per fare commit automatico su GitHub
def commit_csv_to_github():
    GH_TOKEN = os.environ.get("GH_TOKEN")  # PAT GitHub
    GH_REPO = os.environ.get("GH_REPO", "Marchino1978/fondi")  # repo target
    GH_BRANCH = os.environ.get("GH_BRANCH", "main")            # branch target
    FILE_PATH = "fondi_nav.csv"

    # Legge il contenuto del CSV
    with open(FILE_PATH, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Endpoint API GitHub per il file
    api_url = f"https://api.github.com/repos/{GH_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}"}  # 🔧 aggiornato

    # Recupera SHA del file se già esiste
    r = requests.get(api_url, headers=headers, params={"ref": GH_BRANCH})
    sha = r.json().get("sha") if r.status_code == 200 else None

    # Corpo della richiesta PUT
    body = {
        "message": "Aggiornamento automatico NAV fondi",
        "content": content,
        "branch": GH_BRANCH,
    }
    if sha:
        body["sha"] = sha

    # Commit su GitHub
    resp = requests.put(api_url, headers=headers, json=body)

    # 👇 Debug: stampa nei log di Render
    print("GitHub response status:", resp.status_code)
    print("GitHub response body:", resp.text)

    resp.raise_for_status()
    print("✅ Commit su GitHub completato")

# Endpoint per aggiornare i fondi
@app.route("/update-fondi", methods=["GET", "POST"])
def update_fondi():
    try:
        # esegue direttamente la logica di scraping
        scrape_fondi_main()
        # commit automatico su GitHub
        commit_csv_to_github()
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        print("Errore in /update-fondi:", str(e))
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
