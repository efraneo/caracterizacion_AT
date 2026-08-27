import os
from dotenv import load_dotenv
load_dotenv()

# === APIs ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")

# === Admin ===
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

# === Diseño ===
COLOR_PRIMARY = "#1B2838"
COLOR_ACCENT = "#00D4AA"
COLOR_DANGER = "#FF4757"
COLOR_WARNING = "#FFA502"
COLOR_INFO = "#3742FA"
COLOR_BG = "#0F1923"
COLOR_CARD = "#1B2838"
COLOR_TEXT = "#FFFFFF"
COLOR_SEC = "#8899AA"

# === Paleta gráficos ===
PALETA = [
    "#00D4AA", "#FF4757", "#FFA502", "#3742FA", "#FF6B81",
    "#7BED9F", "#70A1FF", "#ECCC68", "#A29BFE", "#FD79A8"
]
