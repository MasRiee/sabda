import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class CameraFeed(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Hapus fixed size — isi penuh parent widget
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy(),
        )
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #000;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # State overlay
        self._word = ""
        self._correction = ""
        self._correction_correct = None   # True/False/None
        self._waveform_data = None        # np.ndarray audio chunk
        self._nav_left = "< PREV"
        self._nav_right = "NEXT >"

   
    def set_word(self, word: str):
        self._word = word.upper()

    def set_correction(self, text: str, correct: bool = None):
        self._correction = text
        self._correction_correct = correct

    def set_waveform(self, audio_chunk):
        self._waveform_data = audio_chunk

    def update_frame(self, frame_bgr):
        frame = frame_bgr.copy()
        h, w = frame.shape[:2]

        # Kata target
        if self._word:
            word_text = self._word
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.0
            thickness = 3
            (tw, th), baseline = cv2.getTextSize(word_text, font, font_scale, thickness)
            tx = (w - tw) // 2
            ty = th + 30
            # Shadow gelap supaya terbaca di background apapun
            cv2.putText(frame, word_text, (tx + 2, ty + 2), font,
                        font_scale, (0, 0, 0), thickness + 2)
            cv2.putText(frame, word_text, (tx, ty), font,
                        font_scale, (255, 255, 255), thickness)

        # Teks koreksi
        if self._correction:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.9
            thickness = 2
            color = (
                (0, 220, 80) if self._correction_correct is True
                else (80, 80, 255) if self._correction_correct is False
                else (200, 200, 200)
            )
            (cw, ch), _ = cv2.getTextSize(self._correction, font, font_scale, thickness)
            cx = (w - cw) // 2
            cy = h - 30
            cv2.putText(frame, self._correction, (cx + 2, cy + 2), font,
                        font_scale, (0, 0, 0), thickness + 2)
            cv2.putText(frame, self._correction, (cx, cy), font,
                        font_scale, color, thickness)

        # gelombang audio
        if self._waveform_data is not None and len(self._waveform_data) > 0:
            self._draw_waveform(frame, x=10, y=h - 120, width=180, height=80)

        # Navigasi
        font = cv2.FONT_HERSHEY_SIMPLEX
        nav_scale = 0.5
        nav_thickness = 2
        nav_y = h // 2

        # Tombol kiri
        cv2.putText(frame, self._nav_left, (20 + 2, nav_y + 2), font,
                    nav_scale, (0, 0, 0), nav_thickness + 2)
        cv2.putText(frame, self._nav_left, (20, nav_y), font,
                    nav_scale, (255, 255, 255), nav_thickness)

        # Tombol kanan
        (rw, _), _ = cv2.getTextSize(self._nav_right, font, nav_scale, nav_thickness)
        rx = w - rw - 20
        cv2.putText(frame, self._nav_right, (rx + 2, nav_y + 2), font,
                    nav_scale, (0, 0, 0), nav_thickness + 2)
        cv2.putText(frame, self._nav_right, (rx, nav_y), font,
                    nav_scale, (255, 255, 255), nav_thickness)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qh, qw, ch = rgb.shape
        qimg = QImage(rgb.data, qw, qh, ch * qw, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pixmap)

    def _draw_waveform(self, frame, x, y, width, height):
        """Gambar waveform audio sederhana di pojok kiri bawah."""
        data = self._waveform_data
        # Normalisasi ke rentang tinggi waveform
        data_norm = data.astype(np.float32)
        max_val = np.max(np.abs(data_norm)) or 1
        data_norm = data_norm / max_val * (height // 2)

        # Background semi-transparan
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + width, y + height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        # Gambar garis waveform
        n = len(data_norm)
        mid_y = y + height // 2
        for i in range(1, min(n, width)):
            x1 = x + i - 1
            x2 = x + i
            y1 = int(mid_y - data_norm[int((i - 1) * n / width)])
            y2 = int(mid_y - data_norm[int(i * n / width)])
            y1 = max(y, min(y + height, y1))
            y2 = max(y, min(y + height, y2))
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 128), 1)