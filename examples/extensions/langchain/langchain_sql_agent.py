"""LangChain SQL Agent

In this example, we first create an SQL database with a ‘countries’ table, and subsequently, we will use LangChain
Agent to make queries against it.
"""

import contextlib
from tempfile import TemporaryFile

from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description_and_args
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool

from genai import Client, Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.schema import TextGenerationParameters

load_dotenv()

try:
    import pandas as pd
    import sqlalchemy
    from langchain.sql_database import SQLDatabase
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
except ImportError:
    print("Please install 'pandas' / 'sqlalchemy' to run this example.")
    raise


@contextlib.contextmanager
def get_countries_db():
    with TemporaryFile(suffix=".db") as f:
        df = pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
            }
        )

        engine = sqlalchemy.create_engine(f"sqlite:///{f.name}")
        df.to_sql("countries", con=engine, index=False, if_exists="replace")
        yield SQLDatabase.from_uri(f"sqlite:///{f.name}")
        engine.dispose(close=True)


def create_llm():
    client = Client(credentials=Credentials.from_env())
    return LangChainChatInterface(
        client=client,
        model_id="meta-llama/llama-3-1-70b-instruct",
        parameters=TextGenerationParameters(
            max_new_tokens=250, min_new_tokens=20, temperature=0, stop_sequences=["\nObservation"]
        ),
    )


def create_agent(tools: list[BaseTool], llm: LangChainChatInterface):
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
    Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""  # noqa

    human_prompt = """{input}
    {agent_scratchpad}
    (reminder to respond in a JSON blob no matter what)"""

    memory = ConversationBufferMemory()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human_prompt),
        ]
    ).partial(
        tools=render_text_description_and_args(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )

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

    return AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, memory=memory)


with get_countries_db() as db:
    llm = create_llm()

    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = sql_toolkit.get_tools()

    agent_executor = create_agent(tools, llm)
    agent_executor.invoke({"input": "How many rows are in the countries table?"})
    agent_executor.invoke({"input": "Which are the countries with GDP greater than 3000000000000?"})
