"""
screen.py — Layar utama

Navigasi: LEFT/RIGHT (keyboard saat mock, atau joystick fisik nanti) untuk
pindah kata sebelumnya/berikutnya
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.camera_feed import CameraFeed


class Screen(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller

        # Layout tanpa margin — kamera isi penuh window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.camera_feed = CameraFeed()
        layout.addWidget(self.camera_feed)

    # ------------------------------------------------------------------
    # Dipanggil dari main_window.py, disambungkan ke signal AppController
    # ------------------------------------------------------------------
    def set_word(self, word: str):
        self.camera_feed.set_word(word)
        self.camera_feed.set_correction("Ucapkan kata di atas...", correct=None)

    def update_frame(self, frame_bgr):
        self.camera_feed.update_frame(frame_bgr)

    def set_face_detected(self, detected: bool):
        # Face status sekarang ditampilkan lewat warna overlay
        # Tidak perlu QLabel terpisah lagi
        pass

    def update_correction(self, result: dict):
        predicted = result["predicted_word"].upper()
        confidence_pct = result["confidence"] * 100
        if result["correct"]:
            text = f"BENAR: {predicted} ({confidence_pct:.0f}%)"
        else:
            text = f"Terdeteksi: {predicted} ({confidence_pct:.0f}%)"
        self.camera_feed.set_correction(text, correct=result["correct"])

    def update_waveform(self, audio_data):
        if isinstance(audio_data, dict):
            # Ambil numpy array mentah dari dictionary hasil olahan DSP
            audio_chunk = audio_data.get("raw_chunk")
            # (Opsional) Jika nanti ingin menampilkan nilai pitch di UI:
            # pitch_hz = audio_data.get("pitch", 0.0)
        else:
            audio_chunk = audio_data

        if audio_chunk is not None:
            self.camera_feed.set_waveform(audio_chunk)