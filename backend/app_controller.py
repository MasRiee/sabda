from __future__ import annotations

import json
from enum import Enum, auto

from PyQt6.QtCore import QObject, pyqtSignal

import config
from backend.model_manager.lip_reading import LipReadingModel
from backend.model_manager.word_validator import validate
from backend.hardware_manager.camera import CameraWorker
from backend.hardware_manager.microphone import MicrophoneWorker
from backend.hardware_manager.audio_dsp import AudioDSPProcessor
from web.server_gamifikasi import broadcast_update

import datetime
import threading

class AppState(Enum):
    IDLE = auto()
    ACTIVE = auto()

class AppController(QObject):

    state_changed = pyqtSignal(object)
    word_changed = pyqtSignal(str)
    camera_frame = pyqtSignal(object)
    face_detected = pyqtSignal(bool)
    correction_updated = pyqtSignal(dict)
    waveform_updated = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._state = AppState.IDLE
        self._word_list = self._load_word_list()
        self._word_index = 0
        self._pitch_buffer = []

        try:
            self._model = LipReadingModel()
        except Exception as exc:
            self._model = None
            self.error.emit(f"Gagal load model: {exc}")

        self._camera = CameraWorker(model=self._model)
        self._camera.frame_ready.connect(self.camera_frame.emit)
        self._camera.face_status_changed.connect(self.face_detected.emit)
        self._camera.prediction_ready.connect(self._on_prediction_ready)
        self._camera.error.connect(self.error.emit)
        self._camera.start()

        self._microphone = MicrophoneWorker()
        self._microphone.audio_chunk_ready.connect(self.waveform_updated.emit)
        self._microphone.error.connect(self.error.emit)
        self._microphone.start()

        self._audio_dsp = AudioDSPProcessor()
        self._microphone.audio_chunk_ready.connect(self._on_audio_data_received)

        from web.server_gamifikasi import broadcast_update, socketio, app
        self._broadcast = broadcast_update
        web_thread = threading.Thread(
            target=lambda: socketio.run(app, host='0.0.0.0', port=5000, debug=False),
            daemon=True
        )
        web_thread.start()
    # ------------------------------------------------------------------
    def _load_word_list(self) -> list[str]:
        if config.WORDS_FILE.exists():
            with open(config.WORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        # fallback: pakai daftar kata target model kalau word_list.json belum disusun
        return list(config.DEFAULT_TARGET_WORDS)

    def _set_state(self, new_state: AppState):
        self._state = new_state
        self.state_changed.emit(new_state)

    @property
    def state(self) -> AppState:
        return self._state

    @property
    def current_word(self) -> str:
        return self._word_list[self._word_index]

    # ------------------------------------------------------------------
    # Slot dipanggil dari frontend
    # ------------------------------------------------------------------
    def start(self):
        """IDLE -> ACTIVE, mulai dari kata pertama."""
        self._word_index = 0
        self._show_current_word()

    def next_word(self):
        """Pindah ke kata berikutnya. Wrap ke kata pertama kalau sudah di akhir daftar."""
        self._word_index = (self._word_index + 1) % len(self._word_list)
        self._show_current_word()

    def previous_word(self):
        """Pindah ke kata sebelumnya. Wrap ke kata terakhir kalau sudah di kata pertama."""
        self._word_index = (self._word_index - 1) % len(self._word_list)
        self._show_current_word()

    def restart(self):
        self._word_index = 0
        self._camera.stop_capturing()
        self._set_state(AppState.IDLE)

    def shutdown(self):
        self._camera.stop()
        self._microphone.stop()

    # ------------------------------------------------------------------
    def _show_current_word(self):
        self._camera.start_capturing()
        self.word_changed.emit(self.current_word)
        self._set_state(AppState.ACTIVE)

    def _on_prediction_ready(self, predicted_word: str, confidence: float):
        if self._state != AppState.ACTIVE:
            return
        
        result = validate(predicted_word, self.current_word, confidence)
        self.correction_updated.emit(result)

        # Broadcast ke web dashboard
        self._broadcast({
            "status": "active",
            "target_word": self.current_word,
            "predicted_word": result["predicted_word"],
            "confidence": result["confidence"],
            "correct": result["correct"],
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

    def _on_audio_data_received(self, chunk):
        # Olah data audio mentah untuk mendapatkan nilai amplitudo & pitch
        dsp_result = self._audio_dsp.process(chunk)
        if self._state == AppState.ACTIVE:
            pitch = dsp_result.get("pitch", 0.0)
            if pitch > 0:
                self._pitch_buffer.append(pitch)
           
        self.waveform_updated.emit(dsp_result)

    def set_target_word(self, word: str):
        """Mengatur kata aktif berdasarkan pilihan user di menu Latihan."""
        if word in self._word_list:
            self._word_index = self._word_list.index(word)
        else:
            self._word_index = 0
        self._pitch_buffer.clear()
        self._show_current_word()

    def get_audio_metrics(self) -> dict:
        """Menghitung skor intonasi riil berdasarkan rata-rata pitch yang terkumpul."""
        if not self._pitch_buffer:
            return {"intonasi_score": 50, "avg_pitch": 0.0}

        avg_pitch = sum(self._pitch_buffer) / len(self._pitch_buffer)
        
        # Konversi rata-rata pitch (Hz) ke rentang skor 50 - 95 
        # (Suara manusia normal umumnya berada di kisaran 85Hz - 255Hz)
        score = min(95, max(50, int(50 + (avg_pitch / 5))))
        
        return {
            "intonasi_score": score,
            "avg_pitch": avg_pitch
        }