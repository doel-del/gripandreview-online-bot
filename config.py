# config.py
"""
Konfigurasi utama Bot Artikel GripAndReview (Online)
----------------------------------------------------
File ini memuat pengaturan dasar untuk:
- Koneksi ke Groq API (AI model)
- Autentikasi Google Service Account (akses Google Sheets)
- Fallback ke Ollama jika Groq tidak tersedia
"""

import os
import json

# Coba impor Streamlit untuk akses secrets (jika dijalankan di Streamlit Cloud)
try:
    import streamlit as st
    _SECRETS = st.secrets
except Exception:
    _SECRETS = {}

# ================================
# 🔧 1️⃣ KONFIGURASI DEFAULT
# ================================
DEFAULT_GROQ_MODEL = "llama-3b"          # bisa diganti sesuai model Groq kamu
DEFAULT_SUMMARY_TOKENS = 512
DEFAULT_SHEET_NAME = "GripAndReview_Articles"
DEFAULT_OLLAMA_MODEL = "llama3"

# ================================
# 🔐 2️⃣ API KEY & CREDENTIALS
# ================================
# Membaca Groq API Key (utama)
GROQ_API_KEY = (
    _SECRETS.get("GROQ_API_KEY") or
    os.getenv("GROQ_API_KEY")
)

# Membaca Groq model name
GROQ_MODEL = (
    _SECRETS.get("GROQ_MODEL") or
    DEFAULT_GROQ_MODEL
)

# Membaca JSON Service Account Google
GCP_SERVICE_ACCOUNT_JSON = None
if "gcp_service_account" in _SECRETS:
    try:
        GCP_SERVICE_ACCOUNT_JSON = json.loads(_SECRETS["gcp_service_account"])
    except Exception as e:
        print(f"[config] ⚠️ Error membaca gcp_service_account dari secrets: {e}")

# ================================
# 🧩 3️⃣ OPSIONAL - FALLBACK OLLAMA
# ================================
OLLAMA_URL = (
    _SECRETS.get("OLLAMA_URL") or
    os.getenv("OLLAMA_URL") or
    None
)

# ================================
# 🧭 4️⃣ RINGKASAN STATUS
# ================================
def config_status():
    """Menampilkan status konfigurasi di terminal atau log"""
    print("=== CONFIG STATUS ===")
    print(f"GROQ_API_KEY   : {'✅ OK' if GROQ_API_KEY else '❌ Missing'}")
    print(f"GROQ_MODEL     : {GROQ_MODEL}")
    print(f"GCP_CREDENTIALS: {'✅ OK' if GCP_SERVICE_ACCOUNT_JSON else '❌ Missing'}")
    print(f"Ollama Fallback: {OLLAMA_URL or '-'}")
    print(f"Default Sheet  : {DEFAULT_SHEET_NAME}")
    print("=====================")


# Jalankan pengecekan otomatis jika file ini dipanggil langsung
if __name__ == "__main__":
    config_status()
