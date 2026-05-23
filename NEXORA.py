from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import aiohttp
import asyncio
import os

# ============================================================
# CONFIGURATION
# ============================================================
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_size=10, 
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# SCHEMAS
# ============================================================
class AuthRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    messages: list
    model_choice: str = "gpt"

# ============================================================
# AUTH ROUTES (Same as before)
# ============================================================
@app.post("/auth/register")
def register(req: AuthRequest):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == req.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = pwd_context.hash(req.password)
        db.add(User(email=req.email, password=hashed))
        db.commit()
        return {"status": "Success", "message": "Registered"}
    finally:
        db.close()

@app.post("/auth/login")
def login(req: AuthRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not pwd_context.verify(req.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"status": "Success", "message": "User authenticated"}
    finally:
        db.close()

# ============================================================
# 🔥 MULTI-API FALLBACK SYSTEM (FREE APIS)
# ============================================================
async def call_pollinations_api(prompt: str) -> str:
    """Free API #1 - Pollinations (no key needed)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://text.pollinations.ai/{prompt}", timeout=30) as resp:
                if resp.status == 200:
                    return await resp.text()
    except:
        pass
    return None

async def call_hercai_api(prompt: str) -> str:
    """Free API #2 - Hercai (no key needed)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://hercai.onrender.com/hercai?question={prompt}", timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and data.get("reply"):
                        return data["reply"]
    except:
        pass
    return None

async def call_openai_api(prompt: str, api_key: str) -> str:
    """OpenAI API (needs key)"""
    if not api_key or api_key == "YOUR_OPENAI_KEY":
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    user_msg = req.messages[-1]['content']
    openai_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
    
    # Try APIs in sequence
    reply = None
    
    # 1. Try OpenAI first (if key available)
    if openai_key and openai_key != "YOUR_OPENAI_KEY":
        reply = await call_openai_api(user_msg, openai_key)
    
    # 2. Try Pollinations (free)
    if not reply:
        reply = await call_pollinations_api(user_msg)
    
    # 3. Try Hercai (free backup)
    if not reply:
        reply = await call_hercai_api(user_msg)
    
    # 4. Final fallback
    if not reply:
        reply = "I'm having trouble connecting right now. Please try again in a moment. 🙏"
    
    return {"choices": [{"message": {"role": "assistant", "content": reply}}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
