import pyaudio
from PyQt5.QtCore import QEvent

from src.ui.controller.popup_view_controller import PopupWindow
from src.ui.view.main_view import Ui_Form
from qframelesswindow import FramelessMainWindow
from PyQt5.QtCore import pyqtSignal


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
    update_voice_text_signal = pyqtSignal(str)

    def __init__(self, settings_manager, voice_models):
        super().__init__()
        self.llm_conversation = None
        self.settings_manager = settings_manager
        self.voice_models = voice_models
        self.setupUi(self)
        self.send_loading_ring.hide()
        self.action_description_lbl.hide()
        self.action_execute_btn.hide()
        self.action_cancel_btn.hide()
        self.action_description_background_lbl.hide()
        self.is_entering_keybind = False
        self.action_to_execute = None
        self.has_confirmed_action = False
        self.popupWindow = None

        self.update_voice_text_signal.connect(self.update_voice_text_label)

        self.populate_voice_model_cmb()
        self.load_voice_model_settings()
        self.voice_cmb.currentIndexChanged.connect(self.on_voice_cmb_changed)

        self.populate_microphone_cmb()
        self.load_microphone_settings()
        self.microphone_cmb.currentIndexChanged.connect(self.on_microphone_cmb_changed)

        self.toggle_voice_txt.setReadOnly(True)
        self.toggle_voice_txt.setText(self.settings_manager.get_voice_toggle_key())
        self.toggle_voice_txt.installEventFilter(self)

        self.load_openai_api_key()
        self.OpenAi_key_txt.textChanged.connect(self.on_openai_key_txt_changed)

        self.send_command_btn.clicked.connect(self.on_send_command_btn_clicked)

        if self.settings_manager.get_use_popup_window():
            if not self.popupWindow:
                self.popupWindow = PopupWindow()
            self.popupWindow.show()

        if self.settings_manager.get_use_popup_window():
            self.popupWindow.action_execute_btn.clicked.connect(self.on_action_execute_btn_click)
            self.popupWindow.action_cancel_btn.clicked.connect(self.on_action_cancel_btn_click)
        else:
            self.action_execute_btn.clicked.connect(self.on_action_execute_btn_click)
            self.action_cancel_btn.clicked.connect(self.on_action_cancel_btn_click)

    def eventFilter(self, watched, event):
        if watched == self.toggle_voice_txt and event.type() == QEvent.FocusIn:
            self.toggle_voice_txt.setText("enter keys...")
            self.is_entering_keybind = True
        elif watched == self.toggle_voice_txt and event.type() == QEvent.FocusOut:
            self.toggle_voice_txt.setText(self.settings_manager.get_voice_toggle_key())
            self.is_entering_keybind = False

        return super().eventFilter(watched, event)

    def populate_voice_model_cmb(self):
        self.voice_cmb.addItems(self.voice_models.keys())

    def change_ui_action_confirmer_visual(self, is_open):
        if self.settings_manager.get_use_popup_window():
            self.popupWindow.change_ui_action_confirmer_visual(is_open)
        else:
            self.action_description_lbl.setVisible(is_open)
            self.action_execute_btn.setVisible(is_open)
            self.action_cancel_btn.setVisible(is_open)
            self.action_description_background_lbl.setVisible(is_open)

    def display_action_confirmer(self, action_description):
        self.action_description_lbl.setText(action_description)
        self.change_ui_action_confirmer_visual(True)

        # if self.settings_manager.get_use_popup_window():
        #     self.popupWindow.display_action_confirmer(action_description)
        # else:
        #     self.action_description_lbl.setText(action_description)
        #     self.change_ui_action_confirmer_visual(True)

    def bind_action_to_execute(self, action):
        self.action_to_execute = action

    def on_action_execute_btn_click(self):
        print("Action confirmed")
        self.change_ui_action_confirmer_visual(False)
        self.has_confirmed_action = True
        self.action_to_execute()
        self.has_confirmed_action = False

    def on_action_cancel_btn_click(self):
        self.last_action_confirmer_result = False
        self.change_ui_action_confirmer_visual(False)

    def load_voice_model_settings(self):
        if self.settings_manager.get_voice_model() is None:
            print("No voice model found in settings")
            self.settings_manager.set_voice_model(self.voice_cmb.currentText())
            self.voice_models[self.voice_cmb.currentText()].load_model()
            return
        voice_model = self.settings_manager.get_voice_model()
        self.voice_models[self.settings_manager.get_voice_model()].load_model()
        voice_model_index = self.voice_cmb.findText(voice_model)
        if voice_model_index != -1:
            print("Voice model found in list: " + voice_model)
            self.voice_cmb.setCurrentIndex(voice_model_index)
        else:
            print("Voice model not found in list: " + voice_model)
            self.settings_manager.set_voice_model(self.voice_cmb.currentText())

    def on_voice_cmb_changed(self):
        print("Voice model changed: " + self.voice_cmb.currentText())
        # unload old model
        self.voice_models[self.settings_manager.get_voice_model()].unload_model()
        self.settings_manager.set_voice_model(self.voice_cmb.currentText())
        self.voice_models[self.voice_cmb.currentText()].load_model()

    def populate_microphone_cmb(self):
        self.microphone_cmb.addItems(get_microphone_list())

    def get_selected_microphone_index(self):
        return self.microphone_cmb.currentIndex()

    def change_ui_voice_listening_visual(self, is_listening):
        print("Changing voice listening visual to: " + str(is_listening))
        if (self.settings_manager.get_use_popup_window()):
            if is_listening:
                self.popupWindow.update_visibility(True)
            else:
                self.popupWindow.update_visibility(False)
        else:
            self.voice_status_radio.setChecked(is_listening)

    def load_openai_api_key(self):
        if self.settings_manager.get_openai_api_key() is None:
            print("No openai api key found in settings")
            return
        self.OpenAi_key_txt.setText(self.settings_manager.get_openai_api_key())

    def on_openai_key_txt_changed(self, text):
        self.settings_manager.set_openai_api_key(text)

    def on_send_command_btn_clicked(self):
        if self.command_txt.toPlainText() == "":
            return
        prompt = self.command_txt.toPlainText()
        self.command_txt.setText("")
        self.llm_conversation.run_conversation(prompt)

    def set_llm_conversation(self, llm_conversation):
        self.llm_conversation = llm_conversation

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

    def update_voice_text_label(self, text):
        if (self.settings_manager.get_use_popup_window()):
            self.popupWindow.update_voice_text_label(text)
        else:
            self.voice_text_txt.setText(text)
