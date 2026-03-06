from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")



client = OpenAI(api_key= API_KEY)

class AIBrain:
    def __init__(self, role: str):
        self.role = role

    async def think(self, context: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a {self.role} in a multi-agent task system."},
                {"role": "user", "content": context}
            ]
        )
        return response.choices[0].message.content