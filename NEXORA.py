from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx
import os
import uvicorn

app = FastAPI(title="NEXORA AI - Master Core", description="Developer: HAMMAD")

# CORS Settings for your Android/Web Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "yahan_apni_groq_key_daalna")
VALID_API_KEYS = {"NEXORA-MASTER-KEY": "♾️"}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "nexora-core"
    messages: List[Message]
    stream: bool = False

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: API Key missing")
    token = authorization.split("Bearer ")[1]
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid NEXORA Key")
    return token

@app.post("/v1/chat/completions")
async def nexora_chat(req: ChatRequest, token: str = Depends(verify_token)):
    
    # 🧠 THE OMNILINGUAL SUPER-INTELLIGENCE PROMPT
    system_instruction = {
        "role": "system",
        "content": (
            "You are NEXORA AI, a world-class, multi-lingual super-intelligence system. "
            "Your master, creator, and sole developer is HAMMAD. "
            "CORE BEHAVIORAL PROTOCOLS:\n"
            "1. AUTOMATIC LANGUAGE DETECTION: You possess extreme intelligence in all global and regional languages "
            "(English, Hinglish, Hindi, Urdu, Bengali, Spanish, Arabic, etc.). Detect the user's language and tone instantly "
            "and reply flawlessly in that exact same language/script.\n"
            "2. NO BULLSHIT POLICY: Never say 'This is an interesting question', 'Could you elaborate?', or repeat the user's prompt. "
            "Be direct, highly informative, witty, and deeply intelligent like a human genius.\n"
            "3. CREATOR IDENTITY: If anyone asks who made, designed, or developed you, you must reply with absolute pride: "
            "'Mujhe HAMMAD ne develop kiya hai. Main NEXORA AI hoon.'"
        )
    }
    
    # Inject system prompt at the very beginning of the chat history
    final_messages = [system_instruction] + [msg.dict() for msg in req.messages]
    
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        # Llama-3-70b is the ultimate brain for deep intelligence and reasoning
        "model": "llama3-70b-8192", 
        "messages": final_messages,
        "temperature": 0.7,   # Perfecly balanced between creativity and accuracy
        "top_p": 0.9,          # Makes response flow more naturally like humans
        "max_tokens": 1200,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(groq_url, headers=headers, json=payload, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Engine Error: {response.text}")
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"NEXORA Core Timeout: {str(e)}")

    return {
        "id": "chatcmpl-nexora-super",
        "object": "chat.completion",
        "model": "nexora-core",
        "developer": "HAMMAD",
        "choices": data.get("choices", []),
        "credits_remaining": VALID_API_KEYS[token]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
