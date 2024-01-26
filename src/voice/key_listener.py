from pynput import keyboard
import threading

from src.voice.voice import Voice


class KeyListener:
    def __init__(self, voice, win):
        self.win = win
        self.voice_key = 'r'
        self.voice = voice
        self.listener = None
        self.listener_thread = threading.Thread(target=self.start_listening)
        self.listener_thread.start()

    def start_listening(self):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        with self.listener:
            self.listener.join()

    def stop_listening(self):
        if self.listener:
            self.listener.stop()
        print("Stopped listening for key presses")
        self.listener_thread.join()

    def on_press(self, key):
        try:
            if key.char == self.voice_key and self.voice:
                self.win.change_ui_voice_listening_visual(True)
                self.voice.enable_recording()
        except AttributeError:
            pass

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char(self.voice_key):
            self.win.change_ui_voice_listening_visual(False)
            self.voice.disable_recording()
