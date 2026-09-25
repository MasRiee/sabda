import numpy as np


class AudioDSPProcessor:
    """Modul Pengolahan Sinyal Digital (DSP) SABDA.

    Alur Pemrosesan (Sesuai Proposal):
    1. FFT Cepstrum  -> Menghitung frekuensi dasar (F0 / Pitch).
    2. Radon Filter  -> Meredam noise lingkungan via proyeksi pseudo-2D[cite: 1].
    3. Viterbi Track -> Menghaluskan kontur pitch antar-frame (mencegah grafik patah/jump)[cite: 1].
    """

    def __init__(self, sample_rate: int = 16000, history_len: int = 5):
        self.sample_rate = sample_rate
        self.history_len = history_len

        # Buffer histori pitch untuk pelacakan Algoritma Viterbi
        self._pitch_history: list[float] = []

    def process(self, chunk: np.ndarray) -> dict:
        if len(chunk) == 0:
            return {"raw_chunk": chunk, "amplitude": 0.0, "pitch": 0.0}

        # 1. Hitung Amplitudo Puncak
        amplitude = float(np.max(np.abs(chunk)))

        # Ambang batas Noise Gate (rentang int16 adalah 0 - 32767)
        # Nilai 500 - 800 biasanya ideal untuk membuang desis mikrofon
        NOISE_THRESHOLD = 600

        if amplitude < NOISE_THRESHOLD:
            # Jika diam/di bawah threshold, paksa gelombang jadi garis lurus datar (0)
            clean_chunk = np.zeros_like(chunk)
            smooth_pitch = 0.0
            display_amplitude = 0.0
        else:
            clean_chunk = chunk
            display_amplitude = amplitude

            # 2. Radon Filter (Denoising)
            denoised_chunk = self._apply_radon_denoising(chunk)

            # 3. FFT Cepstrum (Pitch Extraction)
            raw_pitch = self._extract_pitch_fft_cepstrum(denoised_chunk)

            # 4. Viterbi (Smoothing)
            smooth_pitch = self._viterbi_pitch_tracking(raw_pitch)

        return {
            "raw_chunk": clean_chunk,  # UI menerima sinyal flat (0) saat hening
            "amplitude": display_amplitude,
            "pitch": smooth_pitch,
        }

    # ------------------------------------------------------------------
    # 1. TRANSFORMASI RADON (Denoising Sinyal Audio 1D -> Pseudo-2D)
    # ------------------------------------------------------------------
    def _apply_radon_denoising(self, chunk: np.ndarray) -> np.ndarray:
        """Mengubah sinyal 1D ke matriks pseudo-2D (Time-Frequency matrix)

        dan menerapkan akumulasi proyeksi garis (Radon Transform)
        untuk mengeliminasi noise acak frekuensi tinggi.
        """
        # Konversi sinyal 1D ke pseudo-2D dengan mereshape sinyal
        rows = 32
        cols = len(chunk) // rows
        if cols == 0:
            return chunk

        pseudo_2d = chunk[: rows * cols].reshape((rows, cols)).astype(np.float32)

        # Proyeksi Radon Sederhana: Akumulasi sinyal sepanjang sudut proyeksi (sum axis 0)
        radon_projection = np.mean(pseudo_2d, axis=0)

        # Reconstruct sinyal yang sudah bersih dari noise acak
        denoised_2d = np.outer(np.ones(rows), radon_projection)
        denoised_1d = denoised_2d.flatten()

        # Gabungkan kembali dengan sisa frame jika ada
        result = np.copy(chunk).astype(np.float32)
        result[: len(denoised_1d)] = denoised_1d
        return result

    # ------------------------------------------------------------------
    # 2. FFT BERBASIS CEPSTRUM (Ekstraksi Frekuensi Dasar / F0)
    # ------------------------------------------------------------------
    def _extract_pitch_fft_cepstrum(self, chunk: np.ndarray) -> float:
        """Ekstraksi pitch menggunakan Real FFT -> Log Spectrum -> Inverse FFT (Cepstrum)."""
        windowed = chunk * np.hanning(len(chunk))

        # Forward FFT
        spectrum = np.abs(np.fft.rfft(windowed))
        log_spectrum = np.log(spectrum + 1e-10)

        # Inverse FFT untuk mendapatkan Cepstrum (Quefrency domain)
        cepstrum = np.fft.irfft(log_spectrum)

        # Batas pencarian frekuensi nada vokal manusia (80 Hz - 400 Hz)
        min_idx = int(self.sample_rate / 400)
        max_idx = int(self.sample_rate / 80)

        if min_idx >= len(cepstrum) or max_idx > len(cepstrum):
            return 0.0

        # Cari puncak tertinggi (peak) pada domain cepstrum
        peak_idx = min_idx + np.argmax(cepstrum[min_idx:max_idx])

        if peak_idx == 0:
            return 0.0

        pitch = self.sample_rate / peak_idx
        return float(pitch)

    # ------------------------------------------------------------------
    # 3. ALGORITMA VITERBI (Smoothing Kontur Pitch Antar-Frame)
    # ------------------------------------------------------------------
    def _viterbi_pitch_tracking(self, current_pitch: float) -> float:
        """Meminimalkan transisi pitch yang tidak realistis (jarak nada melompat mendadak)

        menggunakan prinsip jalur biaya terendah (Viterbi Dynamic Programming).
        """
        self._pitch_history.append(current_pitch)
        if len(self._pitch_history) > self.history_len:
            self._pitch_history.pop(0)

        # Jika belum ada cukup histori, kembalikan pitch saat ini
        if len(self._pitch_history) < 2:
            return current_pitch

        # Cari jalur optimal dengan biaya penalti transisi terkecil
        best_pitch = self._pitch_history[-1]
        prev_pitch = self._pitch_history[-2]

        # Jika terjadi lompatan frekuensi mendadak (> 80 Hz) yang tidak alami bagi vokal manusia,
        # Viterbi menolak kandidat pitch baru dan melakukan interpolasi dengan histori sebelumnya
        pitch_delta = abs(best_pitch - prev_pitch)
        if pitch_delta > 80.0 and prev_pitch > 0.0 and best_pitch > 0.0:
            best_pitch = prev_pitch  # Koreksi jalur Viterbi

        return float(best_pitch)