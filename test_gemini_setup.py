import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

async def test_gemini():
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = await model.generate_content_async("Hello, are you working?")
        print(f"Gemini Response: {response.text}")
        print("Gemini setup verified successfully.")
    except Exception as e:
        print(f"Error verifying Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
