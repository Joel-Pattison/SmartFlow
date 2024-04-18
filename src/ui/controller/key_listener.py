from pynput import keyboard
import threading


class KeyListener:
    def __init__(self, voice, win, settings_manager):
        self.settings_manager = settings_manager
        self.win = win
        self.voice_key = 'r'
        self.voice = voice
        self.listener = None
        self.listener_thread = threading.Thread(target=self.start_listening)
        self.listener_thread.start()
        self.currently_pressed_keys = set()
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
        self.currently_pressed_keys.add(key)
        if self.win.is_entering_keybind:
            self.update_entering_keybind_display()
        elif self.check_recording_keys() and not self.is_recording:
            self.start_recording()

    def on_release(self, key):
        self.currently_pressed_keys.discard(key)
        if self.win.is_entering_keybind and len(self.currently_pressed_keys) == 0:
            self.set_new_keybind()
        elif self.is_recording and not self.check_recording_keys():
            self.stop_recording()

    def check_recording_keys(self):
        required_keys_str = self.settings_manager.get_voice_toggle_key()
        required_keys = {k for k in required_keys_str.split(' + ')}

        normalized_required_keys = set(map(str, required_keys))
        normalized_current_keys = set(map(str, self.currently_pressed_keys))

        return normalized_required_keys.issubset(normalized_current_keys)

    def start_recording(self):
        self.is_recording = True
        self.win.change_ui_voice_listening_visual(True)
        self.voice.enable_recording()

    def stop_recording(self):
        self.win.change_ui_voice_listening_visual(False)
        # self.voice.disable_recording()
        self.is_recording = False
        self.voice.disable_recording()

    def update_entering_keybind_display(self):
        keybind_str = " + ".join([str(k) for k in self.currently_pressed_keys])
        self.win.toggle_voice_txt.setText(keybind_str)

    def set_new_keybind(self):
        new_keybind = self.win.toggle_voice_txt.text()
        self.settings_manager.set_voice_toggle_key(new_keybind)
        self.win.toggle_voice_txt.setText("Keybind set to: " + new_keybind)
