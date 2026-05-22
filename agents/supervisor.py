import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv


load_dotenv()



# LLM (Groq)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# Prompt
prompt = ChatPromptTemplate.from_template(
    """
    You are a research planner.

    Given a topic, create a clear step-by-step research plan.

    Topic: {topic}
    """
)

# Chain
supervisor_chain = prompt | llm | StrOutputParser()

# Function
def run_supervisor(topic: str):
    return supervisor_chain.invoke({"topic": topic})


# Test
if __name__ == "__main__":
    result = run_supervisor("AI in Healthcare")
    print(result)