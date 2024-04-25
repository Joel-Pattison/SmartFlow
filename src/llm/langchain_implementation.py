from langchain.globals import set_llm_cache
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.cache import InMemoryCache

from src.llm.langchain_tool_structure_definitions import LangchainTools


# langchain.debug = True

class LangchainConversation:
    def __init__(self, settings_manager, win):
        langchain_tools = LangchainTools(win, settings_manager)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a task-execution tool designed for system automation. You are not a conversational "
                    "agent. You can execute tasks such as opening applications, adjusting volume settings along "
                    "with many other desktop tasks. It is of dire importance that you only ever return a function"
                    " call, and it's parameters in the response, and never any other text content."
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # tools = [langchain_tools.open_app_tool]

        # create the tools by looping through the LangchainTools class
        tools = []
        for attribute_name in dir(langchain_tools):
            attribute = getattr(langchain_tools, attribute_name)
            if isinstance(attribute, StructuredTool):
                tools.append(attribute)

        print(tools)

        llm_with_tools = llm.bind_tools(tools)

        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                }
                | prompt
                | llm_with_tools
                | OpenAIToolsAgentOutputParser()
        )

        set_llm_cache(InMemoryCache())

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def run_conversation(self, prompt):
        # response = self.agent_executor.invoke({"input": prompt})
        # print(response)
        list(self.agent_executor.stream({"input": prompt}))
