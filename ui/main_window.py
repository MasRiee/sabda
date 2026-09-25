"""
main_window.py — Window utama SABDA.

Navigasi: klik tombol di layar, ATAU tekan Enter/Space (menyimulasikan
tombol SELECT joystick) selama HARDWARE_MOCK_MODE=True. Begitu mikrokontroler
joystick tersambung, sambungkan JoystickWorker.button_pressed ke method
_on_joystick_button() di bawah.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

import config
from backend.app_controller import AppController, AppState
from ui.screen import Screen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.UI_WINDOW_TITLE)

        if config.UI_FULLSCREEN:
            self.showFullScreen()
        else:
            self.resize(*config.UI_WINDOW_SIZE)

        self.controller = AppController()

        self.screen = Screen(self.controller)
        self.setCentralWidget(self.screen)

        self._wire_controller_signals()

        self.controller.start()
        
    def _wire_controller_signals(self):
        c = self.controller
        c.word_changed.connect(self.screen.set_word)
        c.camera_frame.connect(self.screen.update_frame)
        c.face_detected.connect(self.screen.set_face_detected)
        c.correction_updated.connect(self.screen.update_correction)
        c.waveform_updated.connect(self.screen.update_waveform)
        c.error.connect(self._on_error)

    def _on_error(self, message: str):
        print(f"[ERROR] {message}")
        # TODO: tampilkan sebagai dialog/toast di UI begitu error handling dirapikan

    # ------------------------------------------------------------------
    # Navigasi keyboard (mock)
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.controller.next_word()
        elif event.key() == Qt.Key.Key_Left:
            self.controller.previous_word()
        elif event.key() == Qt.Key.Key_Escape:
            self.controller.restart()
            self.controller.start()  
        else:
            super().keyPressEvent(event)

    def _on_joystick_button(self, button: str):
        """Dipanggil dari JoystickWorker.button_pressed begitu hardware asli tersambung."""
        if button == "RIGHT":
            self.controller.next_word()
        elif button == "LEFT":
            self.controller.previous_word()

    def closeEvent(self, event):
        self.controller.shutdown()
        super().closeEvent(event)
