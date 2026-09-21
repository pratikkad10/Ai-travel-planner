import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver


from tools import ALL_TOOLS
from prompts import system_prompt


load_dotenv()

checkpointer = InMemorySaver()

# model setup
llm = ChatMistralAI(
    model="ministral-3b-latest",
    temperature=0,
    max_retries=2,
)

agent = create_agent(
    model=llm,
    tools=ALL_TOOLS,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)
