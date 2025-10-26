# app_gripandreview_online.py
"""
GripAndReview Online Bot (v5)
------------------------------
Versi Streamlit Cloud yang sudah aktif untuk:
1️⃣ Scrape Transcript
2️⃣ Scrape Comments

Selanjutnya akan diintegrasikan:
3️⃣ Generate Articles (Groq)
4️⃣ Combine Articles
5️⃣ Render Template HTML
"""

import streamlit as st
import time

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GCP_SERVICE_ACCOUNT_JSON,
    DEFAULT_SHEET_NAME,
)

# Import modul pencarian & fetcher (versi online)
from yt_search_online import (
    search_youtube_online,
    fetch_comments_online,
    save_results_to_session,
)
from yt_fetcher_online import fetch_multiple_transcripts

# ======================================
# ⚙️ SETUP
# ======================================
st.set_page_config(page_title="GripAndReview Online Bot", page_icon="🤖", layout="wide")

st.title("🤖 GripAndReview AI — Online Bot (v5.1)")
st.caption("YouTube Review Automation • Streamlit Cloud + Groq + Google Sheets")

# Sidebar status
st.sidebar.header("Integrasi")
st.sidebar.markdown(f"**Groq API Key:** {'✅ OK' if GROQ_API_KEY else '❌ Missing'}")
st.sidebar.markdown(f"**Google Sheets:** {'✅ OK' if GCP_SERVICE_ACCOUNT_JSON else '❌ Missing'}")
st.sidebar.markdown(f"**Default Sheet:** `{DEFAULT_SHEET_NAME}`")
st.sidebar.divider()
st.sidebar.info("Tab 1 & 2 sudah aktif (scrape YouTube transcript dan komentar).")

# ======================================
# 🧩 TAB SETUP
# ======================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎬 Scrape Transcript",
    "💬 Scrape Comments",
    "🧠 Generate Articles",
    "📰 Combine Articles",
    "🧩 Render Template"
])

# ======================================
# TAB 1 — 🎬 Scrape Transcript
# ======================================
with tab1:
    st.header("🎬 Scrape Transcript (YouTube)")

    st.info("Ambil daftar video dan transcript dari YouTube (maksimal 20 video).")

    keyword = st.text_input("🔎 Masukkan keyword pencarian:", "")
    limit = st.slider("Jumlah video:", 5, 20, 10)

    if st.button("🚀 Cari Video di YouTube"):
        if not keyword.strip():
            st.warning("Masukkan keyword terlebih dahulu.")
        else:
            with st.spinner(f"Mencari '{keyword}' di YouTube..."):
                try:
                    results = search_youtube_online(keyword, max_results=limit)
                    save_results_to_session(results)
                    st.session_state["videos"] = results
                    st.success(f"✅ Ditemukan {len(results)} video.")
                except Exception as e:
                    st.error(f"❌ Gagal mencari video: {e}")

    if "videos" in st.session_state:
        videos = st.session_state["videos"]
        st.subheader("📋 Daftar Video Ditemukan:")
        st.dataframe(videos)

        if st.button("📜 Ambil Transcript Semua Video"):
            with st.spinner("Mengambil transcript..."):
                transcripts = fetch_multiple_transcripts(videos, limit=len(videos))
            st.session_state["transcripts"] = transcripts
            st.success(f"✅ {len(transcripts)} transcript berhasil diambil.")

        if "transcripts" in st.session_state:
            st.subheader("📖 Contoh Transcript (1 Video):")
            any_url = list(st.session_state["transcripts"].keys())[0]
            st.text_area("Sample Transcript", st.session_state["transcripts"][any_url][:1000], height=250)

    else:
        st.warning("Belum ada hasil pencarian. Jalankan pencarian dulu.")

# ======================================
# TAB 2 — 💬 Scrape Comments
# ======================================
with tab2:
    st.header("💬 Scrape Comments")

    st.info("Ambil komentar YouTube dari daftar video yang sudah ditemukan di Tab 1.")
    max_comments = st.slider("Maksimum komentar per video", 10, 200, 50, step=10)

    if "videos" not in st.session_state:
        st.warning("Belum ada video. Jalankan pencarian dulu di Tab 1.")
    else:
        videos = st.session_state["videos"]
        if st.button("⬇️ Ambil Komentar Semua Video"):
            all_comments = {}
            progress = st.progress(0)
            for idx, v in enumerate(videos):
                st.write(f"📥 Mengambil komentar dari: {v['judul']}")
                comments = fetch_comments_online(v["url"], max_comments=max_comments)
                all_comments[v["url"]] = comments
                progress.progress((idx + 1) / len(videos))
            st.session_state["comments"] = all_comments
            st.success(f"✅ Komentar berhasil diambil dari {len(all_comments)} video.")

        if "comments" in st.session_state:
            st.subheader("🗨️ Contoh Komentar (1 Video):")
            any_url = list(st.session_state["comments"].keys())[0]
            sample_comments = "\n".join(st.session_state["comments"][any_url][:10])
            st.text_area("Sample Comments", sample_comments, height=200)

# ======================================
# TAB 3 — 🧠 Generate Articles (coming soon)
# ======================================
with tab3:
    st.header("🧠 Generate Articles (AI)")
    st.info("Akan menggunakan Groq API untuk membuat artikel otomatis dari transcript + komentar.")
    st.write("💤 Fitur ini akan diaktifkan setelah Tab 1 & 2 stabil.")

# ======================================
# TAB 4 — 📰 Combine Articles (coming soon)
# ======================================
with tab4:
    st.header("📰 Combine Articles")
    st.info("Akan menggabungkan artikel menjadi satu kesatuan menggunakan AI.")
    st.write("💤 Fitur ini akan diaktifkan setelah modul summarizer siap.")

# ======================================
# TAB 5 — 🧩 Render Template HTML (coming soon)
# ======================================
with tab5:
    st.header("🧩 Render Template HTML")
    st.info("Akan mengubah hasil gabungan artikel menjadi template HTML siap posting.")
    st.write("💤 Fitur ini akan diaktifkan setelah renderer AI selesai.")

# ======================================
# 🧭 FOOTER
# ======================================
st.divider()
st.caption("GripAndReview Online Bot — powered by Streamlit Cloud + Groq + Google Sheets")
