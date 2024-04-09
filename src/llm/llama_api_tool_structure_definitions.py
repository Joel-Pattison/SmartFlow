def getToolJson(prompt, model):
    api_request_json = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Open chrome and firefox side by side"},
            # {"role": "user", "content": "Turn off my computer"},
        ],
        "functions": [
            {
                "name": "open_app",
                "description": "Open the specified app, or multiple specified apps",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_names": {
                            "type": "array",
                            "description": "The name of the app to run e.g. firefox. Can run multiple apps at the same time",
                            "items": {"type": "string"}
                        },
                        "locations": {
                            "type": "array",
                            "description": "The locations to move each of the apps once they're open. Stored in an array of enum values",
                            "enum": ["left", "right", "top left", "bottom left", "top right", "bottom right"],
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["app_names"]
                }
            },
            {
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
            },
            {
                "name": "invalid_command",
                "description": "Run this function if you cannot assist the user with the given input for any reason. this "
                               "will be logged and used to improve the model. it is critical that this function should "
                               "always be used if no other function can complete the request",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The input that was entered"
                        }
                    },
                    "required": ["input"]
                }
            }
        ],
    }

    return api_request_json
