from src.settings.settings_manager import SettingsManager
from src.voice.voice import Voice
from src.voice.key_listener import KeyListener
from PyQt5.QtWidgets import QApplication
import sys
from src.ui.controller.main_view_controller import MainWindow
from src.llm.conversation import LLMConversation

if __name__ == "__main__":
    settings_manager = SettingsManager()

    app = QApplication(sys.argv)
    win = MainWindow(settings_manager)
    win.show()

    llm_conversation = LLMConversation(settings_manager)
    global_voice = Voice(settings_manager)
    key_listener = KeyListener(global_voice, win, settings_manager)

    app.aboutToQuit.connect(key_listener.stop_listening)
    sys.exit(app.exec_())
