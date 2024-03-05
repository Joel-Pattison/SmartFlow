import time
import json
import subprocess
from enum import Enum
from typing import List, Optional

from screeninfo import get_monitors
import os
import pyautogui
import ctypes
from pygetwindow import getWindowsWithTitle
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import wmi


class OpenAppEnum(str, Enum):
    left = 'left'
    right = 'right'
    top_left = 'top left'
    bottom_left = 'bottom left'
    top_right = 'top right'
    bottom_right = 'bottom right'
    invalid = 'invalid'


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
    def open_app(app_names: List[str], locations: Optional[List[OpenAppEnum]] = None):
        print(app_names, locations)
        if locations is None:
            locations = ["NULL"] * len(app_names)

        for app_name, location in zip(app_names, locations):
            find_and_run_app(app_name)
            if location != "NULL":
                set_app_location(app_name, location)
            AutomationFunctions.app_profiles[app_name] = location

    @staticmethod
    def change_volume(volume_level):
        # Convert the volume from percentage to a float between 0.0 and 1.0
        volume_level = volume_level / 100.0

        # Get the default audio device using AudioUtilities
        devices = AudioUtilities.GetSpeakers()

        # Get the interface to the volume control
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Set the master volume to the desired level
        volume.SetMasterVolumeLevelScalar(volume_level, None)
        print(f"System volume set to {volume_level}%")


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
    # location is a enum not a string so must be converted to string
    location = location.value
    window = None
    loops = 0

    while window is None and loops < 4:  # Check the condition here to limit attempts
        for win in getWindowsWithTitle(app_name):
            window = win
        if window is None:
            loops += 1
            print("Waiting for window to appear")
            time.sleep(0.5)

    print(getWindowsWithTitle(app_name), "to location:", location)

    if window is None:
        print(f"No visible window found for: {app_name}")
        return

    screen_width, screen_height = pyautogui.size()

    if location == "left" or location == "l":
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


def set_brightness(level):
    # Initialize the WMI interface
    wmi_interface = wmi.WMI(namespace='wmi')

    # Get the 'WmiMonitorBrightnessMethods' class to access the brightness methods
    methods = wmi_interface.WmiMonitorBrightnessMethods()[0]

    # Set the brightness level
    # The first parameter (Timeout) is set to 0, as it's not used in this context
    methods.WmiSetBrightness(Brightness=level, Timeout=0)

    print(f"Brightness set to {level}%.")
