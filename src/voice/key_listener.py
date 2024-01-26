from pynput import keyboard
import threading

from src.voice.voice import Voice


class KeyListener:
    def __init__(self, voice, win, settings_manager):
        self.settings_manager = settings_manager
        self.win = win
        self.voice_key = 'r'
        self.voice = voice
        self.listener = None
        self.listener_thread = threading.Thread(target=self.start_listening)
        self.listener_thread.start()
        self.currently_pressed_keys = []
        self.current_key_sequence = []
        self.is_recording = False

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
        if key not in self.currently_pressed_keys:
            self.currently_pressed_keys.append(key)
            self.current_key_sequence.append(key)
            if self.win.is_entering_keybind:
                self.win.toggle_voice_txt.setText(" + ".join([str(x) for x in self.current_key_sequence]))
                return

        current_key_sequence_str = ' + '.join([str(k) for k in self.current_key_sequence])
        if current_key_sequence_str == self.settings_manager.get_voice_toggle_key() and not self.is_recording:
            self.is_recording = True
            self.win.change_ui_voice_listening_visual(True)
            self.voice.enable_recording()
            return

    def on_release(self, key):
        self.currently_pressed_keys.remove(key)
        if len(self.currently_pressed_keys) == 0:
            self.settings_manager.set_voice_toggle_key(self.win.toggle_voice_txt.text())
            self.current_key_sequence = []
            if self.win.is_entering_keybind:
                self.win.toggle_voice_txt.setText("Keybind set to: " + self.settings_manager.get_voice_toggle_key())
                return

        if self.is_recording:
            self.is_recording = False
            self.win.change_ui_voice_listening_visual(False)
            self.voice.disable_recording()
