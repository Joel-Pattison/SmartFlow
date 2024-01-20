from GTPInterface import run_conversation
from src.ui.ui import init_ui
from src.voice.voice import Voice
from src.voice.key_listener import KeyListener

if __name__ == "__main__":
    global_voice = Voice()
    global_key_listener = KeyListener(global_voice)
    init_ui(global_key_listener)
