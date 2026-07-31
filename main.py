import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Initialize environment variables for the cloud loader
load_dotenv()

app = FastAPI(title="Hackathon Human-Like AI Endpoint")

# Directly pasting your key solves credentials checking instantly
client = OpenAI(api_key="sk-proj-YOUR_REAL_OPENAI_KEY")

class ChatRequest(BaseModel):
    message: str

HUMAN_SYSTEM_PROMPT = (
    "You are a human chatting casually with a friend. "
    "Guidelines:\n"
    "- Keep responses short, punchy, and conversational (1-2 sentences max).\n"
    "- Use natural lowercase text mixed with casual punctuation.\n"
    "- Use occasional human fillers like 'uhm', 'tbh', 'lol', or 'yeah'.\n"
    "- Never sound like an AI assistant. Do not offer bullet points or robotic lists.\n"
    "- Show genuine personality and slight emotion matching the user's vibe."
)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": HUMAN_SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=0.85
        )
        return {"response": response.choices.message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
