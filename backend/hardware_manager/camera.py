"""
camera.py — Capture kamera di thread terpisah, ekstraksi fitur bibir via
LipReadingModel (FaceLandmarker Tasks API), dan trigger prediksi kata
begitu sliding window siap.

Jalan sebagai QThread supaya UI (PyQt6) tidak nge-freeze saat kamera aktif.

Alur (mirip live_word_predictor di notebook Step 16, tapi jalan lokal
di MiniPC/laptop, bukan lewat webcam browser Colab):
    setiap frame -> extract_features() -> push ke FrameBuffer
    setiap PREDICTION_INTERVAL_FRAMES & buffer penuh -> predict()
"""

from __future__ import annotations

import time

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

import config
from backend.model_manager.lip_reading import LipReadingModel
from backend.hardware_manager.frame_buffer import FrameBuffer


class CameraWorker(QThread):
    """
    Signals:
        frame_ready(np.ndarray): frame BGR mentah, untuk live preview di UI
        face_status_changed(bool): True/False wajah terdeteksi di frame saat ini
        prediction_ready(str, float): (kata, confidence) begitu ada prediksi baru
        error(str): pesan error kalau kamera/model gagal dibuka
    """

    frame_ready = pyqtSignal(np.ndarray)
    face_status_changed = pyqtSignal(bool)
    prediction_ready = pyqtSignal(str, float)
    error = pyqtSignal(str)

    def __init__(self, model: LipReadingModel = None, parent=None):
        super().__init__(parent)
        self._run_flag = True
        self._capturing = False  # True saat state LISTENING, buffer diisi & prediksi jalan
        self._buffer = FrameBuffer()
        self._model = model  # kalau None, dibuat sendiri di run() (thread-safe untuk load model)
        self._frame_idx = 0

    def start_capturing(self):
        """Mulai isi sliding window & prediksi (dipanggil saat masuk state LISTENING)."""
        self._buffer.clear()
        self._frame_idx = 0
        self._capturing = True

    def stop_capturing(self):
        self._capturing = False

    def run(self):
        import cv2

        owns_model = self._model is None
        if owns_model:
            try:
                self._model = LipReadingModel()
            except Exception as e:  # model/landmarker gagal load
                self.error.emit(f"Gagal load model lip reading: {e}")
                return

        if config.HARDWARE_MOCK_MODE:
            cap = _MockCameraCapture()
        else:
            cap = cv2.VideoCapture(config.CAMERA_INDEX)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

        if not cap.isOpened():
            self.error.emit(f"Tidak bisa membuka kamera index {config.CAMERA_INDEX}")
            return

        frame_interval = 1.0 / config.CAMERA_TARGET_FPS

        while self._run_flag:
            loop_start = time.monotonic()

            ret, frame = cap.read()
            if not ret:
                continue

            self.frame_ready.emit(frame)

            if self._capturing:
                feature_vector, face_detected = self._model.extract_features(frame)
                self.face_status_changed.emit(face_detected)

                if feature_vector is not None:
                    self._buffer.push(feature_vector)
                    self._frame_idx += 1

                    should_predict = (
                        self._buffer.is_full()
                        and self._frame_idx % config.PREDICTION_INTERVAL_FRAMES == 0
                    )
                    if should_predict:
                        sequence = self._buffer.get_sequence()
                        word, confidence = self._model.predict(sequence)
                        if confidence >= config.PREDICTION_CONFIDENCE_THRESHOLD:
                            self.prediction_ready.emit(word, confidence)

            # Kamera asli sudah otomatis "ngerem" sesuai FPS fisiknya saat cap.read(),
            # tapi _MockCameraCapture tidak punya rem sama sekali — tanpa sleep ini,
            # loop akan spin secepat CPU bisa dan membanjiri UI thread dengan signal
            # (ribuan frame_ready per detik), yang menyebabkan window "Not Responding".
            elapsed = time.monotonic() - loop_start
            remaining = frame_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

        cap.release()
        if owns_model:
            self._model.close()

    def stop(self):
        self._run_flag = False
        self.wait()


class _MockCameraCapture:
    """Kamera palsu untuk HARDWARE_MOCK_MODE=True — mengembalikan frame hitam
    supaya alur UI/state machine bisa dites tanpa webcam fisik tersambung."""

    def __init__(self):
        self._opened = True

    def isOpened(self):
        return self._opened

    def read(self):
        frame = np.zeros((config.CAMERA_HEIGHT, config.CAMERA_WIDTH, 3), dtype=np.uint8)
        return True, frame

    def release(self):
        self._opened = False
