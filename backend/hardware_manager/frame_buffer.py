"""
frame_buffer.py — Sliding window buffer untuk sequence fitur bibir.

Berbeda dari versi awal (min/max padding), sekarang mengikuti pendekatan
notebook (Step 12): sequence dengan panjang berapa pun diresample lewat
interpolasi linear ke panjang tetap config.SEQUENCE_LENGTH sebelum
dipakai untuk inferensi, supaya konsisten dengan cara model dilatih.
"""

from collections import deque

import numpy as np

import config


def resample_sequence(seq: np.ndarray, target_len: int) -> np.ndarray:
    """Persis logika resample_sequence() di notebook Step 12."""
    seq = np.asarray(seq, dtype=np.float32)
    if len(seq) == target_len:
        return seq
    t_orig = np.linspace(0, 1, num=len(seq))
    t_new = np.linspace(0, 1, num=target_len)
    resampled = np.empty((target_len, seq.shape[1]), dtype=np.float32)
    for f in range(seq.shape[1]):
        resampled[:, f] = np.interp(t_new, t_orig, seq[:, f])
    return resampled


class FrameBuffer:
    """
    Sliding window rolling (deque maxlen=SEQUENCE_LENGTH), meniru
    `collections.deque(maxlen=target_len)` yang dipakai live_word_predictor
    di notebook Step 16 — buffer terus terisi selama capturing aktif,
    prediksi dipicu setiap N frame begitu buffer penuh.
    """

    def __init__(self, sequence_length: int = None):
        self.sequence_length = sequence_length or config.SEQUENCE_LENGTH
        self._buffer: deque = deque(maxlen=self.sequence_length)

    def push(self, feature_vector: np.ndarray) -> None:
        """Tambahkan 1 frame fitur, shape (config.FEATURE_DIM,)."""
        self._buffer.append(feature_vector)

    def is_full(self) -> bool:
        return len(self._buffer) == self.sequence_length

    def get_sequence(self) -> np.ndarray:
        """
        Ambil sequence saat ini, shape (SEQUENCE_LENGTH, FEATURE_DIM).
        Diresample lagi untuk jaga-jaga kalau buffer belum penuh persis
        (mis. dipanggil manual sebelum is_full()).
        """
        frames = np.array(list(self._buffer))
        if len(frames) == 0:
            return np.zeros((self.sequence_length, config.FEATURE_DIM), dtype=np.float32)
        return resample_sequence(frames, self.sequence_length)

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
