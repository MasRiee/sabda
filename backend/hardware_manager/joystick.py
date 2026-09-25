"""
joystick.py — Baca input navigasi dari mikrokontroler (Arduino/ESP32) via
USB-serial. Protokol sederhana: mikrokontroler kirim 1 baris teks per event,
misal "UP", "DOWN", "SELECT", "BACK".

Selama HARDWARE_MOCK_MODE=True, tidak ada polling serial — navigasi dilakukan
lewat keyboard (panah + Enter) langsung di widget PyQt6 (lihat frontend/main_window.py).
"""

from PyQt6.QtCore import QThread, pyqtSignal

import config


class JoystickWorker(QThread):
    """
    Signals:
        button_pressed(str): salah satu dari "UP", "DOWN", "LEFT", "RIGHT", "SELECT", "BACK"
        error(str)
    """

    button_pressed = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_flag = True
        self._serial = None

    def run(self):
        if config.HARDWARE_MOCK_MODE:
            # Tidak perlu polling apa pun — input datang dari keyboard di UI langsung.
            return

        import serial

        try:
            self._serial = serial.Serial(
                config.SERIAL_PORT,
                config.SERIAL_BAUDRATE,
                timeout=config.SERIAL_TIMEOUT_SEC,
            )
        except Exception as exc:
            self.error.emit(f"Gagal konek joystick via serial: {exc}")
            return

        while self._run_flag:
            try:
                line = self._serial.readline().decode("utf-8").strip()
            except Exception:
                continue
            if line:
                self.button_pressed.emit(line)

    def stop(self):
        self._run_flag = False
        self.wait()
        if self._serial is not None:
            self._serial.close()
