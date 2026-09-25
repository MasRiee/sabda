import os
import sys

# Suppress verbose TensorFlow, MediaPipe, and ABSL C++ log outputs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
os.environ["ABSL_LOGGING_MIN_SEVERITY"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

try:
    import absl.logging

    absl.logging.set_verbosity(absl.logging.ERROR)
    absl.logging.set_stderrthreshold("error")
except ImportError:
    pass

from backend.app_controller import AppController
from PyQt6.QtWidgets import QApplication

from ui.mainuiv2 import MainWindow


def main():
    qtapp = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qtapp.exec())


if __name__ == "__main__":
    main()
