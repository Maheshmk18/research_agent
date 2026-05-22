from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate


load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

prompt = ChatPromptTemplate.from_template(
    """
    You are a research writer.

    Write a clear report using the topic, plan, and source data.

    Topic: {topic}

    Plan:
    {plan}

    Sources:
    {sources}
    """
)

writer_chain = prompt | llm | StrOutputParser()


def run_writer(topic: str, plan: str, sources: list):
    return writer_chain.invoke(
        {
            "topic": topic,
            "plan": plan,
            "sources": sources,
        }
    )
