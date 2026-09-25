import sys
import random
import cv2
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import threading
from pathlib import Path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
from web.server_gamifikasi import socketio, app
from backend.app_controller import AppController
import config

class WelcomeWidget(QWidget):
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
        action_page.setup_mode(word="makasih", is_ujian=True, current_idx=1, total_words=8)
        self.stack.setCurrentIndex(2)


class LatihanWidget(QWidget):
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

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Silahkan Pilih Tingkatan")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: 500; color: #000000; margin-bottom: 20px;")
        content_layout.addWidget(title_label)

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

        # Kategori Mudah
        col_mudah = QVBoxLayout()
        col_mudah.setSpacing(12)
        for word in ["makasih", "aku"]:
            col_mudah.addWidget(create_word_button(word, "#00FF00"))
        lbl_mudah = QLabel("Mudah")
        lbl_mudah.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mudah.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        col_mudah.addWidget(lbl_mudah)

        # Kategori Sedang
        col_sedang = QVBoxLayout()
        col_sedang.setSpacing(12)
        for word in ["iya", "engga", "maaf"]:
            col_sedang.addWidget(create_word_button(word, "#FFCC00"))
        lbl_sedang = QLabel("Sedang")
        lbl_sedang.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sedang.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        col_sedang.addWidget(lbl_sedang)

        # Kategori Sulit
        col_sulit = QVBoxLayout()
        col_sulit.setSpacing(12)
        for word in ["tolong", "halo", "permisi"]:
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
        self.stack.setCurrentIndex(2)


