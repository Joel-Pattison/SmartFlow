from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from src.ui.controller.main_view_controller import MainWindow


def init_ui(key_listener):
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.aboutToQuit.connect(key_listener.stop_listening)
    sys.exit(app.exec_())
