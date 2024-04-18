import os.path
import pickle


class SettingsManager:
    settings = {
        "mic_index": None,
        "mic_name": None,
        "voice_toggle_key": "r",
        "selected_model": None,
        "openai_api_key": None,
        "voice_model": None,
        "confirm_actions": True,
        "use_popup_window": True
    }
    save_file = "settings.save"

    def __init__(self):
        if os.path.isfile("settings.save"):
            print("Settings file found: loading...")
            self.load_save()
        else:
            print("No settings file found: creating...")
            self.update_save()

    def load_save(self):
        with open(self.save_file, "rb") as file:
            self.settings = pickle.load(file)

    def update_save(self):
        with open(self.save_file, "wb") as file:
            pickle.dump(self.settings, file)

    def set_microphone_index(self, index):
        self.settings["mic_index"] = index
        self.update_save()

    def get_microphone_index(self):
        return self.settings["mic_index"]

    def set_microphone_name(self, name):
        self.settings["mic_name"] = name
        self.update_save()

    def get_microphone_name(self):
        return self.settings["mic_name"]

    def set_voice_toggle_key(self, key):
        self.settings["voice_toggle_key"] = key
        self.update_save()

    def get_voice_toggle_key(self):
        return self.settings["voice_toggle_key"]

    def set_openai_api_key(self, key):
        self.settings["openai_api_key"] = key
        self.update_save()

    def get_openai_api_key(self):
        return self.settings["openai_api_key"]

    def set_voice_model(self, model):
        self.settings["voice_model"] = model
        self.update_save()

    def get_voice_model(self):
        return self.settings["voice_model"]

    def set_confirm_actions(self, confirm):
        self.settings["confirm_actions"] = confirm
        self.update_save()

    def get_confirm_actions(self):
        return self.settings["confirm_actions"]

    def set_use_popup_window(self, use_popup_window):
        self.settings["use_popup_window"] = use_popup_window
        self.update_save()

    def get_use_popup_window(self):
        return self.settings["use_popup_window"]