import pyaudio
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from src.ui.view.main_view import Ui_Form
from qframelesswindow import FramelessWindow, FramelessMainWindow, StandardTitleBar
import sys


def get_microphone_list():
    audio_interface = pyaudio.PyAudio()
    info = audio_interface.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    microphone_list = []
    for i in range(0, num_devices):
        if audio_interface.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            mic_name = audio_interface.get_device_info_by_host_api_device_index(0, i).get('name')
            microphone_list.append(mic_name)

    audio_interface.terminate()
    return microphone_list


class MainWindow(FramelessMainWindow, Ui_Form):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setupUi(self)
        self.send_loading_ring.hide()
        self.populate_microphone_cmb()
        self.load_microphone_settings()
        self.microphone_cmb.currentIndexChanged.connect(self.on_microphone_cmb_changed)
        self.toggle_voice_txt.setReadOnly(True)
        self.toggle_voice_txt.setText(self.settings_manager.get_voice_toggle_key())
        self.toggle_voice_txt.installEventFilter(self)
        self.is_entering_keybind = False

    def eventFilter(self, watched, event):
        if watched == self.toggle_voice_txt and event.type() == QEvent.FocusIn:
            self.toggle_voice_txt.setText("enter keys...")
            self.is_entering_keybind = True
        elif watched == self.toggle_voice_txt and event.type() == QEvent.FocusOut:
            self.toggle_voice_txt.setText(self.settings_manager.get_voice_toggle_key())
            self.is_entering_keybind = False

        return super().eventFilter(watched, event)

    def populate_microphone_cmb(self):
        self.microphone_cmb.addItems(get_microphone_list())

    def get_selected_microphone_index(self):
        return self.microphone_cmb.currentIndex()

    def change_ui_voice_listening_visual(self, is_listening):
        self.voice_status_radio.setChecked(is_listening)

    def load_microphone_settings(self):
        if self.settings_manager.get_microphone_name() is None:
            print("No microphone name found in settings: setting to current microphone")
            self.settings_manager.set_microphone_name(self.microphone_cmb.currentText())
            self.settings_manager.set_microphone_index(self.microphone_cmb.currentIndex())
            return

        mic_name = self.settings_manager.get_microphone_name()
        mic_index = self.microphone_cmb.findText(mic_name)

        if mic_index != -1:
            print("Microphone name found in list: " + mic_name)
            self.microphone_cmb.setCurrentIndex(mic_index)
        else:
            print("Microphone name not found in list: " + mic_name)
            self.settings_manager.set_microphone_name(self.microphone_cmb.currentText())
            self.settings_manager.set_microphone_index(self.microphone_cmb.currentIndex())

    def on_microphone_cmb_changed(self):
        print("Microphone changed: " + self.microphone_cmb.currentText())
        self.settings_manager.set_microphone_name(self.microphone_cmb.currentText())
        self.settings_manager.set_microphone_index(self.microphone_cmb.currentIndex())
