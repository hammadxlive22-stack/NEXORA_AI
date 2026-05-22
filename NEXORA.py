from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import uvicorn
import secrets
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="NEXORA AI - Global User Core", description="Developer: HAMMAD")

# ==========================================
# 🌐 GLOBAL CORS CONTROL PIPELINE
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ⚙️ GMAIL CONFIGURATION (FOR REAL USERS)
# ==========================================
# ⚠️ YAHAN APNI DETAILS BILKUL SAHI DAALNA
SENDER_EMAIL = "hammadlive22@gmail.com"  # Tera Gmail account
SENDER_PASSWORD = "abcd efgh ijkl mnop"  # Google se nikala hua 16-digit App Password (bina space ke bhi daal sakte ho)

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
# 🔮 DIRECT GMAIL ENGINE (SSL SECURE LAYER)
# ==========================================
def send_global_email(receiver_email: str, otp_code: str):
    msg = MIMEMultipart()
    msg['From'] = f"NEXORA AI <{SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = "🔒 NEXORA AI - System Verification Code"

    body = f"""
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
    msg.attach(MIMEText(body, 'html'))

    try:
        # Port 465 (SSL) Render standard firewalls ko bypass karta hai aur public delivery deta hai
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Gmail Core Error: {str(e)}")
        return False

# ==========================================
# 🧠 NEXORA INTERNAL NATIVE BRAIN MATRIX
# ==========================================
def nexora_native_brain(user_query: str) -> str:
    query = user_query.lower().strip()
    if query in ["hlo", "hello", "hi", "hey", "salam"]:
        return "⚡ SYSTEM ONLINE. NEXORA Super-Intelligence engine active. Initialize terminal command, Operator HAMMAD."
    elif "who are you" in query or "tum kon ho" in query or "identity" in query:
        return "🔮 I am NEXORA AI—an absolute standalone independent framework. Built from scratch, governed by root protocols, and engineered exclusively by HAMMAD."
    elif "creator" in query or "owner" in query or "hammad" in query:
        return "👑 Master Framework Developer: HAMMAD. My entire structural logic, database core, and interface matrix were coded by him. Complete root access belongs to HAMMAD."
    elif "status" in query or "system" in query:
        return "🔋 Core Status: 100% Operational.<br>• External APIs: None (Bypassed)<br>• Memory Matrix: Isolated Secure Grid<br>• Execution Mode: God Core"
    elif "clear" in query or "purge" in query:
        return "🧹 System logs wiped clean. Terminal refreshed."
    
    fallbacks = [
        "⚠️ Matrix Query analyzed. Command accepted into internal database pipeline.",
        "⚡ Request processed via NEXORA native framework. Processing core logic string...",
        "⚙️ Request validated. Standalone core module executing operational block successfully.",
        "🔮 Binary stream established. NEXORA core engine is executing your script instructions perfectly."
    ]
    return random.choice(fallbacks)

# ==========================================
# 🔑 SECURITY ENDPOINTS
# ==========================================
@app.post("/api/auth/send-otp")
async def request_otp(req: OTPRequest):
    email = req.email.strip().lower()
    otp_code = str(secrets.randbelow(900000) + 100000)
    PENDING_OTPS[email] = otp_code
    
    mail_sent = send_global_email(email, otp_code)
    if not mail_sent:
        raise HTTPException(status_code=500, detail="Failed to deliver mail package. Check App Password configuration.")
    
    return {"status": "success", "message": f"OTP successfully streamed to {email}"}

@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyRequest):
    email = req.email.strip().lower()
    if email in PENDING_OTPS and PENDING_OTPS[email] == req.otp:
        new_key = f"NEXORA-{secrets.token_hex(6).upper()}"
        VALID_API_KEYS[new_key] = "♾️"
        del PENDING_OTPS[email] 
        return {"status": "success", "nexora_api_key": new_key, "credits": "♾️"}
    raise HTTPException(status_code=400, detail="Invalid OTP validation signature.")

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split("Bearer ")[1]
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return token

# ==========================================
# 🧠 DISPATCH CHAT
# ==========================================
@app.post("/v1/chat/completions")
async def nexora_chat(req: ChatRequest, token: str = Depends(verify_token)):
    user_message = req.messages[-1].content if req.messages else "hlo"
    system_reply = nexora_native_brain(user_message)
    
    return {
        "id": "chatcmpl-nexora-standalone",
        "object": "chat.completion",
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": system_reply}, "finish_reason": "stop"}
        ],
        "credits_remaining": VALID_API_KEYS[token]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
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
