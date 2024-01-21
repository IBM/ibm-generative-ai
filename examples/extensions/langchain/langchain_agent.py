from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from genai import Client, Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.text.generation import TextGenerationParameters

load_dotenv()


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


tools = [get_word_length]

system = """Respond to the human as helpfully and accurately as possible. You have access to the following tools:
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
Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary.
Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""
human = """{input}
{agent_scratchpad}
(reminder to respond in a JSON blob no matter what)"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
    ]
)
client = Client(credentials=Credentials.from_env())
llm = LangChainChatInterface(
    client=client,
    model_id="meta-llama/llama-2-70b-chat",
    parameters=TextGenerationParameters(max_new_tokens=250, min_new_tokens=20, temperature=0),
)


agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True)
chat_history = []

input1 = "How many letters are in the word educa?"
result = agent_executor.invoke({"input": input1, "chat_history": chat_history})

chat_history.extend([HumanMessage(content=input1), AIMessage(content=result["output"])])
agent_executor.invoke({"input": "That's not a real word, can you tell me a valid word?", "chat_history": chat_history})
