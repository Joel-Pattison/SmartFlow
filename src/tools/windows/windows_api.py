import asyncio
import time
import json
import subprocess
import winreg
from enum import Enum
from typing import List, Optional

import os
import pyautogui
from pygetwindow import getWindowsWithTitle
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from winsdk.windows.devices.radios import Radio, RadioKind, RadioState
import wmi


def shutdown_computer():
    c = wmi.WMI()
    for thisOS in c.Win32_OperatingSystem():
        # The flag 0 + 2 = 2 means "Shutdown"
        thisOS.Win32Shutdown(2)
        print("Shutting down the computer gracefully...")


def restart_computer():
    c = wmi.WMI()
    for thisOS in c.Win32_OperatingSystem():
        # The flag 0 + 4 = 4 means "Restart"
        thisOS.Win32Shutdown(4)
        print("Restarting the computer gracefully...")


def sleep_computer():
    c = wmi.WMI()
    for thisOS in c.Win32_OperatingSystem():
        thisOS.Win32Shutdown(1)
        print("Putting the computer to sleep gracefully...")


def toggle_theme_mode(dark_mode=True):
    # Define registry path and value name
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    value_name_ui = "AppsUseLightTheme"
    value_name_system = "SystemUsesLightTheme"

    # Define the value: 0 for Dark mode, 1 for Light mode
    value_data = 0 if dark_mode else 1

    try:
        # Open the registry key
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as reg_key:
                # Set the value for both UI and system
                winreg.SetValueEx(reg_key, value_name_ui, 0, winreg.REG_DWORD, value_data)
                winreg.SetValueEx(reg_key, value_name_system, 0, winreg.REG_DWORD, value_data)
                print(f"Theme set to {'Dark' if dark_mode else 'Light'} mode.")

                try:
                    c = wmi.WMI()
                    for process in c.Win32_Process(name="explorer.exe"):
                        process.Terminate()  # Terminate existing explorer.exe process

                    # Start a new instance of explorer.exe
                    c.Win32_Process.Create(CommandLine="explorer.exe")
                    print("Explorer.exe restarted successfully.")
                except Exception as e:
                    print(f"Failed to restart explorer.exe: {e}")
    except Exception as e:
        print(f"Failed to change theme mode: {e}")


def toggle_night_light(enable_night_mode):
    STATUS_PATH = "Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate"
    STATE_VALUE_NAME = "Data"

    def get_night_light_state_data():
        try:
            hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATUS_PATH, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(hKey, STATE_VALUE_NAME)
            winreg.CloseKey(hKey)
            if regtype == winreg.REG_BINARY:
                return value
        except Exception as e:
            print(f"Error getting night light state: {e}")
            return False

    def write_data_to_registry(byte_array):
        try:
            hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATUS_PATH, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(hKey, STATE_VALUE_NAME, 0, winreg.REG_BINARY, byte_array)
            winreg.CloseKey(hKey)
            return True
        except Exception as e:
            print(f"Error writing night light state: {e}")
            return False

    value = get_night_light_state_data()
    if value:
        reg_val = bytearray(value)
        write_data_to_registry(reg_val)
        print("Night Light state changed successfully.")
    else:
        print("Failed to toggle Night Light.")


async def bluetooth_power(turn_on):
    all_radios = await Radio.get_radios_async()
    for this_radio in all_radios:
        if this_radio.kind == RadioKind.BLUETOOTH:
            await this_radio.set_state_async(RadioState.ON if turn_on else RadioState.OFF)
            print(f"Bluetooth turned {'on' if turn_on else 'off'}.")


async def toggle_wifi(turn_on):
    all_radios = await Radio.get_radios_async()
    for this_radio in all_radios:
        if this_radio.kind == RadioKind.WI_FI:  # Check if the radio is WiFi
            await this_radio.set_state_async(RadioState.ON if turn_on else RadioState.OFF)
            print(f"WiFi turned {'on' if turn_on else 'off'}.")


class OpenAppEnum(str, Enum):
    left = 'left'
    right = 'right'
    top_left = 'top left'
    bottom_left = 'bottom left'
    top_right = 'top right'
    bottom_right = 'bottom right'
    invalid = 'invalid'


