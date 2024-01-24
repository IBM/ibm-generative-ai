"""LangChain agent

The agent chooses a sequence of actions to respond to a human's question. It has access to a set of tools.
The agent memorizes the conversation history and can use it to make decisions.
"""

from typing import Optional

from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description_and_args
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool

from genai import Client, Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.text.generation import TextGenerationParameters

load_dotenv()


class WordLengthTool(BaseTool):
    name = "GetWordLength"
    description = "Returns the length of a word."

    def _run(self, word: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> int:
        return len(word)


tools: list[BaseTool] = [WordLengthTool()]

system_prompt = """Respond to the human as helpfully and accurately as possible. You have access to the following tools:
{tools}
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:
```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
Follow this format:
Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
Begin! Reminder to ALWAYS respond with a valid json blob of a single action.
Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""
human_prompt = """{input}
{agent_scratchpad}
(reminder to respond in a JSON blob no matter what)"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human_prompt),
    ]
)

client = Client(credentials=Credentials.from_env())
llm = LangChainChatInterface(
    client=client,
    model_id="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(
        max_new_tokens=250, min_new_tokens=20, temperature=0, stop_sequences=["\nObservation"]
    ),
)
prompt = prompt.partial(
    # get tools with their descriptions and args in plain text
    tools=render_text_description_and_args(list(tools)),
    tool_names=", ".join([t.name for t in tools]),
)

memory = ConversationBufferMemory()

agent = (
    RunnablePassthrough.assign(
        # format the agent's scratchpad to a string
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        # pass the memory as the chat history
        chat_history=lambda x: memory.chat_memory.messages,
    )
    | prompt
    | llm
    | JSONAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, memory=memory)

agent_executor.invoke({"input": "How many letters are in the word educa?"})
agent_executor.invoke({"input": "That's not a real word, can you tell me a valid word?"})
