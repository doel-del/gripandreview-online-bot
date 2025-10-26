# app_gripandreview_online.py
"""
GripAndReview Online Bot (Base Structure)
----------------------------------------
Versi awal Streamlit Cloud (online) dari YouTube Review Bot.
Menampilkan 5 tab utama seperti versi offline:
1️⃣ Scrape Transcript
2️⃣ Scrape Comments
3️⃣ Generate Articles
4️⃣ Combine Articles
5️⃣ Render Template HTML
"""

import streamlit as st
import os
import time
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GCP_SERVICE_ACCOUNT_JSON,
    DEFAULT_SHEET_NAME
)

# ======================================
# ⚙️ SETUP APLIKASI
# ======================================
st.set_page_config(page_title="GripAndReview Online Bot", page_icon="🤖", layout="wide")

st.title("🤖 GripAndReview AI — Online Bot (v5 Base)")

# --- Sidebar Status ---
st.sidebar.header("Integrasi")
st.sidebar.markdown(f"**Groq API Key:** {'✅ OK' if GROQ_API_KEY else '❌ Missing'}")
st.sidebar.markdown(f"**Google Sheets:** {'✅ OK' if GCP_SERVICE_ACCOUNT_JSON else '❌ Missing'}")
st.sidebar.markdown(f"**Default Sheet:** `{DEFAULT_SHEET_NAME}`")
st.sidebar.divider()
st.sidebar.info("Versi dasar ini sudah siap untuk integrasi scraping, summarizer, dan rendering.")

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

    st.info("Fitur ini akan mengambil transcript dari maksimal 20 video YouTube.")
    keyword = st.text_input("Masukkan keyword pencarian (contoh: bor cordless 13mm):")
    limit = st.slider("Jumlah video", 5, 20, 10)

    if st.button("🔍 Cari Video"):
        if not keyword.strip():
            st.warning("Masukkan keyword terlebih dahulu.")
        else:
            with st.spinner("Mencari video di YouTube..."):
                # TODO: integrasikan fungsi search_youtube() dan fetch_transcript()
                time.sleep(1)
            st.success(f"✅ Dummy hasil: {limit} video ditemukan (nanti diganti hasil asli).")

    st.divider()
    st.markdown("📥 Setelah video dipilih, tombol *Download Transcript* akan aktif di versi berikutnya.")

# ======================================
# TAB 2 — 💬 Scrape Comments
# ======================================
with tab2:
    st.header("💬 Scrape Comments")

    st.info("Fitur ini akan mengunduh komentar YouTube dari video yang dipilih di Tab 1.")
    if st.button("⬇️ Download Komentar (dummy)"):
        with st.spinner("Mengambil komentar..."):
            time.sleep(1)
        st.success("✅ Dummy komentar 20 video berhasil diunduh (fitur asli segera ditambahkan).")

# ======================================
# TAB 3 — 🧠 Generate Articles
# ======================================
with tab3:
    st.header("🧠 Generate Artikel AI")

    st.info("Tab ini akan membuat artikel dari transcript + komentar (max 20 video).")
    model = st.selectbox("Pilih model Groq", [GROQ_MODEL, "llama-3-8b", "llama-3-70b"])
    token_limit = st.number_input("Max token ringkasan", 128, 2048, 512, step=64)
    if st.button("🚀 Generate Artikel AI (dummy)"):
        with st.spinner("Memproses dengan Groq..."):
            time.sleep(2)
        st.success(f"✅ 20 artikel berhasil dibuat (dummy, model: {model})")

    st.divider()
    st.markdown("Output akan disimpan otomatis ke Google Sheets setelah integrasi selesai.")

# ======================================
# TAB 4 — 📰 Combine Articles
# ======================================
with tab4:
    st.header("📰 Combine Articles")

    st.info("Tab ini akan menggabungkan semua artikel agar saling melengkapi dengan bantuan AI.")
    if st.button("🧩 Combine Semua Artikel (dummy)"):
        with st.spinner("Menggabungkan artikel dengan AI..."):
            time.sleep(2)
        st.success("✅ Artikel gabungan berhasil dibuat (dummy).")

    st.text_area("Hasil gabungan sementara (dummy):", "Artikel gabungan akan muncul di sini...", height=250)

# ======================================
# TAB 5 — 🧩 Render Template HTML
# ======================================
with tab5:
    st.header("🧩 Renderer (Template HTML)")

    st.info("Tab ini akan merender artikel gabungan menjadi template HTML final (siap posting).")

    template_name = st.text_input("Nama template:", "default_template.html")
    if st.button("🧠 Render HTML (dummy)"):
        with st.spinner("Membuat template HTML..."):
            time.sleep(1)
        st.success(f"✅ Template `{template_name}` berhasil dibuat (dummy).")

    st.code("""
    <article>
      <h1>Judul Artikel Gabungan</h1>
      <p>Konten hasil renderer AI akan muncul di sini...</p>
    </article>
    """, language="html")

# ======================================
# 🧭 FOOTER
# ======================================
st.divider()
st.caption("GripAndReview Online Bot — powered by Streamlit Cloud + Groq + Google Sheets")
