import os
import openai
import json

from src.tools.windows.windows_api import AutomationFunctions


class LLMConversation:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.client = openai.OpenAI(api_key="NONE")

    def run_conversation(self, prompt):
        print("Running conversation...")
        if self.client.api_key != self.settings_manager.get_openai_api_key():
            self.client.api_key = self.settings_manager.get_openai_api_key()

        if not os.path.exists("profiles"):
            os.makedirs("profiles")

        path = "profiles"

        all_files = os.listdir(path)

        existing_profiles = [file[:-4] for file in all_files if file.endswith(".txt")]

        print(existing_profiles)

        messages = [
            {
                "role": "system",
                "content": f"This assistant is a task-execution tool designed for system automation. It is not a conversational agent. It can execute tasks such as opening applications, adjusting volume settings, saving and loading app profiles. The existing profiles that it can open are: {', '.join(existing_profiles)}.",
            },
            {"role": "user", "content": prompt},
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open the specified app, or multiple specified apps",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_names": {
                                "type": "array",
                                "description": "The name of the app to run e.g. firefox. can run multiple apps at the same time",
                                "items": {"type": "string"}
                            },
                            "locations": {
                                "type": "array",
                                "description": "The locations to move each of the apps once they're open to be stored in an array of enum values",
                                "enum": ["left", "right", "top left", "bottom left", "top right", "bottom right"],
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["app_names"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "change_volume",
                    "description": "Change the volume level",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "volume_level": {
                                "type": "number",
                                "description": "The volume level to set, from 0 to 100"
                            }
                        },
                        "required": ["volume_level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_profile",
                    "description": "Save the current app profiles",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "The name of the profile to save"
                            }
                        },
                        "required": ["profile_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "load_profile",
                    "description": "Load a saved app profile. the profile must exist and the input profile name has to match the name of the existing profile exactly",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "The name of the profile to load"
                            }
                        },
                        "required": ["profile_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "invalid_command",
                    "description": "If for any way the input is entered in a unexpected way, run this function"
                }
            },
        ]

        model = "gpt-3.5-turbo-1106"

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        print(response_message)

        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "open_app": AutomationFunctions.open_app,
                "change_volume": AutomationFunctions.change_volume,
                "save_profile": AutomationFunctions.save_profile,
                "load_profile": AutomationFunctions.load_profile,
            }
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
