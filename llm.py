from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, MODEL_NAME

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)
