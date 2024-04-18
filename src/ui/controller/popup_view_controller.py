import ctypes
import os

import pyaudio
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtWidgets import QApplication

from src.ui.view.popup import Ui_Form
from qframelesswindow import FramelessMainWindow
from qframelesswindow import FramelessWindow
from PyQt5.QtCore import pyqtSignal, Qt


class PopupWindow(FramelessMainWindow, Ui_Form):
    update_voice_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.movie = QMovie("ui/resources/listening.webp")
        # self.movie = QMovie("ui/resources/listening_original.gif")

        self.listening_movie = QMovie("ui/resources/listening.webp")
        self.waiting_movie = QMovie("ui/resources/waiting.webp")
        self.loading_movie = QMovie("ui/resources/loading.webp")

        # self.action_execute_btn.setVisible(False)
        # self.action_cancel_btn.setVisible(False)
        # self.action_description_lbl.setVisible(False)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # self.setWindowOpacity(0.3)

        # self.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

        self.current_movie = self.listening_movie
        self.assistant_gif_lbl.setMovie(self.current_movie)
        self.current_movie.setScaledSize(self.assistant_gif_lbl.size())
        self.current_movie.start()

        self.change_ui_action_confirmer_visual(False)

        # self.action_description_lbl.setCursor(Qt.ArrowCursor)
        # self.action_description_lbl.setTextInteractionFlags(Qt.NoTextInteraction)

        self.move_to_bottom_left()

        # self.setVisible(False)
        self.update_visibility(False)
        # QTimer.singleShot(0, lambda: self.update_visibility(False))

    def set_movie(self, movie_state):
        if movie_state == "listening":
            new_movie = self.listening_movie
        elif movie_state == "waiting":
            new_movie = self.waiting_movie
        elif movie_state == "loading":
            new_movie = self.loading_movie

        if self.current_movie != new_movie:
            self.assistant_gif_lbl.setMovie(new_movie)
            self.current_movie = new_movie
            self.current_movie.setScaledSize(self.assistant_gif_lbl.size())
            self.current_movie.start()

    def update_visibility(self, visibility):
        if visibility:
            self.setWindowOpacity(1.0)
            self.set_movie("listening")
        else:
            # self.setWindowOpacity(0.0)
            self.set_movie("loading")

    def move_to_bottom_left(self):
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        window_width = self.width()
        window_height = self.height()
        self.move(0, screen_rect.height() - window_height)

    def update_voice_text_label(self, text):
        self.voice_text_lbl.setText(text)

    def change_ui_action_confirmer_visual(self, is_open):
        print("Changing action confirmer visual to: " + str(is_open))
        print("making description visible: " + str(is_open))
        self.action_description_lbl.setVisible(is_open)
        print("making execute visible: " + str(is_open))
        self.action_execute_btn.setVisible(is_open)
        print("making cancel visible: " + str(is_open))
        self.action_cancel_btn.setVisible(is_open)
        # if is_open:
        #     self.set_movie("waiting")

    def display_action_confirmer(self, action_description):
        self.action_description_lbl.setText(action_description)
        self.change_ui_action_confirmer_visual(True)
