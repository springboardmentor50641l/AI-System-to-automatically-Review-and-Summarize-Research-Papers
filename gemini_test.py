from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    timeout=30,
    temperature=0
)

response = llm.invoke([
    HumanMessage(content="Reply ONLY with valid JSON: {\"status\": \"ok\"}")
])

print(response.content)

