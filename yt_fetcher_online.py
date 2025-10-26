# yt_fetcher_online.py
"""
GripAndReview Online Bot - YouTube Transcript Fetcher (Cloud-safe)
------------------------------------------------------------------
Versi ringan dan aman untuk Streamlit Cloud dari yt_fetcher_v4_2_stream.py

✅ Tidak menulis file lokal
✅ Semua hasil disimpan di memori (session_state)
✅ Otomatis pakai fallback API jika transcript utama gagal
✅ Kompatibel dengan tab “Scrape Transcript” di app_gripandreview_online.py
"""

import re
import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


# ============================================================
# 🔗 Helper untuk ambil video ID
# ============================================================
def extract_video_id(url: str) -> str:
    """Ekstrak video ID dari berbagai format URL YouTube."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Tidak dapat menemukan video ID dari URL.")


# ============================================================
# 🧠 Fungsi utama: ambil transcript
# ============================================================
def fetch_transcript_online(video_url: str, lang_priority=None, log_ui_placeholder=None) -> str:
    """
    Ambil transcript video dari YouTube.
    Fallback otomatis ke API alternatif jika tidak ditemukan.
    """

    lang_priority = lang_priority or ["id", "en"]
    video_id = extract_video_id(video_url)

    log = (lambda msg: log_ui_placeholder.info(msg)) if log_ui_placeholder else print

    try:
        log(f"📡 Mengambil transcript utama untuk video ID: {video_id}")
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=lang_priority)
        transcript_text = " ".join([t["text"] for t in transcript_data if t["text"].strip()])
        log(f"✅ Transcript ditemukan ({len(transcript_text.split())} kata).")
        return transcript_text

    except TranscriptsDisabled:
        log("⚠️ Transcript dimatikan di video ini. Coba metode fallback (NoteGPT API)...")
    except NoTranscriptFound:
        log("⚠️ Transcript tidak tersedia. Coba metode fallback...")
    except Exception as e:
        log(f"⚠️ Gagal mengambil transcript langsung: {e}")

    # =====================================================
    # 🔁 Fallback 1: NoteGPT Proxy API
    # =====================================================
    try:
        url = f"https://notegpt.io/api/yt/transcript?url={video_url}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and "text" in r.json():
            transcript_text = r.json()["text"]
            log("✅ Transcript berhasil diambil via NoteGPT API.")
            return transcript_text
    except Exception as e:
        log(f"⚠️ Fallback NoteGPT gagal: {e}")

    # =====================================================
    # 🔁 Fallback 2: deskripsi video (opsi terakhir)
    # =====================================================
    try:
        log("📦 Mengambil deskripsi video sebagai fallback terakhir...")
        api_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"
        meta = requests.get(api_url, timeout=10).json()
        transcript_text = meta.get("title", "") + " - " + meta.get("author_name", "")
        log("✅ Menggunakan deskripsi video sebagai fallback.")
        return transcript_text
    except Exception as e:
        log(f"❌ Gagal semua metode transcript: {e}")
        return ""


# ============================================================
# 💾 Helper: Simpan ke session_state
# ============================================================
def save_transcript_to_session(video_url: str, text: str):
    """Simpan hasil transcript di st.session_state agar bisa diakses tab lain."""
    if "transcripts" not in st.session_state:
        st.session_state["transcripts"] = {}
    st.session_state["transcripts"][video_url] = text


# ============================================================
# 🧩 Fungsi utama gabungan
# ============================================================
def fetch_multiple_transcripts(videos, limit=10, lang_priority=None):
    """
    Ambil transcript dari beberapa video sekaligus.
    Digunakan di Tab 1 (Scrape Transcript) app utama.
    """
    if not videos:
        st.warning("Belum ada daftar video untuk diambil transcript-nya.")
        return {}

    st.info(f"📜 Mengambil transcript untuk {min(limit, len(videos))} video...")
    progress = st.progress(0)
    transcripts = {}

    for idx, video in enumerate(videos[:limit]):
        url = video["url"]
        log_placeholder = st.empty()
        text = fetch_transcript_online(url, lang_priority=lang_priority, log_ui_placeholder=log_placeholder)
        transcripts[url] = text
        save_transcript_to_session(url, text)
        progress.progress((idx + 1) / limit)
        log_placeholder.empty()

    st.success(f"✅ {len(transcripts)} transcript berhasil diambil.")
    return transcripts


# ============================================================
# 🧠 Test lokal manual
# ============================================================
if __name__ == "__main__":
    print("Tes fetch transcript...")
    yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    txt = fetch_transcript_online(yt_url)
    print(f"Hasil transcript: {len(txt.split())} kata")
