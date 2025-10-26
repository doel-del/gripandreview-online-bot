# app_stream_online.py
"""
Streamlit app: GripAndReview Bot (Online Version)
------------------------------------------------
Fungsi utama:
- Scrape URL atau teks manual
- Ringkas dan ubah menjadi artikel review (Groq / Ollama / fallback)
- Simpan hasil otomatis ke Google Sheets
"""

import os
import json
import time
from typing import Optional

import streamlit as st
import requests
from bs4 import BeautifulSoup

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Local config
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GCP_SERVICE_ACCOUNT_JSON,
    DEFAULT_GROQ_MODEL,
    DEFAULT_SUMMARY_TOKENS,
    DEFAULT_SHEET_NAME,
    OLLAMA_URL,
)

# -------------------- SETUP --------------------
st.set_page_config(page_title="GripAndReview Bot (Online)", layout="centered")
st.title("🧠 GripAndReview — Bot Artikel Online")

# Sidebar status
st.sidebar.header("Integrasi & Status")

st.sidebar.markdown(f"**Groq API Key:** {'✅ OK' if GROQ_API_KEY else '❌ Missing'}")
st.sidebar.markdown(f"**Google Sheets:** {'✅ OK' if GCP_SERVICE_ACCOUNT_JSON else '❌ Missing'}")
st.sidebar.markdown(f"**Ollama URL:** {OLLAMA_URL or '-'}")
sheet_name = st.sidebar.text_input("Google Sheet Name", value=DEFAULT_SHEET_NAME)
st.sidebar.divider()

# -------------------- INPUT --------------------
st.subheader("Input Artikel")
input_type = st.radio("Sumber teks:", ("URL (halaman web)", "Teks manual"))
source_text = ""

if input_type == "URL (halaman web)":
    url = st.text_input("Masukkan URL target:")
    if st.button("🕸️ Scrape halaman"):
        if not url.strip():
            st.warning("Masukkan URL terlebih dahulu.")
        else:
            with st.spinner("Sedang men-scrape halaman..."):
                try:
                    resp = requests.get(url, timeout=15, headers={
                        "User-Agent": "GripAndReviewBot/1.0 (+https://gripandreview.com)"
                    })
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Ambil teks artikel
                    article_tags = soup.find_all(["article"])
                    if article_tags:
                        source_text = "\n\n".join([a.get_text(" ", strip=True) for a in article_tags])
                    else:
                        ps = soup.find_all("p")
                        source_text = "\n\n".join([p.get_text(" ", strip=True) for p in ps])
                    st.text_area("Hasil scrape:", source_text[:5000], height=200)
                except Exception as e:
                    st.error(f"Gagal scrape URL: {e}")
else:
    source_text = st.text_area("Tempel teks artikel di sini:", height=250)

# -------------------- AI SUMMARIZER --------------------
def summarize_with_groq(prompt: str) -> str:
    """Gunakan Groq API (resmi)"""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=GROQ_MODEL or DEFAULT_GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=DEFAULT_SUMMARY_TOKENS,
    )
    return completion.choices[0].message.content.strip()

def summarize_with_ollama(prompt: str) -> str:
    """Fallback jika Ollama diaktifkan"""
    if not OLLAMA_URL:
        raise RuntimeError("OLLAMA_URL belum diset di secrets.")
    payload = {"model": "llama3", "prompt": prompt, "stream": False}
    r = requests.post(f"{OLLAMA_URL.rstrip('/')}/api/generate", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data.get("response") or data.get("output", "")

def simple_fallback_summary(text: str) -> str:
    """Ringkasan manual jika tanpa AI"""
    words = text.split()
    return "(Fallback) " + " ".join(words[:300]) + " ..."

# -------------------- GOOGLE SHEETS --------------------
def get_gsheets_client() -> gspread.Client:
    creds = Credentials.from_service_account_info(
        GCP_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)

def save_to_sheets(sheet_name: str, title: str, url: str, content: str):
    client = get_gsheets_client()
    try:
        sheet = client.open(sheet_name).sheet1
    except Exception:
        sheet = client.create(sheet_name).sheet1
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, title, url, content[:10000]])

# -------------------- GENERATE ARTICLE --------------------
st.subheader("🔧 Generate Artikel")

title = st.text_input("Judul Artikel", "(otomatis jika kosong)")
if st.button("🚀 Buat Artikel"):
    if not source_text.strip():
        st.error("Tidak ada teks untuk diproses.")
    else:
        with st.spinner("Sedang membuat ringkasan artikel..."):
            prompt = (
                "Ringkas konten berikut menjadi artikel review yang padat, natural, "
                "dan berbahasa Indonesia. Gunakan gaya penjelasan teknikal yang ringan, "
                "dengan struktur pembuka, isi, dan kesimpulan.\n\n"
                f"INPUT:\n{source_text}\n\nOUTPUT:\n"
            )
            try:
                if GROQ_API_KEY:
                    summary = summarize_with_groq(prompt)
                elif OLLAMA_URL:
                    summary = summarize_with_ollama(prompt)
                else:
                    summary = simple_fallback_summary(source_text)
            except Exception as e:
                st.error(f"Gagal menjalankan model: {e}")
                summary = simple_fallback_summary(source_text)

            # Tentukan judul otomatis
            if not title.strip():
                title = summary.split("\n")[0][:80]

            article_md = f"# {title}\n\n{summary}"
            st.markdown("### 📝 Hasil Artikel")
            st.markdown(article_md)

            # Simpan ke Google Sheets
            try:
                save_to_sheets(sheet_name, title, url if input_type.startswith("URL") else "", summary)
                st.success(f"✅ Artikel disimpan ke Google Sheets: `{sheet_name}`")
            except Exception as e:
                st.error(f"Gagal menyimpan ke Sheets: {e}")

st.divider()
st.caption("GripAndReview Bot • Powered by Streamlit + Groq + Google Sheets")
