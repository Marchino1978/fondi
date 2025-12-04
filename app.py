# app.py
from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.get("/healthz")
def healthz():
  return jsonify({"status": "ok"})

@app.post("/update-fondi")
def update_fondi():
  try:
    # Esegue lo script di scraping
    subprocess.check_call(["python", "scrape_fondi.py"])
    # Opzionale: salva output in una cartella pubblica o invia commit a GitHub (vedi sotto)
    return jsonify({"status": "updated"}), 200
  except subprocess.CalledProcessError as e:
    return jsonify({"status": "error", "detail": str(e)}), 500
