from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate


load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

prompt = ChatPromptTemplate.from_template(
    """
    You are a fact checker.

    Review the draft report using the provided sources.
    Fix unclear or weak parts and return the improved final report only.

    Draft report:
    {draft_report}

    Sources:
    {sources}
    """
)

fact_checker_chain = prompt | llm | StrOutputParser()


def run_fact_checker(draft_report: str, sources: list):
    return fact_checker_chain.invoke(
        {
            "draft_report": draft_report,
            "sources": sources,
        }
    )
