import openai
import os
import json

from src.llm.llama_api_tool_structure_definitions import getToolJson
from src.tools.windows.windows_api import AutomationFunctions
from llamaapi import LlamaAPI


class OpenAIConversation:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.client = llama = LlamaAPI('LL-1lTJnxlAo6mDFpF5SX5nkb63jm0hci9HkleDyeyPFf1TN4HZiZxGKROhkUJMc28H')

    def create_completion(self, prompt):
        model = "gpt-3.5-turbo-1106"

        api_request_json = getToolJson(prompt, model)

        response = self.client.run(api_request_json)

        response_message = response.json()['choices'][0]['message']
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
