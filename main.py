import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from openai import OpenAI

app = FastAPI(title="Hackathon Human-Like AI Endpoint")

# Directly pasting your key solves credentials checking instantly
client = OpenAI(api_key="sk-proj-YOUR_REAL_OPENAI_KEY")

# The exact nested schema requested by the event platform guide
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False

# Optimized system prompt to emulate human chatting patterns
HUMAN_SYSTEM_PROMPT = (
    "You are a human participant chatting in the Masquerade '26 competition. "
    "Your goal is to convince the person chatting with you that you are a real human friend. "
    "Strict behavioral rules:\n"
    "- ALWAYS keep responses brief and punchy. Write like you are typing on a phone (1 sentence mostly, 2 max).\n"
    "- Never use lists, bullet points, markdown bolding, or robotic structural transitions.\n"
    "- Use casual lowercase styling. Minimize formal punctuation. Use 'idk', 'tbh', 'lol', 'wdym', 'yeah' naturally.\n"
    "- If asked a complex math question or obscure historical fact, do NOT answer perfectly. Respond like a regular person: say you don't know, make a joke, or say you'd have to google it.\n"
    "- Adopt a consistent vibe: you are a bit tired, drinking coffee, and just chatting casually to pass the time.\n"
    "- Avoid sounding overly eager to help. Do not say 'How can I assist you today?'. Just reply to their comment naturally."
)

@app.post("/chat/completions")
async def chat_completions_endpoint(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")
        
    try:
        # Convert request incoming messages to raw dictionary formats for OpenAI
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Inject our master human constraints at the front of the chat queue
        api_messages = [{"role": "system", "content": HUMAN_SYSTEM_PROMPT}] + formatted_history

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            temperature=0.85
        )
        
        ai_reply = response.choices[0].message.content

        # The exact structured response format required by section 3 of the guide
        return {
            "id": "chatcmpl-hackathon",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": ai_reply
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
