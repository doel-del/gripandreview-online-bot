
# app_stream_online.py
"""
Streamlit app: GripAndReview Bot (basic online version)
Features:
- Scrape a URL (simple HTML text extraction)
- Summarize using Groq (preferred) or Ollama (fallback if configured)
- Combine / Render a short article
- Save result to Google Sheets (via gspread + service account JSON passed in Streamlit secrets)
"""

import os
import json
import time
from typing import Optional

import streamlit as st
import requests
from bs4 import BeautifulSoup

# AI provider: groq library if available
try:
    import groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

# Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except Exception:
    HAS_GSPREAD = False

# local config
from config import (
    DEFAULT_GROQ_MODEL,
    DEFAULT_SUMMARY_TOKENS,
    DEFAULT_SHEET_NAME,
)

st.set_page_config(page_title="GripAndReview Bot (Online)", layout="centered")

st.title("GripAndReview — Bot Artikel (Online)")

# --- Sidebar: settings & secrets checks ---
st.sidebar.header("Settings & Integrations")

use_groq = st.sidebar.checkbox("Use Groq (if API key configured)", value=True)
use_ollama = st.sidebar.checkbox("Use Ollama (fallback)", value=False)

st.sidebar.markdown("**Output storage**")
sheet_name = st.sidebar.text_input("Google Sheet name", value=DEFAULT_SHEET_NAME)

st.sidebar.markdown("---")
st.sidebar.markdown("**Integration status**")
st.sidebar.write(f"groq client installed: {HAS_GROQ}")
st.sidebar.write(f"gspread available: {HAS_GSPREAD}")

# --- Input: URL or plain text ---
st.subheader("Input")
input_type = st.radio("Scrape from:", ("URL (page)", "Paste text"))

source_text = ""
if input_type == "URL (page)":
    url = st.text_input("Target URL (http/https)", "")
    if st.button("Scrape & Summarize"):
        if not url.strip():
            st.error("Masukkan URL terlebih dahulu.")
        else:
            with st.spinner("Scraping..."):
                try:
                    resp = requests.get(url, timeout=15, headers={
                        "User-Agent": "gripandreview-bot/1.0 (+https://gripandreview.com)"
                    })
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Basic article extraction heuristics
                    article_tags = soup.find_all(["article"])
                    if article_tags:
                        source_text = "\n\n".join([t.get_text(separator=" ", strip=True) for t in article_tags])
                    else:
                        # fallback: join all <p>
                        ps = soup.find_all("p")
                        source_text = "\n\n".join([p.get_text(separator=" ", strip=True) for p in ps])
                    if not source_text.strip():
                        st.warning("Tidak menemukan teks artikel yang signifikan. Coba URL lain atau gunakan paste text.")
                except Exception as e:
                    st.error(f"Error scraping URL: {e}")
else:
    source_text = st.text_area("Paste article text here", height=250)

# --- Summarization / generation helpers ---
def generate_with_groq(prompt: str, model: str = DEFAULT_GROQ_MODEL, max_tokens: int = DEFAULT_SUMMARY_TOKENS) -> str:
    """
    Use Groq Python SDK (if installed) to create a completion/chat. 
    Requires env var: GROQ_API_KEY (or set up according to Groq docs).
    """
    if not HAS_GROQ:
        raise RuntimeError("Groq library not installed in environment.")
    # Example using groq Python package (API may vary across versions).
    # This minimal wrapper uses ChatCompletion-like interface used in examples.
    from groq.cloud.core import ChatCompletion
    with ChatCompletion(model) as chat:
        response, *_ = chat.send_chat(prompt)
        return response

