"""
config.py — Konfigurasi global SABDA

Semua value yang berbeda antar environment (Windows dev laptop <-> MiniPC Linux)
DIPUSATKAN di sini. Jangan hardcode device index / path / port di file lain.

Saat pindah dari Windows ke MiniPC (Linux), yang perlu diubah HANYA file ini.
"""

import platform
from pathlib import Path

# ── Base paths (otomatis cross-platform, jangan pakai backslash manual) ────
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
ASSETS_DIR = BASE_DIR / "assets"
WORDS_FILE = ASSETS_DIR / "words" / "word_list.json"

# ── File model, HARUS sama dengan output notebook (Step 2, 15) ────────────
FACE_LANDMARKER_MODEL_FILE = MODEL_DIR / "face_landmarker.task"   # dari Step 2
WORD_CLASSIFIER_FILE = MODEL_DIR / "word_classifier.keras"        # dari Step 15
WORD_LABELS_FILE = MODEL_DIR / "word_labels.json"                 # dari Step 15
FACE_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)

# ── Mode pengembangan tanpa hardware / model asli ──────────────────────────
# Set False satu per satu begitu komponen aslinya sudah siap & tersambung.
HARDWARE_MOCK_MODE = False  # False = pakai kamera & mikrofon LAPTOP ASLI (motor getar/joystick tetap disimulasikan karena belum ada mikrokontroler tersambung — lihat catatan di haptic.py/joystick.py)
MODEL_MOCK_MODE = False     # True = prediksi kata di-random / dummy (tanpa model GRU terlatih) — ganti False begitu word_classifier.h5 & face_landmarker.task sudah ada di folder model/

# ── Kamera ──────────────────────────────────────────────────────────────
CAMERA_INDEX = 0            # index device webcam. Cek ulang tiap pindah OS (Windows/Linux beda urutan)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_TARGET_FPS = 30

# ── Landmark & fitur bibir — HARUS PERSIS SAMA dengan notebook (Step 3 & 9) ─
# Kalau ini berbeda dari yang dipakai saat training, fitur tidak akan valid.
LIP_POINTS = {
    "left_corner_outer": 61,
    "right_corner_outer": 291,
    "upper_inner": 13,
    "lower_inner": 14,
    "upper_outer": 0,
    "lower_outer": 17,
    "left_corner_inner": 78,
    "right_corner_inner": 308,
}

REF_POINTS = {
    "left_eye_outer": 33,
    "right_eye_outer": 263,
}

# 40 titik kontur bibir (20 luar + 20 dalam) — sama seperti Step 9 di notebook
LIP_CONTOUR_POINTS = [
    # kontur luar
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
    146, 91, 181, 84, 17, 314, 405, 321, 375,
    # kontur dalam
    78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308,
    95, 88, 178, 87, 14, 317, 402, 318, 324,
]

# Dimensi fitur per frame: (x, y) tiap titik kontur + MAR + Roundness + Protrusion
FEATURE_DIM = len(LIP_CONTOUR_POINTS) * 2 + 3  # = 83

# ── Sliding window sequence — HARUS SAMA dengan TARGET_LEN saat training (Step 12) ─
SEQUENCE_LENGTH = 24
PREDICTION_INTERVAL_FRAMES = 5           # sesuai live_word_predictor di notebook
PREDICTION_CONFIDENCE_THRESHOLD = 0.4    # sesuai threshold di notebook

DEFAULT_TARGET_WORDS = ["kucing", "babi", "daun"]

# ── Mikrofon ─────────
MIC_SAMPLE_RATE = 16000
MIC_CHUNK_SIZE = 1024

JOYSTICK_POLL_INTERVAL_MS = 50

# ── UI ──────────────────────────────────────────────────────────────────
UI_FULLSCREEN = False        # set True saat deploy ke LCD di MiniPC
UI_WINDOW_TITLE = "SABDA"
UI_WINDOW_SIZE = (1024, 600)  # dipakai kalau UI_FULLSCREEN = False (dev mode di laptop)
