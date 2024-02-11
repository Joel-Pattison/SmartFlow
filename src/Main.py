from src.settings.settings_manager import SettingsManager
from src.voice.models.google_model import Google
from src.voice.models.whisper_model import Whisper
from src.voice.voice import Voice
from src.ui.controller.key_listener import KeyListener
from PyQt5.QtWidgets import QApplication
import sys
from src.ui.controller.main_view_controller import MainWindow
from src.llm.conversation import LLMConversation


def initialize_voice_models():
    models = {
        "whisper base": Whisper("base.en"),
        "whisper small": Whisper("small.en"),
        "whisper medium": Whisper("medium.en"),
        "whisper large": Whisper("large-v3"),
        "google": Google(),
    }
    return models


if __name__ == "__main__":
    voice_models = initialize_voice_models()

    settings_manager = SettingsManager()
    llm_conversation = LLMConversation(settings_manager)

    app = QApplication(sys.argv)
    win = MainWindow(settings_manager, llm_conversation, voice_models)
    win.show()

    global_voice = Voice(settings_manager, llm_conversation, voice_models)
    key_listener = KeyListener(global_voice, win, settings_manager)

    app.aboutToQuit.connect(key_listener.stop_listening)
    sys.exit(app.exec_())
