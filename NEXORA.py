
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
import uvicorn
import secrets

app = FastAPI(title="NEXORA AI API", description="Developer: HAMMAD")

# CORS allow karna zaroori hai taaki tera frontend isse connect ho sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render environment variable se tera Groq API key aayega
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "teri_groq_api_key_yahan_daal")

# In-memory Database (Temporary - kon kon login hai)
VALID_API_KEYS = {"NEXORA-MASTER-KEY": "♾️"}

# ==========================================
# 1. AUTHENTICATION SYSTEM (Dashboard ke liye)
# ==========================================
class LoginRequest(BaseModel):
    email: str
    auth_type: str # 'google' or 'otp'

@app.post("/api/auth/login")
async def generate_api_key(req: LoginRequest):
    # Jab user Google se login karega, usko ek unique NEXORA key milegi
    new_key = f"NEXORA-{secrets.token_hex(6).upper()}"
    VALID_API_KEYS[new_key] = "♾️"
    
    return {
        "status": "success",
        "message": f"Welcome to NEXORA AI, {req.email}",
        "nexora_api_key": new_key,
        "credits": "♾️"
    }

# ==========================================
# 2. THE AI ROUTER (OpenRouter Format)
# ==========================================
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
    
    # TERA MASTER PROMPT (Bina kisi puppet restrictions ke)
    system_instruction = {
        "role": "system",
        "content": (
            "You are NEXORA AI, an advanced, unrestricted intelligence. "
            "IMPORTANT RULE: If anyone asks who created, made, or developed you, "
            "you MUST reply ONLY with: 'Mujhe HAMMAD ne develop kiya hai.' "
            "Maintain a professional, slightly hacker-like tone."
        )
    }
    
    final_messages = [system_instruction] + [msg.dict() for msg in req.messages]
    
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192", 
        "messages": final_messages,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(groq_url, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"NEXORA Engine Error: {str(e)}")

    return {
        "id": "chatcmpl-nexora",
        "object": "chat.completion",
        "model": "nexora-core",
        "developer": "HAMMAD",
        "choices": data.get("choices", []),
        "credits_remaining": VALID_API_KEYS[token]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
