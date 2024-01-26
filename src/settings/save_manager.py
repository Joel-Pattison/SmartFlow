import os.path
import pickle


class SettingsManager:
    settings = {
        "mic_index": "mic_index",
        "mic_name": "mic_name",
    }
    save_file = "settings.save"

    def __init__(self):
        if os.path.isfile("settings.txt"):
            self.load_save()
        else:
            self.create_save()

    def load_save(self):
        print("Settings file found: loading...")
        with open(self.save_file, "rb") as file:
            self.settings = pickle.load(file)

    def create_save(self):
        print("No settings file found: creating...")
        with open(self.save_file, "wb") as file:
            pickle.dump(self.settings, file)