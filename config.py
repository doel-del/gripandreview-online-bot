# config.py
# Minimal configuration constants

# Default Groq model name (tweak to your Groq account/models)
DEFAULT_GROQ_MODEL = "llama-3b"   # contoh: "llama-3b" atau "llama-3-8k" (sesuaikan akun Groq)
DEFAULT_SUMMARY_TOKENS = 512

# Default Google Sheet name (will create if doesn't exist, depending on permissions)
DEFAULT_SHEET_NAME = "GripAndReview_Articles"

# Ollama default (only used if OLLAMA_URL provided via env/secrets)
DEFAULT_OLLAMA_MODEL = "llama3"

