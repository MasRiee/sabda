"""
microphone.py 
"""

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

import config


class MicrophoneWorker(QThread):
    """
    Signals:
        audio_chunk_ready(np.ndarray): potongan buffer audio mentah
        error(str)
    """

    audio_chunk_ready = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_flag = True

    def run(self):
        try:
            import pyaudio
        except ImportError:
            self.error.emit(
                "pyaudio belum terinstall. Di Linux perlu 'sudo apt install "
                "portaudio19-dev' dulu sebelum 'pip install pyaudio'."
            )
            return

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=config.MIC_SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.MIC_CHUNK_SIZE,
        )

        while self._run_flag:
            data = stream.read(config.MIC_CHUNK_SIZE, exception_on_overflow=False)
            chunk = np.frombuffer(data, dtype=np.int16)
            self.audio_chunk_ready.emit(chunk)

        stream.stop_stream()
        stream.close()
        pa.terminate()

    def stop(self):
        self._run_flag = False
        self.wait()
