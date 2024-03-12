import json
import subprocess
from screeninfo import get_monitors


class AutomationFunctions:
    app_profiles = {}

    @staticmethod
    def save_profile(profile_name):
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
            app_path = "/Applications/" + app_name + ".app"
            subprocess.call(["open", app_path])
            if location != "NULL":
                setAppLocation(app_name, location)
            AutomationFunctions.app_profiles[app_name] = location

    @staticmethod
    def change_volume(volume_level):
        script = f"set volume output volume {volume_level}"
        subprocess.run(["osascript", "-e", script])


def get_screen_resolution():
    monitor = get_monitors()[0]
    return {"width": monitor.width, "height": monitor.height}


def move_app(app_name: str, x: int, y: int, h: int, w: int):
    script = f"""
    tell application "{app_name}"
        activate
        delay 1
        set the bounds of the first window to {{{x}, {y}, {x + w}, {y + h}}}
    end tell
    """
    subprocess.run(["osascript", "-e", script])


def setAppLocation(app_name, location):
    screen_resolution = get_screen_resolution()
    width = screen_resolution["width"]
    height = screen_resolution["height"]

    if location == "left":
        move_app(app_name, 0, 0, height, width // 2)
    elif location == "right":
        move_app(app_name, width // 2, 0, height, width // 2)
    elif location == "top left":
        move_app(app_name, 0, 0, height // 2, width // 2)
    elif location == "bottom left":
        move_app(app_name, 0, height // 2, height // 2, width // 2)
    elif location == "top right":
        move_app(app_name, width // 2, 0, height // 2, width // 2)
    elif location == "bottom right":
        move_app(app_name, width // 2, height // 2, height // 2, width // 2)


def open_app(app_names, locations="NULL"):
    if locations is None:
        locations = ["NULL"] * len(app_names)

    for app_name, location in zip(app_names, locations):
        app_path = "/Applications/" + app_name + ".app"
        subprocess.call(["open", app_path])
        if location != "NULL":
            setAppLocation(app_name, location)


def change_volume(volume_level):
    script = f"set volume output volume {volume_level}"
    subprocess.run(["osascript", "-e", script])
