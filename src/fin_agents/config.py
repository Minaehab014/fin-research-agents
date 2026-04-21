from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

GROQ_MODEL = "llama-3.3-70b-versatile"



def groq_llm(temperature: float = 0) -> ChatGroq:
    return ChatGroq(model=GROQ_MODEL, temperature=temperature)


