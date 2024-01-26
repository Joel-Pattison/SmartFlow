import os.path
import pickle


class SettingsManager:
    settings = {
        "mic_index": None,
        "mic_name": None,
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
