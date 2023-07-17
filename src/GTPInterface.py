import openai
import json

from DesktopOps import AutomationFunctions

openai.api_key = "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"


def run_conversation(prompt, gptVersion):
    messages = [{"role": "user", "content": prompt}]
    functions = [
        {
            "name": "open_app",
            "description": "Open the specified app, or multiple specified apps",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_names": {
                        "type": "array",
                        "description": "The name of the app to run e.g. firefox. can be up to two different apps to run at the same time",
                        "items": {"type": "string"},
                    },
                    "locations": {
                        "type": "array",
                        "description": "The location to move each of the apps once they're open",
                        "enum": [
                            "left",
                            "right",
                            "top left",
                            "bottom left",
                            "top right",
                            "bottom right",
                        ],
                        "items": {"type": "string"},
                    },
                },
                "required": ["app_names"],
            },
        },
        {
            "name": "change_volume",
            "description": "Change the volume level",
            "parameters": {
                "type": "object",
                "properties": {
                    "volume_level": {
                        "type": "number",
                        "description": "The volume level to set, from 0 to 100",
                    },
                },
                "required": ["volume_level"],
            },
        },
        {
            "name": "save_profile",
            "description": "Save the current app profiles",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_name": {
                        "type": "string",
                        "description": "The name of the profile to save",
                    },
                },
                "required": ["profile_name"],
            },
        },
        {
            "name": "load_profile",
            "description": "Load a saved app profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_name": {
                        "type": "string",
                        "description": "The name of the profile to load",
                    },
                },
                "required": ["profile_name"],
            },
        },
    ]

    model = "gpt-4-0613" if gptVersion == "4" else "gpt-3.5-turbo-0613"

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call="auto",
    )

    response_message = response["choices"][0]["message"]
    print(response_message)

    if response_message.get("function_call"):
        available_functions = {
            "open_app": AutomationFunctions.open_app,
            "change_volume": AutomationFunctions.change_volume,
            "save_profile": AutomationFunctions.save_profile,
            "load_profile": AutomationFunctions.load_profile,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(**function_args)
