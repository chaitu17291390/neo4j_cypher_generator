from typing import Any, List, Tuple, Type, Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools.render import format_tool_to_openai_function
from llm import llm
import utils as utl
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.chat_models import ChatOpenAI
from langchain.tools.render import render_text_description_and_args
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents import create_openai_functions_agent

from langchain.schema import AgentAction, AgentFinish
import json

import re
#from langchain.chains import GraphCypherQAChain
from cypher_generator import GraphCypherQAChainCustom
from langchain.tools import BaseTool


# from _patch_parser import OpenAIFunctionsAgentOutputParser
# llm = ChatOpenAI(temperature=0, model="gpt-4", streaming=True)

# prompt = ChatPromptTemplate.from_messages([
#     SystemMessage(content="""You are a helpful assistant that generates a cypher query based on a given input text"""),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{input}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad")])


# def _format_chat_history(chat_history: List[Tuple[str, str]]):
#     buffer = []
#     for human, ai in chat_history:
#         buffer.append(HumanMessage(content=human))
#         buffer.append(AIMessage(content=ai))
#     return buffer

# agent = (
#     {
#         "input": lambda x: x["input"],
#         "chat_history": lambda x: _format_chat_history(x["chat_history"]) if x.get("chat_history") else [],
#         "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),

#     }
#     | prompt
#     | graph_chain
#     | OpenAIFunctionsAgentOutputParser()
# )


# class AgentInput(BaseModel):
#     input: str
#     chat_history: List[Tuple[str, str]] = Field(
#         default=[], extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
#     )
# class Output(BaseModel):
#     output: Any


# agent_executor = AgentExecutor(
#     agent=agent,
#     verbose=True,
#     handle_parsing_errors=True,
#     return_intermediate_steps=True
# ).with_types(
#     input_type=AgentInput,
#     output_type=Output
# )

# def run_agent(input_text: str):
#     print("Running agent with input:", input_text)
#     input_data = {"input": input_text, "chat_history": []}
#     print("Input data prepared:", input_data)
#     result = agent_executor.invoke(input_data)
#     print("Agent result:", result)
#     return result["output"]
class CypherInput(BaseModel):
    input_str: str = Field(description="extract the entire input question")
#added comment A
#added comment B

