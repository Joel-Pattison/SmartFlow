import time
import json
import subprocess
from screeninfo import get_monitors
import os
import pyautogui
import ctypes
from pygetwindow import getWindowsWithTitle


class AutomationFunctions:
    app_profiles = {}

    @staticmethod
    def save_profile(profile_name):
        if not os.path.exists("profiles"):
            os.makedirs("profiles")
        with open(f"profiles/{profile_name}.txt", "w") as outfile:
            json.dump(AutomationFunctions.app_profiles, outfile)

    @staticmethod
    def load_profile(profile_name):
        with open(f"profiles/{profile_name}.txt", "r") as infile:
            AutomationFunctions.app_profiles = json.load(infile)
            for app_name, location in AutomationFunctions.app_profiles.items():
                AutomationFunctions.open_app([app_name], [location])

    @staticmethod
    def open_app(app_names, locations="NULL"):
        if locations is None:
            locations = ["NULL"] * len(app_names)

        for app_name, location in zip(app_names, locations):
            find_and_run_app(app_name)
            if location != "NULL":
                set_app_location(app_name, location)
            AutomationFunctions.app_profiles[app_name] = location

    @staticmethod
    def change_volume(volume_level):
        ctypes.windll.winmm.waveOutSetVolume(0, volume_level * 65535 // 100)


def find_and_run_app(app_name):
    paths = [
        os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs')
    ]

    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".lnk") and app_name.lower() in file.lower():
                    shortcut_path = os.path.join(root, file)
                    print(f"Running: {shortcut_path}")
                    subprocess.Popen(shortcut_path, shell=True)
                    return

    print(f"No application found for: {app_name}")


def set_app_location(app_name, location):
    window = None
    for win in getWindowsWithTitle(app_name):
        if win.isVisible:
            window = win
            break

    if window is None:
        print(f"No visible window found for: {app_name}")
        return

    screen_width, screen_height = pyautogui.size()

    if location == "left":
        window.moveTo(0, 0)
        window.resizeTo(screen_width // 2, screen_height)
    elif location == "right":
        window.moveTo(screen_width // 2, 0)
        window.resizeTo(screen_width // 2, screen_height)
    elif location == "top left":
        window.moveTo(0, 0)
        window.resizeTo(screen_width // 2, screen_height // 2)
    elif location == "bottom left":
        window.moveTo(0, screen_height // 2)
        window.resizeTo(screen_width // 2, screen_height // 2)
    elif location == "top right":
        window.moveTo(screen_width // 2, 0)
        window.resizeTo(screen_width // 2, screen_height // 2)
    elif location == "bottom right":
        window.moveTo(screen_width // 2, screen_height // 2)
        window.resizeTo(screen_width // 2, screen_height // 2)
