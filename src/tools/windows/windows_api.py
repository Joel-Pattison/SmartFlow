import asyncio
import time
import json
import subprocess
import winreg
from enum import Enum
from typing import List, Optional

import os

import psutil
import pyautogui
from pygetwindow import getWindowsWithTitle
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from winsdk.windows.devices.radios import Radio, RadioKind, RadioState
import wmi
import webbrowser
import win32com.client
from fuzzywuzzy import process
from pynput.keyboard import Controller
from pywinauto.application import Application
import re


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


class AmPmEnum(str, Enum):
    am = 'am'
    pm = 'pm'


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

    def write_email(self, recipient_name, subject, body):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.write_email(recipient_name, subject, body))
            self.win.display_action_confirmer(
                f"Write email to {recipient_name} with subject '{subject}' and body '{body}'?")
            return

        try:
            # Find the recipient's email address
            recipient_email = find_email_by_name(recipient_name)
            if recipient_email:
                # Construct the mailto URL with the recipient, subject, and body
                mailto_url = f"mailto:{recipient_email}?subject={subject}&body={body}"
                # Open the default mail client with the pre-filled details
                webbrowser.open(mailto_url)
                print("Opened the default email provider to create a new email.")
            else:
                print("Recipient not found in contacts.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def create_timer(self, hours, minutes, seconds):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            time_parts = []
            if hours > 0:
                time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
            if seconds > 0:
                time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

            if len(time_parts) > 1:
                time_str = ", ".join(time_parts[:-1]) + " and " + time_parts[-1]
            elif time_parts:
                time_str = time_parts[0]
            else:
                time_str = "0 seconds"

            self.win.bind_action_to_execute(lambda: self.create_timer(hours, minutes, seconds))
            self.win.display_action_confirmer(f"Create timer for {time_str}?")
            return

        # Use the PFN of the Windows Alarms & Clock app
        alarms_app_pfn = "Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"

        # Launch the Alarms & Clock app using its PFN
        Application().start(f'explorer.exe shell:appsFolder\\{alarms_app_pfn}')

        app = Application(backend="uia").connect(title="Clock", timeout=20)

        main_win = app.window(title="Clock")

        alarm_button = main_win.child_window(title="Timer", auto_id="TimerButton", control_type="ListItem")
        alarm_button.select()

        main_win.child_window(title="Add new timer", control_type="Button").click()

        keyboard = Controller()

        main_win.child_window(title="hours", control_type="Custom").set_focus()
        keyboard.type(str(hours))

        main_win.child_window(title="minutes", control_type="Custom").set_focus()
        keyboard.type(str(minutes))

        main_win.child_window(title="seconds", control_type="Custom").set_focus()
        keyboard.type(str(seconds))

        main_win.child_window(title="Save", control_type="Button").click()

        main_win.child_window(title="Start", control_type="Button").click()

    def create_alarm(self, hours, minutes, am_pm: AmPmEnum):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            formatted_minutes = f"{minutes:02d}"
            time_str = f"{hours}:{formatted_minutes} {am_pm}"
            self.win.bind_action_to_execute(lambda: self.create_alarm(hours, minutes, am_pm))
            self.win.display_action_confirmer(f"Create alarm for {time_str}?")
            return

        alarms_app_pfn = "Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"

        Application().start(f'explorer.exe shell:appsFolder\\{alarms_app_pfn}')

        app = Application(backend="uia").connect(title="Clock", timeout=20)

        main_win = app.window(title="Clock")

        alarm_button = main_win.child_window(title="Alarm", auto_id="AlarmButton", control_type="ListItem")
        alarm_button.select()

        main_win.child_window(title="Add an alarm", control_type="Button").click()

        keyboard = Controller()

        main_win.child_window(auto_id="HourPicker", control_type="Custom").set_focus()
        keyboard.type(str(hours))

        main_win.child_window(auto_id="MinutePicker", control_type="Custom").set_focus()
        keyboard.type(str(minutes))

        main_win.child_window(auto_id="TwelveHourPicker", control_type="Custom").set_focus()
        keyboard.type(am_pm)

        main_win.child_window(title="Save", control_type="Button").click()

    def install_application(self, app_name):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.install_application(app_name))
            self.win.display_action_confirmer(f"Install application {app_name}?")
            return

        search_command = f"winget search {app_name} --accept-source-agreements"
        search_result = subprocess.run(search_command, check=True, shell=True, text=True, capture_output=True).stdout

        pattern = fr'^{app_name}\s+([^\s]+)\s+Unknown\s+msstore$'

        match = re.search(pattern, search_result, re.MULTILINE | re.IGNORECASE)

        app_id = match.group(1)

        install_command = f"winget install --id={app_id} --accept-package-agreements --accept-source-agreements"
        try:
            subprocess.run(install_command, check=True, shell=True)
            print(f"The app '{app_name}' has been successfully installed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install the app '{app_name}': {e}")

    def uninstall_application(self, app_name):

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.uninstall_application(app_name))
            self.win.display_action_confirmer(f"Uninstall application {app_name}?")
            return

        list_command = "winget list --accept-source-agreements"
        try:
            list_result = subprocess.run(list_command, check=True, shell=True, text=True, capture_output=True).stdout
        except subprocess.CalledProcessError as e:
            print(f"Error listing installed apps: {e}")
            return

        print(list_result)

        pattern = fr'{app_name}\s+([^\s]+)\s+'
        match = re.search(pattern, list_result, re.IGNORECASE)

        if not match:
            print(f"{app_name} does not appear to be installed.")
            return

        app_id = match.group(1)

        # Step 3: Uninstall the app
        uninstall_command = f"winget uninstall --id={app_id} --accept-source-agreements"
        try:
            subprocess.run(uninstall_command, check=True, shell=True)
            print(f"The app {app_name} has been successfully uninstalled.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to uninstall {app_name}: {e}")

    def open_website(self, website_url):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.open_website(website_url))
            self.win.display_action_confirmer(f"Open website {website_url}?")
            return

        try:
            webbrowser.open(website_url, new=2)
            print(f"Website opened successfully: {website_url}")
        except Exception as e:
            print(f"Failed to open the website: {e}")

    def kill_application_process(self, app_name):
        # Get the list of all running process names
        process_names = {proc.pid: proc.name() for proc in psutil.process_iter(['name'])}

        # Find the best match for the app_name in the list of process names
        best_match = process.extractOne(app_name, process_names.values())

        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            if best_match:
                self.win.bind_action_to_execute(lambda: self.kill_application_process(app_name))
                self.win.display_action_confirmer(f"End the application {best_match}?")
            return

        if best_match:
            # Find the PID(s) for the best match name (there might be multiple instances)
            matched_pids = [pid for pid, name in process_names.items() if name == best_match[0]]
            print(f"Best match: {best_match[0]} (PID: {', '.join(map(str, matched_pids))})")

            for pid in matched_pids:
                try:
                    p = psutil.Process(pid)
                    p.terminate()  # or p.kill() if terminate is not effective
                    print(f"Process {pid} ({p.name()}) terminated.")
                except psutil.NoSuchProcess:
                    print(f"No process with PID {pid}.")
        else:
            print("No matching process found.")

    def change_timezone(self, new_timezone: str):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.change_timezone(new_timezone))
            self.win.display_action_confirmer(f"Change timezone to {new_timezone}?")
            return

        try:
            # Execute the tzutil command to set the new timezone
            result = subprocess.run(['tzutil', '/s', new_timezone], capture_output=True, text=True, check=True)
            output = result.stdout if result.stdout else result.stderr
        except subprocess.CalledProcessError as e:
            output = f"Failed to change timezone. Error: {e.output}"
        except Exception as e:
            output = f"An unexpected error occurred: {e}"
        return output

    def change_time_format(self, use_24_hour: bool):
        if not self.win.has_confirmed_action and self.settings_manager.get_confirm_actions():
            self.win.bind_action_to_execute(lambda: self.change_time_format(use_24_hour))
            self.win.display_action_confirmer(f"Change time format to {'24-hour' if use_24_hour else '12-hour'}?")
            return

        # PowerShell command to set the time format
        if use_24_hour:
            # 24-hour format
            ps_command = """
            Set-ItemProperty -Path "HKCU:\\Control Panel\\International" -Name sShortTime -Value "HH:mm";
            Set-ItemProperty -Path "HKCU:\\Control Panel\\International" -Name sLongTime -Value "HH:mm:ss";
            """
        else:
            # 12-hour format
            ps_command = """
            Set-ItemProperty -Path "HKCU:\\Control Panel\\International" -Name sShortTime -Value "hh:mm tt";
            Set-ItemProperty -Path "HKCU:\\Control Panel\\International" -Name sLongTime -Value "hh:mm:ss tt";
            """

        try:
            # Execute the PowerShell command
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            print("Time format changed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to change time format. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def find_email_by_name(recipient_name):
    # Connect to Outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    # Access the Contacts folder
    contacts_folder = outlook.GetDefaultFolder(10)  # 10 corresponds to the Contacts folder
    contacts = contacts_folder.Items

    # Build a list of (full name, email address) tuples
    contacts_list = [(contact.FullName, contact.Email1Address) for contact in contacts]

    # Use fuzzywuzzy to find the closest match
    closest_match_name, _ = process.extractOne(recipient_name, [contact[0] for contact in contacts_list])

    # Find the email of the closest match
    closest_match_email = next((email for name, email in contacts_list if name == closest_match_name), None)

    print(f"Closest match for '{recipient_name}': {closest_match_name} ({closest_match_email})")

    return closest_match_email


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