class WordActionWidget(QWidget):
    def __init__(self, parent_stack, controller):
        super().__init__()
        self.stack = parent_stack
        self.controller = controller
        self.is_ujian_mode = False
        self.current_word = "Kata"
        self.current_idx = 1
        self.total_words = 8
        self._last_confidence = 0.0
        self._correction_text = ""
        self._correction_correct = None
        self._current_word_display = ""
        

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_widget.setFixedHeight(40)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 0)
        
        right_icon = QLabel("📶")
        right_icon.setStyleSheet("font-size: 20px;")
        header_layout.addStretch()
        header_layout.addWidget(right_icon)
        root_layout.addWidget(header_widget)

        top_section = QVBoxLayout()
        top_section.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.word_label = QLabel("Kata")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #000000;")
        top_section.addWidget(self.word_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedWidth(400)
        line.setStyleSheet("color: #D9D9D9; background-color: #D9D9D9; height: 4px; border: none;")
        top_section.addWidget(line, alignment=Qt.AlignmentFlag.AlignCenter)

        self.counter_label = QLabel("Kata ke-1 dari 8 kata")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; margin-top: 4px;")
        top_section.addWidget(self.counter_label)

        root_layout.addLayout(top_section)

        # Video Frame Kamera
        self.camera_view = QLabel("Memuat Kamera...")
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setStyleSheet("background-color: #000000; color: #FFFFFF; font-size: 16px; border-radius: 8px;")
        self.camera_view.setMinimumSize(480, 270)
        root_layout.addWidget(self.camera_view, alignment=Qt.AlignmentFlag.AlignCenter)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(30, 10, 30, 20)

        # Visualizer Gelombang Suara (Waveform) Mic
        self.waveform_box = QLabel("||||||||||||")
        self.waveform_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.waveform_box.setStyleSheet("""
            background-color: #031B2E; color: #00FFCC;
            font-size: 22px; font-weight: bold; letter-spacing: 3px;
            border-radius: 4px;
        """)
        self.waveform_box.setFixedSize(220, 80)

        self.btn_finish_speech = QPushButton("Selesai Bicara")
        self.btn_finish_speech.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: #FFFFFF;
                font-size: 15px; font-weight: bold; border: none;
                padding: 10px 15px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_finish_speech.clicked.connect(self.finish_speech_simulation)

        self.btn_keluar = QPushButton("Keluar")
        self.btn_keluar.setStyleSheet("""
            QPushButton {
                background-color: #D9D9D9; color: #000000;
                font-size: 16px; font-weight: bold; border: none;
                padding: 8px 25px; min-width: 120px;
            }
            QPushButton:hover { background-color: #CCCCCC; }
        """)
        self.btn_keluar.clicked.connect(self.go_back)

        bottom_layout.addWidget(self.waveform_box)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(self.btn_finish_speech, alignment=Qt.AlignmentFlag.AlignBottom)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.btn_keluar, alignment=Qt.AlignmentFlag.AlignBottom)

        root_layout.addLayout(bottom_layout)

    def setup_mode(self, word="Kata", is_ujian=False, current_idx=1, total_words=8):
        self.is_ujian_mode = is_ujian
        self.current_word = word
        self.current_idx = current_idx
        self.total_words = total_words
        self._last_confidence = 0.0
        self.word_label.setText(word)
        self._current_word_display = word.upper()
        self._correction_text = "Ucapkan kata di atas..."
        self._correction_correct = None
        
        if is_ujian:
            self.counter_label.setText(f"Kata ke-{current_idx} dari {total_words} kata")
            self.counter_label.setVisible(True)
        else:
            self.counter_label.setVisible(False)

        self.controller.set_target_word(word)

    def update_camera_frame(self, frame_bgr):
        frame = cv2.flip(frame_bgr, 1)
        h, w = frame.shape[:2]

        if self._correction_text:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness = 2
            color = (
                (0, 220, 80) if self._correction_correct is True
                else (80, 80, 255) if self._correction_correct is False
                else (200, 200, 200)
            )
            (cw, ch_), _ = cv2.getTextSize(self._correction_text, font, font_scale, thickness)
            cx = (w - cw) // 2
            cy = h - 15
            cv2.putText(frame, self._correction_text, (cx+2, cy+2), font,
                        font_scale, (0, 0, 0), thickness + 2)
            cv2.putText(frame, self._correction_text, (cx, cy), font,
                        font_scale, color, thickness)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(qt_img).scaled(
            self.camera_view.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camera_view.setPixmap(scaled_pixmap)

    def update_waveform(self, audio_data):
        if isinstance(audio_data, dict):
            raw = audio_data.get("raw_chunk")
        else:
            raw = audio_data

        if raw is not None and len(raw) > 0:
            volume_norm = int(np.linalg.norm(raw.astype(np.float32)) / 500)
            num_bars = min(18, max(2, volume_norm))
            self.waveform_box.setText("|" * num_bars)

    def on_correction_updated(self, result: dict):
        self._last_confidence = result.get("confidence", 0.0)
        predicted = result["predicted_word"].upper()
        confidence_pct = result["confidence"] * 100
        if result["correct"]:
            self._correction_text = f"BENAR: {predicted} ({confidence_pct:.0f}%)"
        else:
            self._correction_text = f"Terdeteksi: {predicted} ({confidence_pct:.0f}%)"
        self._correction_correct = result["correct"]

    def finish_speech_simulation(self):
        """Hitung nilai dan pindah ke halaman hasil."""
        # Ambil metrik audio riil dari controller
        audio_metrics = self.controller.get_audio_metrics()
        intonasi = audio_metrics["intonasi_score"]

        # Gunakan confidence model sebagai nilai bibir & artikulasi
        bibir      = int(self._last_confidence * 100) if self._last_confidence > 0 else random.randint(50, 80)
        artikulasi = bibir
        total_nilai = int((artikulasi + intonasi + bibir) / 3)

        import datetime
        try:
            from web.server_gamifikasi import broadcast_update
            is_correct = total_nilai >= 60
            broadcast_update({
                "status": "active",
                "target_word": self.current_word,
                "predicted_word": self.current_word if is_correct else "Belum Tepat",
                "confidence": self._last_confidence,
                "correct": is_correct,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "artikulasi": artikulasi,
                "intonasi": intonasi,
                "bibir": bibir,
                "total_nilai": total_nilai,
                "mode": "Ujian" if self.is_ujian_mode else "Latihan"
            })
        except Exception as e:
            print(f"Gagal broadcast: {e}")

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
    def __init__(self, parent_stack):
        super().__init__()
        self.stack = parent_stack
        self.is_ujian = False
        self.current_idx = 1
        self.total_words = 8
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

        body_layout = QVBoxLayout()
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_nilai_title = QLabel("Nilai")
        self.lbl_nilai_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nilai_title.setStyleSheet("font-size: 36px; color: #000000;")

        self.lbl_nilai_val = QLabel("%")
        self.lbl_nilai_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nilai_val.setStyleSheet("font-size: 32px; font-weight: bold; color: #000000; margin-bottom: 20px;")

        body_layout.addStretch(1)
        body_layout.addWidget(self.lbl_nilai_title)
        body_layout.addWidget(self.lbl_nilai_val)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(60)
        metrics_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col_art = QVBoxLayout()
        lbl_art_title = QLabel("Artikulasi")
        lbl_art_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_art_title.setStyleSheet("font-size: 28px; color: #000000;")
        self.lbl_art_val = QLabel("%")
        self.lbl_art_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_art_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        col_art.addWidget(lbl_art_title)
        col_art.addWidget(self.lbl_art_val)

        col_int = QVBoxLayout()
        lbl_int_title = QLabel("Intonasi")
        lbl_int_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_int_title.setStyleSheet("font-size: 28px; color: #000000;")
        self.lbl_int_val = QLabel("%")
        self.lbl_int_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_int_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        col_int.addWidget(lbl_int_title)
        col_int.addWidget(self.lbl_int_val)

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

    def set_results(self, total_nilai, artikulasi, intonasi, bibir, is_ujian=False, current_idx=1, total_words=8):
        self.is_ujian = is_ujian
        self.current_idx = current_idx
        self.total_words = total_words

        self.lbl_nilai_val.setText(f"{total_nilai}%")
        self.lbl_art_val.setText(f"{artikulasi}%")
        self.lbl_int_val.setText(f"{intonasi}%")
        self.lbl_bib_val.setText(f"{bibir}%")

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
        action_page = self.stack.widget(2)
        action_page.setup_mode(
            word=action_page.current_word,
            is_ujian=self.is_ujian,
            current_idx=self.current_idx,
            total_words=self.total_words
        )
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
        self.latihan_page = LatihanWidget(self.stacked_widget)
        self.action_page = WordActionWidget(self.stacked_widget, self.controller)
        self.result_page = ResultWidget(self.stacked_widget)

        self.stacked_widget.addWidget(self.welcome_page) # Index 0
        self.stacked_widget.addWidget(self.latihan_page) # Index 1
        self.stacked_widget.addWidget(self.action_page)  # Index 2
        self.stacked_widget.addWidget(self.result_page)  # Index 3

        self.controller.camera_frame.connect(self.action_page.update_camera_frame)
        self.controller.waveform_updated.connect(self.action_page.update_waveform)
        self.controller.correction_updated.connect(self.action_page.on_correction_updated)
        self.controller.error.connect(lambda msg: print(f"[ERROR] {msg}"))

    def closeEvent(self, event):
        self.controller.shutdown()
        super().closeEvent(event)

def start_web_server():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec())