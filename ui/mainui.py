import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt

from backend.app_controller import AppController
from ui.screen import Screen
import config, json

class WelcomeWidget(QWidget):
    """Halaman Utama / Welcome Screen"""
    def __init__(self, parent_stack):
        super().__init__()
        self.stack = parent_stack
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(50)
        header_widget.setStyleSheet("background-color: #EAEAEA;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)

        left_icons = QLabel("👤 ⭐")
        left_icons.setStyleSheet("font-size: 20px;")
        right_icon = QLabel("📶")
        right_icon.setStyleSheet("font-size: 20px;")

        header_layout.addWidget(left_icons)
        header_layout.addStretch()
        header_layout.addWidget(right_icon)
        root_layout.addWidget(header_widget)

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Welcome")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 64px; font-weight: 500; color: #000000;")

        subtitle_label = QLabel("Silahkan Pilih Mode")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 24px; color: #000000; margin-bottom: 30px;")

        btn_style = """
            QPushButton {
                background-color: #D9D9D9; color: #000000; font-size: 18px;
                font-weight: bold; border: none; border-radius: 2px;
                padding: 10px; min-width: 220px; max-width: 220px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """

        btn_latihan = QPushButton("Latihan")
        btn_latihan.setStyleSheet(btn_style)
        btn_latihan.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_ujian = QPushButton("Ujian")
        btn_ujian.setStyleSheet(btn_style)
        btn_ujian.clicked.connect(self.open_ujian)

        btn_keluar = QPushButton("Keluar")
        btn_keluar.setStyleSheet(btn_style)
        btn_keluar.clicked.connect(QApplication.instance().quit)

        center_layout.addStretch(1)
        center_layout.addWidget(title_label)
        center_layout.addWidget(subtitle_label)
        center_layout.addWidget(btn_latihan, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addSpacing(15)
        center_layout.addWidget(btn_ujian, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addSpacing(40)
        center_layout.addWidget(btn_keluar, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addStretch(1)

        root_layout.addWidget(center_widget)

    def open_ujian(self):
        action_page = self.stack.widget(2)
        action_page.setup_mode(word="Kata 1", is_ujian=True, current_idx=1, total_words=10)
        self.stack.setCurrentIndex(2)


class LatihanWidget(QWidget):
    """Halaman Mode Latihan (Pilih Tingkatan 10 Kata)"""
    def __init__(self, parent_stack, controller):
        super().__init__()
        self.stack = parent_stack
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(50)
        header_widget.setStyleSheet("background-color: #EAEAEA;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)

        left_icons = QLabel("👤 ⭐")
        left_icons.setStyleSheet("font-size: 20px;")
        right_icon = QLabel("📶")
        right_icon.setStyleSheet("font-size: 20px;")

        header_layout.addWidget(left_icons)
        header_layout.addStretch()
        header_layout.addWidget(right_icon)
        root_layout.addWidget(header_widget)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Silahkan Pilih Tingkatan")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: 500; color: #000000; margin-bottom: 20px;")
        content_layout.addWidget(title_label)

        word_list = []
        if config.WORDS_FILE.exists():
            with open(config.WORDS_FILE, "r", encoding="utf-8") as f:
                word_list = json.load(f)

        # Bagi ke 3 tingkatan
        n = len(word_list)
        mudah  = word_list[:n//3]
        sedang = word_list[n//3: 2*n//3]
        sulit  = word_list[2*n//3:]

        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(35)
        columns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_word_button(text, bg_color):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color}; color: #000000;
                    font-size: 16px; font-weight: bold;
                    border: 1px solid #000000; padding: 10px;
                    min-width: 140px; max-width: 140px;
                }}
                QPushButton:hover {{ opacity: 0.8; }}
            """)
            btn.clicked.connect(lambda: self.open_latihan_word(text))
            return btn

        # Kolom 1: Mudah (Hijau)
        col_mudah = QVBoxLayout()
        col_mudah.setSpacing(12)
        for word in mudah:
            col_mudah.addWidget(create_word_button(word, "#00FF00"))
        lbl_mudah = QLabel("Mudah")
        lbl_mudah.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mudah.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        col_mudah.addWidget(lbl_mudah)

        # Kolom 2: Sedang (Kuning)
        col_sedang = QVBoxLayout()
        col_sedang.setSpacing(12)
        for word in sedang:
            col_sedang.addWidget(create_word_button(word, "#FFCC00"))
        lbl_sedang = QLabel("Sedang")
        lbl_sedang.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sedang.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        col_sedang.addWidget(lbl_sedang)

        # Kolom 3: Sulit (Merah)
        col_sulit = QVBoxLayout()
        col_sulit.setSpacing(12)
        for word in sulit:
            col_sulit.addWidget(create_word_button(word, "#FF3333"))
        lbl_sulit = QLabel("Sulit")
        lbl_sulit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sulit.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        col_sulit.addWidget(lbl_sulit)

        columns_layout.addLayout(col_mudah)
        columns_layout.addLayout(col_sedang)
        columns_layout.addLayout(col_sulit)
        content_layout.addLayout(columns_layout)

        content_layout.addSpacing(30)

        btn_keluar = QPushButton("Keluar")
        btn_keluar.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: #000000; font-size: 16px;
                font-weight: bold; border: none; padding: 8px;
                min-width: 160px; max-width: 160px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """)
        btn_keluar.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        content_layout.addWidget(btn_keluar, alignment=Qt.AlignmentFlag.AlignCenter)

        root_layout.addWidget(content_widget)

    def open_latihan_word(self, word_text):
        action_page = self.stack.widget(2)
        action_page.setup_mode(word=word_text, is_ujian=False)
        self.controller.set_target_word(word_text)
        self.stack.setCurrentIndex(2)


class WordActionWidget(QWidget):
    """Halaman Universal untuk Area Latihan & Mode Ujian"""
    def __init__(self, parent_stack, controller):
        super().__init__()
        self.stack = parent_stack
        self.controller = controller
        self.is_ujian_mode = False
        self.current_word = "Kata"
        self.current_idx = 1
        self.total_words = 10
        self._last_result = None
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(40)
        header_widget.setStyleSheet("background-color: #EAEAEA;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_mode = QLabel("Latihan")
        self.lbl_mode.setStyleSheet("font-size: 16px; font-weight: bold; color: #000;")
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("font-size: 14px; color: #555;")
        right_icon = QLabel("📶")
        right_icon.setStyleSheet("font-size: 18px;")

        header_layout.addWidget(self.lbl_mode)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.counter_label)
        header_layout.addStretch()
        header_layout.addWidget(right_icon)
        root_layout.addWidget(header_widget)

        self.screen = Screen(self.controller)
        root_layout.addWidget(self.screen, stretch=1)

        footer_widget = QWidget()
        footer_widget.setFixedHeight(60)
        footer_widget.setStyleSheet("background-color: #F5F5F5;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 0, 20, 0)

        self.btn_keluar = QPushButton("Keluar")
        self.btn_keluar.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: #000;
                font-size: 15px; font-weight: bold;
                border: none; padding: 8px 24px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """)
        self.btn_keluar.clicked.connect(self.go_back)

        self.btn_lihat_hasil = QPushButton("Lihat Hasil")
        self.btn_lihat_hasil.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: #FFF;
                font-size: 15px; font-weight: bold;
                border: none; padding: 8px 24px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_lihat_hasil.setVisible(False)  # muncul setelah ada prediksi
        self.btn_lihat_hasil.clicked.connect(self.show_result)

        footer_layout.addWidget(self.btn_keluar)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_lihat_hasil)
        root_layout.addWidget(footer_widget)


    def setup_mode(self, word="Kata", is_ujian=False, current_idx=1, total_words=10):
        self.is_ujian_mode = is_ujian
        self.current_word = word
        self.current_idx = current_idx
        self.total_words = total_words
        self._last_result = None
        self.btn_lihat_hasil.setVisible(False)

        self.lbl_mode.setText("Ujian" if is_ujian else "Latihan")
        if is_ujian:
            self.counter_label.setText(f"Kata ke-{current_idx} dari {total_words} kata")
        else:
            self.counter_label.setText(f"Kata: {word}")

        self.controller.start()

    def on_word_changed(self, word: str):
        """Dipanggil saat controller ganti kata."""
        self.screen.set_word(word)
        self.screen.camera_feed.set_correction("Ucapkan kata di atas...", correct=None)

    def on_correction_updated(self, result: dict):
        """Dipanggil saat ada hasil prediksi dari model."""
        self.screen.update_correction(result)
        self._last_result = result
        # Tampilkan tombol Lihat Hasil setelah ada prediksi
        self.btn_lihat_hasil.setVisible(True)

    def show_result(self):
        """Pindah ke halaman hasil dengan data riil dari model & audio."""
        if self._last_result is None:
            return

        confidence = self._last_result["confidence"] # 0.0 sampai 1.0
        confidence_pct = int(confidence * 100)

        # 1. Gerakan Bibir: Berdasarkan confidence model lip-reading langsung
        bibir = confidence_pct

        # 2. Artikulasi: Dihitung dari stabilitas confidence (misal diberi bobot atau disesuaikan)
        artikulasi = int(min(100, confidence_pct * 1.05)) if confidence_pct > 50 else int(confidence_pct * 0.8)

        # 3. Intonasi: Diambil dari analisis DSP mikrofon (pitch/suara terdeteksi)
        audio_metrics = self.controller.get_audio_metrics()
        intonasi = audio_metrics.get("intonasi_score", 70)
        
        # Jika confidence sangat rendah, turunkan skor intonasi secara proporsional
        if confidence_pct < 40:
            intonasi = max(30, intonasi - 25)

        # Total Nilai: Rata-rata tertimbang dari ketiga metrik riil
        total_nilai = int((artikulasi * 0.4) + (bibir * 0.4) + (intonasi * 0.2))

        result_page = self.stack.widget(3)
        result_page.set_results(
            total_nilai=total_nilai,
            artikulasi=artikulasi,
            intonasi=intonasi,
            bibir=bibir,
            is_ujian=self.is_ujian_mode,
            current_idx=self.current_idx,
            total_words=self.total_words
        )
        self.stack.setCurrentIndex(3)

    def go_back(self):
        self.controller.restart()
        if self.is_ujian_mode:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)


class ResultWidget(QWidget):
    """Halaman Hasil Evaluasi Pelafalan (Nilai, Artikulasi, Intonasi, Gerakan Bibir)"""
    def __init__(self, parent_stack):
        super().__init__()
        self.stack = parent_stack
        self.is_ujian = False
        self.current_idx = 1
        self.total_words = 10
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Header Bar
        header_widget = QWidget()
        header_widget.setFixedHeight(50)
        header_widget.setStyleSheet("background-color: #EAEAEA;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)

        left_icons = QLabel("👤 ⭐")
        left_icons.setStyleSheet("font-size: 20px;")
        right_icon = QLabel("📶")
        right_icon.setStyleSheet("font-size: 20px;")

        header_layout.addWidget(left_icons)
        header_layout.addStretch()
        header_layout.addWidget(right_icon)
        root_layout.addWidget(header_widget)

        # 2. Body Section
        body_layout = QVBoxLayout()
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Section Nilai Utama (Atas)
        self.lbl_nilai_title = QLabel("Nilai")
        self.lbl_nilai_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nilai_title.setStyleSheet("font-size: 36px; color: #000000;")

        self.lbl_nilai_val = QLabel("%")
        self.lbl_nilai_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nilai_val.setStyleSheet("font-size: 32px; font-weight: bold; color: #000000; margin-bottom: 20px;")

        body_layout.addStretch(1)
        body_layout.addWidget(self.lbl_nilai_title)
        body_layout.addWidget(self.lbl_nilai_val)

        # Section 3 Metrik (Artikulasi, Intonasi, Gerakan Bibir)
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(60)
        metrics_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Column Artikulasi
        col_art = QVBoxLayout()
        lbl_art_title = QLabel("Artikulasi")
        lbl_art_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_art_title.setStyleSheet("font-size: 28px; color: #000000;")
        self.lbl_art_val = QLabel("%")
        self.lbl_art_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_art_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        col_art.addWidget(lbl_art_title)
        col_art.addWidget(self.lbl_art_val)

        # Column Intonasi
        col_int = QVBoxLayout()
        lbl_int_title = QLabel("Intonasi")
        lbl_int_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_int_title.setStyleSheet("font-size: 28px; color: #000000;")
        self.lbl_int_val = QLabel("%")
        self.lbl_int_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_int_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        col_int.addWidget(lbl_int_title)
        col_int.addWidget(self.lbl_int_val)

        # Column Gerakan Bibir
        col_bib = QVBoxLayout()
        lbl_bib_title = QLabel("Gerakan Bibir")
        lbl_bib_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_bib_title.setStyleSheet("font-size: 28px; color: #000000;")
        self.lbl_bib_val = QLabel("%")
        self.lbl_bib_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_bib_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        col_bib.addWidget(lbl_bib_title)
        col_bib.addWidget(self.lbl_bib_val)

        metrics_layout.addLayout(col_art)
        metrics_layout.addLayout(col_int)
        metrics_layout.addLayout(col_bib)

        body_layout.addLayout(metrics_layout)
        body_layout.addStretch(1)

        # 3. Area Tombol Aksi Bottom Center
        btn_box = QVBoxLayout()
        btn_box.setSpacing(12)
        btn_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ulangi = QPushButton("Ulangi")
        self.btn_ulangi.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: #000000; font-size: 18px;
                font-weight: bold; border: none; padding: 10px;
                min-width: 180px; max-width: 180px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """)
        self.btn_ulangi.clicked.connect(self.ulangi_action)

        self.btn_lanjut = QPushButton("Lanjut")
        self.btn_lanjut.clicked.connect(self.lanjut_action)

        self.btn_keluar = QPushButton("Keluar")
        self.btn_keluar.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: #000000; font-size: 18px;
                font-weight: bold; border: none; padding: 10px;
                min-width: 180px; max-width: 180px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """)
        self.btn_keluar.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        btn_box.addWidget(self.btn_ulangi)
        btn_box.addWidget(self.btn_lanjut)
        btn_box.addWidget(self.btn_keluar)

        body_layout.addLayout(btn_box)
        body_layout.addSpacing(30)

        root_layout.addLayout(body_layout)

    def set_results(self, total_nilai, artikulasi, intonasi, bibir, is_ujian=False, current_idx=1, total_words=10):
        self.is_ujian = is_ujian
        self.current_idx = current_idx
        self.total_words = total_words

        self.lbl_nilai_val.setText(f"{total_nilai}%")
        self.lbl_art_val.setText(f"{artikulasi}%")
        self.lbl_int_val.setText(f"{intonasi}%")
        self.lbl_bib_val.setText(f"{bibir}%")

        # Logika Aktif/Nonaktifkan Tombol 'Lanjut' untuk Mode Ujian
        if is_ujian:
            if total_nilai >= 60:
                self.btn_lanjut.setEnabled(True)
                self.btn_lanjut.setStyleSheet("""
                    QPushButton {
                        background-color: #D9D9D9; color: #000000; font-size: 18px;
                        font-weight: bold; border: none; padding: 10px;
                        min-width: 180px; max-width: 180px;
                    }
                    QPushButton:hover { background-color: #CCCCCC; }
                """)
            else:
                self.btn_lanjut.setEnabled(False)
                self.btn_lanjut.setStyleSheet("""
                    QPushButton {
                        background-color: #F0F0F0; color: #A0A0A0; font-size: 18px;
                        font-weight: bold; border: none; padding: 10px;
                        min-width: 180px; max-width: 180px;
                    }
                """)
        else:
            # Mode Latihan selalu memperbolehkan Lanjut
            self.btn_lanjut.setEnabled(True)
            self.btn_lanjut.setStyleSheet("""
                QPushButton {
                    background-color: #D9D9D9; color: #000000; font-size: 18px;
                    font-weight: bold; border: none; padding: 10px;
                    min-width: 180px; max-width: 180px;
                }
                QPushButton:hover { background-color: #CCCCCC; }
            """)

    def ulangi_action(self):
        self.stack.setCurrentIndex(2)

    def lanjut_action(self):
        if self.is_ujian:
            next_idx = self.current_idx + 1
            if next_idx <= self.total_words:
                action_page = self.stack.widget(2)
                action_page.setup_mode(
                    word=f"Kata {next_idx}",
                    is_ujian=True,
                    current_idx=next_idx,
                    total_words=self.total_words
                )
                self.stack.setCurrentIndex(2)
            else:
                self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SABDA - Speech Assistance")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #FFFFFF;")

        self.controller = AppController()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.welcome_page = WelcomeWidget(self.stacked_widget)
        self.latihan_page = LatihanWidget(self.stacked_widget, self.controller)
        self.action_page = WordActionWidget(self.stacked_widget, self.controller)
        self.result_page = ResultWidget(self.stacked_widget)

        self.stacked_widget.addWidget(self.welcome_page) # Index 0
        self.stacked_widget.addWidget(self.latihan_page) # Index 1
        self.stacked_widget.addWidget(self.action_page)  # Index 2
        self.stacked_widget.addWidget(self.result_page)  # Index 3

        self._wire_signals()

    def _wire_signals(self):
        c = self.controller
        c.word_changed.connect(self.action_page.on_word_changed)
        c.camera_frame.connect(self.action_page.screen.update_frame)
        c.face_detected.connect(self.action_page.screen.set_face_detected)
        c.correction_updated.connect(self.action_page.on_correction_updated)
        c.waveform_updated.connect(self.action_page.screen.update_waveform)
        c.error.connect(lambda msg: print(f"[ERROR] {msg}"))

    def keyPressEvent(self, event):
        # Keyboard navigasi hanya aktif saat di halaman kamera (index 2)
        if self.stacked_widget.currentIndex() == 2:
            if event.key() == Qt.Key.Key_Right:
                self.controller.next_word()
            elif event.key() == Qt.Key.Key_Left:
                self.controller.previous_word()
            elif event.key() == Qt.Key.Key_Escape:
                self.action_page.go_back()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self.controller.shutdown()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())