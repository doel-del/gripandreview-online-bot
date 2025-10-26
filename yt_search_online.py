# yt_search_online.py
"""
GripAndReview Online Bot - YouTube Search (Cloud-safe)
-----------------------------------------------------
Modul ini menggantikan yt_search.py versi offline agar dapat berjalan di Streamlit Cloud.
Perbedaan utama:
✅ Tidak menyimpan file lokal
✅ Semua hasil (video, komentar) dikembalikan dalam bentuk list/dict
✅ Bisa disimpan di st.session_state atau Google Sheets
"""

import re
import streamlit as st
import googleapiclient.discovery
import yt_dlp

# Ambil API key dari Streamlit Secrets / config
try:
    from config import YOUTUBE_API_KEY
except Exception:
    YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY")

# ============================================================
# 🔍 Fungsi: Search YouTube Video
# ============================================================

def search_youtube_online(query: str, max_results: int = 10):
    """
    Cari video YouTube berdasarkan keyword.
    Menggunakan YouTube Data API v3.
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("❌ YOUTUBE_API_KEY tidak ditemukan di secrets/config.py")

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
        relevanceLanguage="id",
        safeSearch="moderate",
    )
    response = request.execute()

    results = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        title = snippet["title"]
        channel = snippet["channelTitle"]
        description = snippet.get("description", "")
        publish_date = snippet["publishedAt"].split("T")[0]

        # Ambil statistik video (views, comment count)
        stats_req = youtube.videos().list(part="statistics,contentDetails", id=video_id)
        stats_res = stats_req.execute()
        stats = stats_res["items"][0]["statistics"]

        results.append({
            "judul": title,
            "channel": channel,
            "upload_date": publish_date,
            "views": int(stats.get("viewCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "subtitle": "❌",  # akan di-update di yt_fetcher_online
        })

    return results


# ============================================================
# 💬 Fungsi: Download Komentar (Cloud Version)
# ============================================================

def fetch_comments_online(video_url: str, max_comments: int = 100):
    """
    Ambil komentar video YouTube menggunakan yt_dlp.
    Dikembalikan sebagai list of string (tanpa file lokal).
    """
    opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "getcomments": True,
    }

    comments_list = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            comments = info.get("comments", [])
            for c in comments[:max_comments]:
                text = c.get("text", "").strip()
                author = c.get("author", "Anonim")
                if text:
                    comments_list.append(f"{author}: {text}")
    except Exception as e:
        st.warning(f"⚠️ Gagal mengambil komentar dari {video_url}: {e}")

    return comments_list


# ============================================================
# 🧠 Helper: Simpan ke Session State
# ============================================================

def save_results_to_session(videos, comments_dict=None):
    """
    Simpan hasil pencarian & komentar ke Streamlit session_state
    agar tab lain (transcript, summarizer) bisa mengaksesnya.
    """
    if "videos" not in st.session_state:
        st.session_state["videos"] = videos
    if comments_dict:
        st.session_state["comments"] = comments_dict


# ============================================================
# 🔍 Test Cepat (jalankan manual di lokal)
# ============================================================
if __name__ == "__main__":
    print("Tes pencarian YouTube...")
    vids = search_youtube_online("bor listrik cordless", max_results=3)
    for v in vids:
        print(f"- {v['judul']} | {v['url']}")
    if vids:
        comm = fetch_comments_online(vids[0]["url"])
        print(f"\nKomentar pertama ({len(comm)}):")
        print("\n".join(comm[:5]))
