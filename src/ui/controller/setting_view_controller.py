import ctypes
import os

import pyaudio
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtWidgets import QApplication

from src.ui.view.settings_view import Ui_Form
from qframelesswindow import FramelessMainWindow
from qframelesswindow import FramelessWindow
from PyQt5.QtCore import pyqtSignal, Qt


class SettingsWindow(FramelessMainWindow, Ui_Form):
    update_voice_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # self.hide()

        # self.update_visibility(False)

    def update_visibility(self, visibility):
        if visibility:
            self.setWindowOpacity(1.0)
            self.set_movie("listening")
        else:
            # self.setWindowOpacity(0.0)
            self.set_movie("loading")