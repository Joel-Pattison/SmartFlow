import os

from src.llm.langchain_implementation import LangchainConversation

os.environ["OPENAI_API_KEY"] = "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"


class LLMConversation:
    def __init__(self, settings_manager, win):
        self.settings_manager = settings_manager
        self.client = LangchainConversation(settings_manager, win)
        win.set_llm_conversation(self)

    def run_conversation(self, prompt):
        if os.environ["OPENAI_API_KEY"] != self.settings_manager.get_openai_api_key():
            os.environ["OPENAI_API_KEY"] = self.settings_manager.get_openai_api_key()

        response = self.client.run_conversation(prompt)

        print("Running conversation...")
