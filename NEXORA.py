from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import google.generativeai as genai
from openai import OpenAI
import os

# --- CONFIGURATION ---
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

# Environment se keys le raha hai (tu ne set kar rakhi hai)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- DATABASE MODEL ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- SCHEMAS ---
class AuthRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    messages: list
    model_choice: str = "gemini" 

# --- ROUTES ---
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

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    user_msg = req.messages[-1]['content']
    try:
        if req.model_choice == "gpt":
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_msg}]
            )
            reply = response.choices[0].message.content
        else:
            # 🔥 FIX: Model name change kar diya
            model = genai.GenerativeModel('gemini-1.5-pro')  # ← YAHAN CHANGE KIYA
            response = model.generate_content(user_msg)
            reply = response.text
            
        return {"choices": [{"message": {"role": "assistant", "content": reply}}]}
    except Exception as e:
        return {"choices": [{"message": {"role": "assistant", "content": f"Engine Alert: {str(e)}"}}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
