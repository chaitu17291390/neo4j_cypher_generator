from typing import Any, List, Tuple

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools.render import format_tool_to_openai_function
from llm import llm
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.chat_models import ChatOpenAI
from langchain.tools.render import render_text_description_and_args
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents import create_openai_functions_agent


from langchain.schema import AgentAction, AgentFinish

from cypher_tool import GraphCypherTool
import json

import re

# from _patch_parser import OpenAIFunctionsAgentOutputParser
# llm = ChatOpenAI(temperature=0, model="gpt-4", streaming=True)
tools = [GraphCypherTool()]

llm_with_tools = llm.bind(functions=[convert_to_openai_function(t) for t in tools])

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are a helpful assistant that  has access to a cypher generation tool, 
    please generate a cypher query for a given input question return the cypher query and output provided by the tool, 
    do not try to regenerate or optimize the cypher returned by the graphcyphertool"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")])


def _format_chat_history(chat_history: List[Tuple[str, str]]):
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


agent = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: _format_chat_history(x["chat_history"]) if x.get("chat_history") else [],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),

        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
)


class AgentInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        default=[], extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )


class Output(BaseModel):
    output: Any


agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
).with_types(
    input_type=AgentInput,
    output_type=Output
)


def run_agent(input_text: str):
    print("Running agent with input:", input_text)
    input_data = {"input": input_text, "chat_history": []}
    print("Input data prepared:", input_data)
    result = agent_executor.invoke(input_data)
    print("Agent result:", result)
    return result["output"]


# result = run_agent("list top 5 materials related to equipment 82135-09-0")
#result = agent_executor.invoke({"input":"Who are my top 3 on time suppliers?"})
#print("Final result:", result['output'])