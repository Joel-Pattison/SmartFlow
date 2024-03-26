from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from typing import List, Optional
from src.tools.windows.windows_api import AutomationFunctions, OpenAppEnum, WindowsSettingsInteractionEnum


class OpenAppInput(BaseModel):
    app_names: List[str] = Field(description="List of names of the app(s) to open.")
    locations: Optional[List[OpenAppEnum]] = Field(description="List of locations to move each app to once opened. "
                                                               "The index of each location should match the index of "
                                                               "the app name.")


class ChangeVolumeInput(BaseModel):
    volume_level: int = Field(description="The desired volume level as a percentage. E.g. 50 for 50% volume.")


class WindowsSettingsInteractionInput(BaseModel):
    interaction: WindowsSettingsInteractionEnum = Field(
        description="The interaction to perform with the Windows settings. ")


class WriteEmailInput(BaseModel):
    recipient_name: str = Field(description="The name of the recipient of the email.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")


class LangchainTools:
    def __init__(self, win, settings_manager):
        automation_functions = AutomationFunctions(win, settings_manager)

        self.open_app_tool = StructuredTool.from_function(
            func=automation_functions.open_app,
            name="OpenApp",
            description="Open the specified app, or multiple specified apps. You should always try to provide "
                        "multiple apps to open at the same time as to minimize token usage.",
            args_schema=OpenAppInput
        )

        self.change_volume_tool = StructuredTool.from_function(
            func=automation_functions.change_volume,
            name="ChangeVolume",
            description="Change the system volume to the specified level.",
            args_schema=ChangeVolumeInput
        )

        self.windows_settings_interaction_tool = StructuredTool.from_function(
            func=automation_functions.windows_settings_interaction,
            name="WindowsSettingsInteraction",
            description="Interact with various Windows settings, such as shutdown, restart, sleep, "
                        "dark mode, light mode, night light, Bluetooth, and Wi-Fi.",
            args_schema=WindowsSettingsInteractionInput
        )

        self.write_email_tool = StructuredTool.from_function(
            func=automation_functions.write_email,
            name="WriteEmail",
            description="Open the default email provider to create a new email.",
            args_schema=WriteEmailInput
        )
