from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Fetching available models...")
try:
    # We will just print the name to avoid attribute errors
    for model in client.models.list():
        print(f"Model Name: {model.name}")
        
except Exception as e:
    print(f"Error: {e}")