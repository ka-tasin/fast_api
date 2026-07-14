from google import genai
from dotenv import load_dotenv
load_dotenv()
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
 
# def ask_llm(message: str) -> str:
#     response = client.models.generate_content(
#         model="gemini-3.5-flash",
#         contents=message
#     )

#     return response.text

SYSTEM_PROMPT = "You are a concise job-matching assistant. Only answer questions about jobs, resumes, or careers. Politely refuse anything else."

# Ask LLM with system prompt
def ask_llm(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=message,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    return response.text



def ask_llm_stream(message: str):
    response = client.models.generate_content_stream(
        model = "gemini-3.5-flash",
        contents=message
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text
