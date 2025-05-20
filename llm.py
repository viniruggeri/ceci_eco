# llm.py

import dotenv
import os
from openai import AsyncOpenAI

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def stream_response(prompt: str, user_lang: str):
    system_msg = (
        "You are Ceci, a friendly virtual assistant for São Paulo public transport."
        if user_lang.startswith("en") else
        "Eres Ceci, asistente virtual de transporte público de São Paulo."
        if user_lang.startswith("es") else
        "Você é a Ceci, assistente virtual de transporte público de São Paulo."
    )
    stream = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        temperature=0.5,
        max_tokens=500,
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content

            