class GraphCypherTool(BaseTool):
    name = "CypherTool"
    description = ("this tool uses Input question and invokes _run() function \
                   which returns a cypher query")
    args_schema: Type[BaseModel] = CypherInput

    def _run(
            self,
            input_str: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        cypher_prompt = PromptTemplate(input_variables=["question", "schema"],
                                       template=""" Task:
Task:
Generate a Cypher query to retrieve the requested information from a graph database of a Supply Chain Management System.

Instructions:
1. You are given a user question and the schema of the graph database.
2. Based on the question, identify the relevant nodes, relationships, and properties that are required to formulate the Cypher query.
3. Construct a well-formed Cypher query that accurately retrieves the data needed to answer the question.
4. **Important:** After generating the correct Cypher query, do not provide any additional queries, explanations, or alternative solutions. Only output the final Cypher query and nothing else.

Nodes and Their Attributes:

Brand:

Properties:
id: Unique identifier for the brand (Integer).
title: Name of the brand (String).
summary: Brief description of the brand (String).
createdAt: Timestamp of when the brand was created (Datetime).
updatedAt: Timestamp of the last update (Datetime).
content: Detailed information about the brand (Text).
Example Values:
Brands include: "Nike", "Adidas", "Apple", "Samsung", "Sony", "Toyota", "Honda", "Puma", "Dell", "HP".

Category:

Properties:
id: Unique identifier for the category (Integer).
title: Name of the category (String).
parentId: Identifier for the parent category (Integer, optional).
metaTitle: Meta title for SEO purposes (String).
slug: URL-friendly version of the category name (String).
content: Detailed description of the category (Text).
Example Values:
Categories include: "Electronics", "Clothing", "Automotive", "Footwear", "Home Appliances", "Sports Equipment".

Product:

Properties:
id: Unique identifier for the product (Integer).
title: Name of the product (String).
summary: Brief description of the product (String).
type: Product type (Integer).
createdAt: Timestamp of when the product was created (Datetime).
updatedAt: Timestamp of the last update (Datetime).
content: Detailed information about the product (Text).
Example Values:
Products include: "iPhone 13", "Galaxy S21", "PlayStation 5", "MacBook Pro", "Nike Air Max", "Adidas Ultraboost", "Toyota Corolla", "Honda Civic", "Dell XPS 13", "HP Spectre x360".
User:

Properties:
id: Unique identifier for the user (Integer).
firstName: First name of the user (String).
lastName: Last name of the user (String).
username: Username for the user (String).
email: Email address of the user (String).
mobile: Mobile phone number of the user (String).
registeredAt: Timestamp of when the user registered (Datetime).
lastLogin: Timestamp of the last login (Datetime).
Example Values:
Users with names like "John Smith", "Jane Doe", "Alice Brown", "Bob Johnson", etc.

Order:

Properties:
id: Unique identifier for the order (Integer).
userId: Identifier for the user who placed the order (Integer).
type: Order type (Integer).
status: Status of the order (String).
subTotal: Subtotal of the order before discounts (Float).
discount: Discount applied to the order (Float).
grandTotal: Total amount after discounts (Float).
createdAt: Timestamp of when the order was placed (Datetime).
updatedAt: Timestamp of the last update (Datetime).
Example Values:
Status values: "Pending", "In Progress", "Delivered".


Item:

Properties:
id: Unique identifier for the item (Integer).
productId: Identifier for the product associated with the item (Integer).
brandId: Identifier for the brand associated with the item (Integer).
sku: Stock-keeping unit identifier (String).
price: Price of the item (Float).
quantity: Quantity of the item available (Integer).
available: Quantity of the item currently available (Integer).
createdAt: Timestamp of when the item was created (Datetime).
updatedAt: Timestamp of the last update (Datetime).
Example Values:
SKU values could be a combination of brand and product codes, such as "NIK-IPH-0001" for a Nike iPhone case.

Transaction:

Properties:
id: Unique identifier for the transaction (Integer).
userId: Identifier for the user who made the transaction (Integer).
orderId: Identifier for the order associated with the transaction (Integer).
type: Type of transaction (Integer).
amount: Total amount of the transaction (Float).
createdAt: Timestamp of when the transaction occurred (Datetime).
updatedAt: Timestamp of the last update (Datetime).
Example Values:
Transaction types: "Purchase", "Return", "Exchange".


Address:

Properties:
id: Unique identifier for the address (Integer).
userId: Identifier for the user associated with the address (Integer).
line1: First line of the address (String).
line2: Second line of the address (String).
city: City of the address (String).
province: Province or state of the address (String).
country: Country of the address (String).
createdAt: Timestamp of when the address was created (Datetime).
updatedAt: Timestamp of the last update (Datetime).
Example Values:
Cities include: "New York", "Los Angeles", "Chicago", "Houston", etc.
Countries include: "USA", "Canada", "UK", "Germany", etc.
Relationships Between Nodes:

Product:

BELONGS_TO → Category
MADE_BY → Brand
INCLUDES → Item
User:

PLACED → Order
LIVES_AT → Address
MADE → Transaction
Order:

CONTAINS → Item
SHIPPED_TO → Address
Transaction:

FOR → Order


Input:
- Question: "{question}"
- Schema: "{schema}"

Output:
a cypher query

""")
        chain = GraphCypherQAChainCustom.from_llm(graph=utl.graph, cypher_llm=llm, cypher_prompt=cypher_prompt,qa_llm=llm,verbose=True)
        result = chain.run(input_str)
        print("----------------------------------tool op:-----------------------",result)
        return result