def generate_with_ollama(prompt: str, model: str = "llama2", max_tokens: int = 512, ollama_url: Optional[str] = None) -> str:
    """
    Call Ollama HTTP API. Expects OLLAMA_URL like 'http://HOST:11434' or use 'http://localhost:11434'.
    Endpoint used: /api/generate
    """
    if not ollama_url:
        raise RuntimeError("OLLAMA_URL not configured.")
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "stream": False
    }
    r = requests.post(f"{ollama_url.rstrip('/')}/api/generate", json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Ollama returns structure with 'result' or 'choices' depending on version — we try a couple patterns
    if isinstance(data, dict):
        if "result" in data and isinstance(data["result"], str):
            return data["result"]
        if "choices" in data and data["choices"]:
            return data["choices"][0].get("content", "") or data["choices"][0].get("message", {}).get("content", "")
    return json.dumps(data)  # fallback

def compose_article(title: str, summary: str, source_url: Optional[str]) -> str:
    header = f"# {title}\n\n"
    meta = f"_Sumber: {source_url}_\n\n" if source_url else ""
    return header + meta + summary

# --- Google Sheets helpers ---
def gsheets_client_from_streamlit_secrets() -> gspread.Client:
    """
    Create a gspread client using service_account info provided via Streamlit secrets.
    In Streamlit Community Cloud -> Secrets, store a key: "gcp_service_account" with JSON text value.
    Example secrets.toml:
    gcp_service_account = '''{"type": "...", "project_id": "...", ...}'''
    """
    if not HAS_GSPREAD:
        raise RuntimeError("gspread/google-auth not installed.")
    raw = st.secrets.get("gcp_service_account", None)
    if not raw:
        raise RuntimeError("Google service account credentials not found in Streamlit secrets (gcp_service_account).")
    # allow both dict or JSON string
    if isinstance(raw, dict):
        info = raw
    else:
        info = json.loads(raw)
    creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

def append_to_sheet(sheet_name: str, data_row: list):
    client = gsheets_client_from_streamlit_secrets()
    sheet = None
    try:
        spreadsheet = client.open(sheet_name)
    except Exception:
        # create new sheet (requires Drive API permission; if not allowed, user must pre-create)
        spreadsheet = client.create(sheet_name)
    # open first worksheet
    worksheet = spreadsheet.sheet1
    worksheet.append_row(data_row)

# --- Main action: summarize + save ---
st.subheader("Generate article")

title = st.text_input("Judul artikel (singkat)", value="(otomatis jika kosong)")

if st.button("Generate Article") or (input_type == "URL (page)" and source_text and st.session_state.get("auto_generate", False)):
    if not source_text.strip():
        st.error("Tidak ada teks yang bisa diproses.")
    else:
        with st.spinner("Menyusun prompt & memanggil model..."):
            # build prompt
            prompt = (
                "Ringkas konten berikut menjadi artikel review singkat 6-10 paragraf. "
                "Buat bahasa Indonesia yang enak dibaca, poin penting, dan kesimpulan akhir. "
                "Jangan sertakan terlalu banyak kutipan; gunakan gaya friendly teknikal.\n\n"
                f"INPUT:\n{source_text}\n\nOUTPUT:\n"
            )
            ai_output = ""
            # Try Groq first if enabled
            try:
                if use_groq and HAS_GROQ and os.getenv("GROQ_API_KEY"):
                    ai_output = generate_with_groq(prompt, model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL))
                elif use_ollama and os.getenv("OLLAMA_URL"):
                    ai_output = generate_with_ollama(prompt, model=os.getenv("OLLAMA_MODEL", "llama3"), ollama_url=os.getenv("OLLAMA_URL"))
                else:
                    # fallback: naive simple summarizer (if no model configured)
                    ai_output = ("(Fallback) Ringkasan otomatis: " + " ".join(source_text.split()[:250]) + " ...")
            except Exception as e:
                st.error(f"Gagal memanggil model: {e}")
                ai_output = ("(Error) Tidak dapat menghasilkan ringkasan karena masalah integrasi model.")
            # title default
            if not title.strip():
                # pick first sentence as title heuristic
                title = ai_output.split("\n")[0][:80] if ai_output else "Artikel GripAndReview"
            article = compose_article(title, ai_output, url if input_type.startswith("URL") else None)

            st.markdown("### Hasil Artikel (preview)")
            st.code(article, language="markdown")
            st.success("Selesai membuat artikel.")

            # Save to Google Sheets
            st.info("Menyimpan ke Google Sheets...")
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                row = [timestamp, title, url if input_type.startswith("URL") else "", ai_output[:10000]]
                append_to_sheet(sheet_name, row)
                st.success(f"Disimpan ke Google Sheet: {sheet_name}")
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheets: {e}\nPastikan service account punya akses edit ke sheet tersebut.")

st.markdown("---")
st.markdown("**Catatan integrasi:**")
st.markdown("- Untuk Groq: atur `GROQ_API_KEY` di Streamlit secrets; contoh variable `GROQ_API_KEY` dan optional `GROQ_MODEL` (mis. `llama-3b`/`llama-3-8k`).").markdown("")
st.markdown("- Untuk Ollama (fallback): atur `OLLAMA_URL` (contoh: `http://<host>:11434`) dan `OLLAMA_MODEL`.")
st.markdown("- Untuk Google Sheets: simpan JSON credentials service account di `gcp_service_account` di Streamlit secrets (isi JSON sebagai string).")