# this is a enum with functions as values
class WindowsSettingsInteractionEnum(str, Enum):
    SHUT_DOWN_COMPUTER = "shut_down_computer"
    RESTART_COMPUTER = "restart_computer"
    SLEEP_COMPUTER = "sleep_computer"
    TURN_ON_DARK_MODE = "turn_on_dark_mode"
    TURN_ON_LIGHT_MODE = "turn_on_light_mode"
    TURN_ON_NIGHT_LIGHT = "turn_on_night_light"
    TURN_OFF_NIGHT_LIGHT = "turn_off_night_light"
    TURN_ON_BLUETOOTH = "turn_on_bluetooth"
    TURN_OFF_BLUETOOTH = "turn_off_bluetooth"
    TURN_ON_WIFI = "turn_on_wifi"
    TURN_OFF_WIFI = "turn_off_wifi"


class AutomationFunctions:
    app_profiles = {}

    def __init__(self, win, settings_manager):
        self.win = win
        self.settings_manager = settings_manager

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

    def open_app(self, app_names: List[str], locations: Optional[List[OpenAppEnum]] = None):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.open_app(app_names, locations))
            self.win.display_action_confirmer(f"Open app(s) {app_names} at location(s) {locations}?")
            return

        print(app_names, locations)
        if locations is None:
            locations = ["NULL"] * len(app_names)

        for app_name, location in zip(app_names, locations):
            find_and_run_app(app_name)
            if location != "NULL":
                set_app_location(app_name, location)
            AutomationFunctions.app_profiles[app_name] = location

    def change_volume(self, volume_level):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.change_volume(volume_level))
            self.win.display_action_confirmer(f"Change volume to {volume_level}%?")
            return

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

    def set_brightness(self, level):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.set_brightness(level))
            self.win.display_action_confirmer(f"Set brightness to {level}%?")
            return

        # Initialize the WMI interface
        wmi_interface = wmi.WMI(namespace='wmi')

        # Get the 'WmiMonitorBrightnessMethods' class to access the brightness methods
        methods = wmi_interface.WmiMonitorBrightnessMethods()[0]

        # Set the brightness level
        methods.WmiSetBrightness(Brightness=level, Timeout=0)

        print(f"Brightness set to {level}%.")

    def windows_settings_interaction(self, interaction: WindowsSettingsInteractionEnum):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.windows_settings_interaction(interaction))
            self.win.display_action_confirmer(f"Perform {interaction} action?")
            return

        print("Interaction received:", interaction)
        try:
            if interaction == WindowsSettingsInteractionEnum.SHUT_DOWN_COMPUTER:
                shutdown_computer()
            elif interaction == WindowsSettingsInteractionEnum.RESTART_COMPUTER:
                restart_computer()
            elif interaction == WindowsSettingsInteractionEnum.SLEEP_COMPUTER:
                sleep_computer()
            elif interaction in [WindowsSettingsInteractionEnum.TURN_ON_DARK_MODE,
                                 WindowsSettingsInteractionEnum.TURN_ON_LIGHT_MODE]:
                dark_mode = interaction == WindowsSettingsInteractionEnum.TURN_ON_DARK_MODE
                toggle_theme_mode(dark_mode)
            elif interaction in [WindowsSettingsInteractionEnum.TURN_ON_NIGHT_LIGHT,
                                 WindowsSettingsInteractionEnum.TURN_OFF_NIGHT_LIGHT]:
                enable_night_mode = interaction == WindowsSettingsInteractionEnum.TURN_ON_NIGHT_LIGHT
                print(enable_night_mode)
                toggle_night_light(enable_night_mode)
            elif interaction in [WindowsSettingsInteractionEnum.TURN_ON_BLUETOOTH,
                                 WindowsSettingsInteractionEnum.TURN_OFF_BLUETOOTH]:
                turn_on = interaction == WindowsSettingsInteractionEnum.TURN_ON_BLUETOOTH
                asyncio.run(bluetooth_power(turn_on))
            elif interaction in [WindowsSettingsInteractionEnum.TURN_ON_WIFI,
                                 WindowsSettingsInteractionEnum.TURN_OFF_WIFI]:
                turn_on = interaction == WindowsSettingsInteractionEnum.TURN_ON_WIFI
                asyncio.run(toggle_wifi(turn_on))
        except Exception as e:
            print(f"Error performing interaction: {e.with_traceback(None)}")


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
