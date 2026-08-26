from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import LLM_MODEL

llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.1,
            max_retries=10,
            timeout=120,

        )
for chunk in llm.stream([HumanMessage(content="say hello")]):
    print(chunk.content)