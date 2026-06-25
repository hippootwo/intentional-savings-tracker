import os
from google import genai
from google.genai import types

def test_api_key():
    api_key = os.environ.get("GEMINI_API_KEY", "")  # never hardcode keys
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say hi"
        )
        print("SUCCESS:", response.text)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_api_key()
