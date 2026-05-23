from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from openai import OpenAI
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

# 🔥 SIRF OPENAI - GEMINI HATAYA
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY"))

# ============================================================
# DATABASE MODEL
# ============================================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROOT ENDPOINT
# ============================================================
@app.get("/")
def root():
    return {
        "status": "active",
        "message": "NEXORA AI API is running (GPT Only)",
        "endpoints": ["/auth/register", "/auth/login", "/v1/chat/completions"]
    }

# ============================================================
# SCHEMAS
# ============================================================
class AuthRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    messages: list
    model_choice: str = "gpt"  # 🔥 Default GPT

# ============================================================
# AUTH ROUTES
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
# 🔥 CHAT ROUTE - SIRF GPT (GEMINI HATAYA)
# ============================================================
@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    user_msg = req.messages[-1]['content']
    try:
        # 🔥 Sirf GPT - Gemini ka code hata diya
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=500,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return {"choices": [{"message": {"role": "assistant", "content": reply}}]}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"choices": [{"message": {"role": "assistant", "content": f"Engine Alert: {str(e)}"}}]}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
