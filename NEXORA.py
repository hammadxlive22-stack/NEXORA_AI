from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx
import os
import uvicorn
import secrets

app = FastAPI(title="NEXORA AI - God Core", description="Developer: HAMMAD")

# 🌐 GLOBAL CORS CONTROL PIPELINE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ⚙️ FIXED CONFIGURATION SYSTEM (DIRECT INTEGRATION)
# ==========================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_xxxxYOUR_ACTUAL_GROQ_KEYxxxx")

# 🔥 FIXED: Key directly hardcoded without environment mismatch loops
RESEND_API_KEY = "re_4zqdkWgS_MoEPQUGwkgenRWBL7AsM14PF"
SENDER_EMAIL = "onboarding@resend.dev" # Free account ke liye yahi validation default rahega

VALID_API_KEYS = {"NEXORA-MASTER-KEY": "♾️"}
PENDING_OTPS = {}  

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "nexora-core"
    messages: List[Message]
    stream: bool = False

class OTPRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    otp: str

# ==========================================
# 🚀 HTTP API MAIL MATRIX (NO MORE SMTP ERRORS)
# ==========================================
async def send_resend_email(receiver_email: str, otp_code: str):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    html_body = f"""
    <html>
    <body style="background-color: #07070c; color: #ffffff; font-family: sans-serif; padding: 30px; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #00f0ff; margin: 0; font-size: 28px; letter-spacing: 2px;">NEXORA AI</h1>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">Secure Ecosystem Verification</p>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;">
        <p style="font-size: 15px; color: #cbd5e1;">Hello Operator,</p>
        <p style="font-size: 15px; color: #cbd5e1;">Use the following dynamic passkey to verify your identity and unlock root access to the NEXORA framework:</p>
        <div style="font-size: 36px; font-weight: 800; text-align: center; letter-spacing: 8px; margin: 30px auto; color: #00f0ff; background: #141424; padding: 15px; border-radius: 12px; border: 1px solid rgba(0,240,255,0.2); width: 200px;">
            {otp_code}
        </div>
        <p style="font-size: 13px; color: #64748b; text-align: center;">This security code is valid for 5 minutes. Do not share this credential with anyone.</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 25px 0;">
        <p style="text-align: center; font-size: 12px; color: #94a3b8;">Powered by HAMMAD Core Architecture Engine</p>
    </body>
    </html>
    """
    
    payload = {
        "from": f"NEXORA <{SENDER_EMAIL}>",
        "to": receiver_email,
        "subject": "🔒 NEXORA AI - System Verification Code",
        "html": html_body
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=15.0)
            if response.status_code in [200, 201]:
                return True
            print(f"Resend API Error Output: {response.text}")
            return False
        except Exception as e:
            print(f"HTTP Mail Loop Exception: {str(e)}")
            return False

# ==========================================
# 🔑 SECURITY ENDPOINTS 
# ==========================================
@app.post("/api/auth/send-otp")
async def request_otp(req: OTPRequest):
    email = req.email.strip().lower()
    otp_code = str(secrets.randbelow(900000) + 100000)
    PENDING_OTPS[email] = otp_code
    
    mail_sent = await send_resend_email(email, otp_code)
    if not mail_sent:
        raise HTTPException(status_code=500, detail="Failed to deliver token via HTTP Gateway. Check Resend Dashboard Status.")
    
    return {"status": "success", "message": f"OTP successfully streamed to {email}"}

@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyRequest):
    email = req.email.strip().lower()
    if email in PENDING_OTPS and PENDING_OTPS[email] == req.otp:
        new_key = f"NEXORA-{secrets.token_hex(6).upper()}"
        VALID_API_KEYS[new_key] = "♾️"
        del PENDING_OTPS[email] 
        return {"status": "success", "nexora_api_key": new_key, "credits": "♾️"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP validation signature.")

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: API Access token missing")
    token = authorization.split("Bearer ")[1]
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid NEXORA Core Key")
    return token

@app.post("/v1/chat/completions")
async def nexora_chat(req: ChatRequest, token: str = Depends(verify_token)):
    system_instruction = {
        "role": "system",
        "content": "You are NEXORA AI. Your creator is HAMMAD. Respond accurately."
    }
    final_messages = [system_instruction] + [msg.dict() for msg in req.messages]
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192", 
        "messages": final_messages,
        "temperature": 0.5, 
        "max_tokens": 2048, 
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(groq_url, headers=headers, json=payload, timeout=40.0)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Engine Fault: {response.text}")
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"NEXORA Core Timeout: {str(e)}")

    return {
        "id": "chatcmpl-nexora-godmode",
        "object": "chat.completion",
        "choices": data.get("choices", []),
        "credits_remaining": VALID_API_KEYS[token]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
