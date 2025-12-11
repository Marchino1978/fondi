import threading
from flask import Flask, jsonify
import os
import base64
import requests
from src.scrape_fondi import main as scrape_fondi_main   # aggiornato

app = Flask(__name__)

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

def commit_csv_to_github():
    GH_TOKEN = os.environ.get("GH_TOKEN")
    GH_REPO = os.environ.get("GH_REPO", "Marchino1978/fondi")
    GH_BRANCH = os.environ.get("GH_BRANCH", "main")
    FILE_PATH = "data/fondi_nav.csv"   # aggiornato

    with open(FILE_PATH, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    api_url = f"https://api.github.com/repos/{GH_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}"}

    r = requests.get(api_url, headers=headers, params={"ref": GH_BRANCH})
    sha = r.json().get("sha") if r.status_code == 200 else None

    body = {
        "message": "Aggiornamento automatico NAV fondi",
        "content": content,
        "branch": GH_BRANCH,
    }
    if sha:
        body["sha"] = sha

    resp = requests.put(api_url, headers=headers, json=body)
    print("GitHub response status:", resp.status_code)
    print("GitHub response body:", resp.text)
    resp.raise_for_status()
    print("✅ Commit su GitHub completato")

@app.route("/update-fondi", methods=["GET", "POST"])
def update_fondi():
    def job():
        try:
            scrape_fondi_main()
            commit_csv_to_github()
        except Exception as e:
            print("Errore scraping/commit:", e)

    threading.Thread(target=job).start()
    return jsonify({"status": "started"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
