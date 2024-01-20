import pyaudio
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
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.send_loading_ring.hide()
        self.populate_microphone_cmb()

    def populate_microphone_cmb(self):
        self.microphone_cmb.addItems(get_microphone_list())

    def get_selected_microphone_index(self):
        return self.microphone_cmb.currentIndex()

