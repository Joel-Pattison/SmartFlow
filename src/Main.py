from GTPInterface import run_conversation
from src.settings.settings_manager import SettingsManager
from src.voice.voice import Voice
from src.voice.key_listener import KeyListener
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from src.ui.controller.main_view_controller import MainWindow

if __name__ == "__main__":
    settings_manager = SettingsManager()

    app = QApplication(sys.argv)
    win = MainWindow(settings_manager)
    win.show()

    global_voice = Voice(settings_manager)
    key_listener = KeyListener(global_voice, win)

    app.aboutToQuit.connect(key_listener.stop_listening)
    sys.exit(app.exec_())
