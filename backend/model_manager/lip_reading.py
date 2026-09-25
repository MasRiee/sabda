"""
lip_reading.py — Wrapper FaceLandmarker (MediaPipe Tasks API) + model kata (GRU/Keras).

Ini adalah porting dari notebook "Vowel Lip-Shape Detection Using MediaPipe"
Bagian 2 (Step 9-16), diubah jadi kelas yang bisa dipanggil dari CameraWorker
(sensor_manager) tanpa perlu Colab/webcam browser.

Selama MODEL_MOCK_MODE=True, prediksi kata di-random dari DEFAULT_TARGET_WORDS
supaya alur aplikasi (state machine, UI) bisa dites duluan tanpa menunggu
model & face_landmarker.task tersedia.
"""

from __future__ import annotations

import json
import math
import random
from typing import Optional

import numpy as np

import config


class LipReadingModel:
    """
    Menggabungkan 2 tanggung jawab:
    1. Ekstraksi fitur bibir per-frame (FaceLandmarker Tasks API) — extract_features()
    2. Klasifikasi kata dari sequence fitur (model GRU) — predict()

    Kedua-duanya dipisah supaya CameraWorker bisa memanggil extract_features()
    setiap frame (murah), dan predict() hanya dipanggil setiap
    PREDICTION_INTERVAL_FRAMES atau saat buffer penuh (lebih mahal).
    """

    def __init__(self):
        self._landmarker = None
        self._word_model = None
        self._target_words: list[str] = list(config.DEFAULT_TARGET_WORDS)
        self._frame_counter = 0  # timestamp_ms untuk detect_for_video, HARUS monoton naik

        self._load_labels()

        if not config.MODEL_MOCK_MODE:
            self._load_landmarker()
            self._load_word_model()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _load_labels(self):
        if config.WORD_LABELS_FILE.exists():
            with open(config.WORD_LABELS_FILE, "r", encoding="utf-8") as f:
                self._target_words = json.load(f)
        # kalau belum ada, tetap pakai DEFAULT_TARGET_WORDS (sudah di-set di __init__)

    def _load_landmarker(self):
        """Load FaceLandmarker (MediaPipe Tasks API) dalam mode VIDEO."""
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python.core.base_options import BaseOptions

        if not config.FACE_LANDMARKER_MODEL_FILE.exists():
            raise FileNotFoundError(
                f"File model tidak ditemukan: {config.FACE_LANDMARKER_MODEL_FILE}\n"
                f"Download dulu dari: {config.FACE_LANDMARKER_MODEL_URL}\n"
                f"atau jalankan: python scripts/download_face_landmarker.py"
            )

        base_options = BaseOptions(model_asset_path=str(config.FACE_LANDMARKER_MODEL_FILE))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)

    def _load_word_model(self):
        """Load model GRU hasil training (Step 15 notebook)."""
        import tensorflow as tf

        if not config.WORD_CLASSIFIER_FILE.exists():
            raise FileNotFoundError(
                f"Model kata belum ada: {config.WORD_CLASSIFIER_FILE}\n"
                f"Training dulu lewat notebook, lalu copy word_classifier.keras + "
                f"word_labels.json ke folder model/."
            )
        self._word_model = tf.keras.models.load_model(config.WORD_CLASSIFIER_FILE)

    def close(self):
        if self._landmarker is not None:
            self._landmarker.close()

    @property
    def target_words(self) -> list[str]:
        return self._target_words

    # ------------------------------------------------------------------
    # Ekstraksi fitur per-frame — porting dari normalize_lip_contour()
    # dan extract_lip_sequence_features() di notebook (Step 10)
    # ------------------------------------------------------------------
    def extract_features(self, frame_bgr: np.ndarray) -> tuple[Optional[np.ndarray], bool]:
        """
        Args:
            frame_bgr: 1 frame OpenCV (BGR, HxWx3)

        Returns:
            (feature_vector, face_detected)
            feature_vector: np.ndarray shape (config.FEATURE_DIM,) atau None kalau wajah tidak terdeteksi
            face_detected: bool, dipakai UI untuk indikator "wajah terdeteksi"
        """
        if config.MODEL_MOCK_MODE or self._landmarker is None:
            # Mock: fitur dummy tapi tetap "wajah terdeteksi" supaya buffer terisi
            return np.zeros(config.FEATURE_DIM, dtype=np.float32), True

        import cv2
        from mediapipe import Image, ImageFormat

        height, width, _ = frame_bgr.shape
        rgb_image = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_image)

        # timestamp_ms HARUS monoton naik sepanjang umur objek landmarker (mode VIDEO),
        # jangan direset per sequence/klip — lihat catatan bug di notebook Step 11.
        self._frame_counter += 1
        result = self._landmarker.detect_for_video(mp_image, self._frame_counter)

        if not result.face_landmarks:
            return None, False

        lm = result.face_landmarks[0]
        feature_vector = self._normalize_lip_contour(lm, width, height)
        if feature_vector is None:
            return None, False
        return feature_vector, True

    @staticmethod
    def _normalize_lip_contour(lm, width: int, height: int) -> Optional[np.ndarray]:
        """Persis logika normalize_lip_contour() di notebook Step 10."""

        def px(idx):
            return lm[idx].x * width, lm[idx].y * height

        eye_l = px(config.REF_POINTS["left_eye_outer"])
        eye_r = px(config.REF_POINTS["right_eye_outer"])
        interocular_dist = math.hypot(eye_l[0] - eye_r[0], eye_l[1] - eye_r[1])
        if interocular_dist < 1e-6:
            return None

        left_corner = px(config.LIP_POINTS["left_corner_outer"])
        right_corner = px(config.LIP_POINTS["right_corner_outer"])
        center_x = (left_corner[0] + right_corner[0]) / 2
        center_y = (left_corner[1] + right_corner[1]) / 2

        coords = []
        for idx in config.LIP_CONTOUR_POINTS:
            x, y = px(idx)
            coords.append((x - center_x) / interocular_dist)
            coords.append((y - center_y) / interocular_dist)

        mouth_width = math.hypot(
            left_corner[0] - right_corner[0], left_corner[1] - right_corner[1]
        ) / interocular_dist
        upper_inner = px(config.LIP_POINTS["upper_inner"])
        lower_inner = px(config.LIP_POINTS["lower_inner"])
        mouth_height = math.hypot(
            upper_inner[0] - lower_inner[0], upper_inner[1] - lower_inner[1]
        ) / interocular_dist
        left_inner = px(config.LIP_POINTS["left_corner_inner"])
        right_inner = px(config.LIP_POINTS["right_corner_inner"])
        inner_width = math.hypot(
            left_inner[0] - right_inner[0], left_inner[1] - right_inner[1]
        ) / interocular_dist

        mar = mouth_height / mouth_width if mouth_width else 0
        roundness = inner_width / mouth_width if mouth_width else 0

        lip_center_z = (lm[config.LIP_POINTS["upper_outer"]].z + lm[config.LIP_POINTS["lower_outer"]].z) / 2
        corner_center_z = (
            lm[config.LIP_POINTS["left_corner_outer"]].z + lm[config.LIP_POINTS["right_corner_outer"]].z
        ) / 2
        protrusion = corner_center_z - lip_center_z

        return np.array(coords + [mar, roundness, protrusion], dtype=np.float32)

    # ------------------------------------------------------------------
    # Prediksi kata dari sequence fitur — porting dari live_word_predictor (Step 16)
    # ------------------------------------------------------------------
    def predict(self, sequence: np.ndarray) -> tuple[str, float]:
        """
        Args:
            sequence: array shape (SEQUENCE_LENGTH, FEATURE_DIM), sudah diresample
                      (lihat backend/sensor_manager/frame_buffer.py)

        Returns:
            (predicted_word, confidence)
        """
        if config.MODEL_MOCK_MODE or self._word_model is None:
            word = random.choice(self._target_words)
            confidence = round(random.uniform(0.5, 0.99), 2)
            return word, confidence

        preds = self._word_model.predict(sequence[None, ...], verbose=0)[0]
        idx = int(np.argmax(preds))
        confidence = float(preds[idx])
        word = self._target_words[idx] if idx < len(self._target_words) else "?"
        return word, confidence
